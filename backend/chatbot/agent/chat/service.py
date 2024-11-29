import logging
from kink import di
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.globals import set_debug, set_verbose
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableWithMessageHistory

from agent.history.service import HistoryAgent
from agent.knowledge_base.service import KnowledgeBaseAgent
from agent.llm.service import ChatVertexLLM
from config.app import Settings

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    ChatAgent class handles the initialization and management of chat sessions
    with integrated history and knowledge base retrieval.
    """

    def __init__(self, kb_agent: KnowledgeBaseAgent, history_agent: HistoryAgent):
        """
        Initializes the ChatAgent with the given knowledge base and history agents.

        :param kb_agent: An instance of KnowledgeBaseAgent for retrieving knowledge base data.
        :param history_agent: An instance of HistoryAgent for managing chat history.
        """
        self.settings: Settings = di[Settings]
        self.vertex: ChatVertexLLM = di[ChatVertexLLM]
        self.kb_agent = kb_agent
        self.history_agent = history_agent
        self.prompt = self._initialize_prompt(di['template'])
        self.condense_prompt = self._initialize_condense_prompt(di['condense_template'])
        self._memory = self._initialize_memory()

        set_debug(self.settings.gcp.vertex.model.debug)
        set_verbose(self.settings.gcp.vertex.model.verbose)

    def _initialize_prompt(self, template: str) -> ChatPromptTemplate:
        """
        Initializes the main prompt template for the chat agent.

        :param template: Template string for the prompt.
        :return: A ChatPromptTemplate instance.
        """
        return ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

    def _initialize_condense_prompt(self, template: str) -> ChatPromptTemplate:
        """
        Initializes the condense prompt template for the chat agent.

        :param template: Template string for the condense prompt.
        :return: A ChatPromptTemplate instance.
        """
        return ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

    def _initialize_memory(self) -> ConversationBufferMemory:
        """
        Initializes the conversation buffer memory for the chat agent.

        :return: A ConversationBufferMemory instance.
        """
        return ConversationBufferMemory(
            input_key="question",
            output_key="answer",
            return_messages=True,
            chat_memory=self.history_agent.memory,
            max_token_limit=self.settings.gcp.vertex.chat_memory.max_token_limit
        )

    @property
    def memory(self) -> BaseChatMemory:
        """
        Returns the conversation memory.

        :return: An instance of BaseChatMemory.
        """
        return self._memory

    @property
    def chain(self) -> Runnable:
        """
        Constructs the retrieval chain for the chat agent.

        :return: A Runnable instance representing the retrieval chain.
        """
        logger.debug("Initializing retrieval from knowledge base chain")

        history_aware_retriever = create_history_aware_retriever(
            llm=self.vertex.model,
            retriever=self.kb_agent.retriever,
            prompt=self.condense_prompt
        )
        document_chain = create_stuff_documents_chain(
            llm=self.vertex.model,
            prompt=self.prompt
        )
        retrieval_chain = create_retrieval_chain(
            retriever=history_aware_retriever,
            combine_docs_chain=document_chain
        )

        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            return self.history_agent.message_history

        return RunnableWithMessageHistory(
            retrieval_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )
