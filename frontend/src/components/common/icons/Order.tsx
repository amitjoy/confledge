import {SVGProps} from "react"

export const Order = (props: SVGProps<SVGSVGElement>) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round"
         className="lucide lucide-sliders-horizontal css-r9wktm" {...props}>
        <line x1="21" x2="14" y1="4" y2="4"></line>
        <line x1="10" x2="3" y1="4" y2="4"></line>
        <line x1="21" x2="12" y1="12" y2="12"></line>
        <line x1="8" x2="3" y1="12" y2="12"></line>
        <line x1="21" x2="16" y1="20" y2="20"></line>
        <line x1="12" x2="3" y1="20" y2="20"></line>
        <line x1="14" x2="14" y1="2" y2="6"></line>
        <line x1="8" x2="8" y1="10" y2="14"></line>
        <line x1="16" x2="16" y1="18" y2="22"></line>
    </svg>
);


export default Order