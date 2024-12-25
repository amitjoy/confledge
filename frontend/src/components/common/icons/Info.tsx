import {SVGProps} from "react"

const Info = (props: SVGProps<SVGSVGElement>) => (

    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-info css-svt5ra"
         data-state="closed" {...props}>
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 16v-4"></path>
        <path d="M12 8h.01"></path>
        info
    </svg>
)

export default Info