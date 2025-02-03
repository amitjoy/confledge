from agent.history.sql import HistoryMessageModel

HistoryMessageModel._meta.database.create_tables([HistoryMessageModel])
