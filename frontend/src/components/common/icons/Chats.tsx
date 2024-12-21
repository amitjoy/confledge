import {SVGProps} from "react"

const Chats = (props: SVGProps<SVGSVGElement>) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-messages-square css-r9wktm" {...props}>
        <path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4c0-1.1.9-2 2-2h8a2 2 0 0 1 2 2v5Z"></path>
        <path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1">
        </path>
    </svg>
);

export default Chats