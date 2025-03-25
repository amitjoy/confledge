/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Lato', 'Roboto', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Helvetica', 'Arial', 'sans-serif', '"Apple Color Emoji"', '"Segoe UI Emoji"', '"Segoe UI Symbol"'],
            },
            width: {
                'custom-sm': '15em',
                'custom-md': '20em',
                'custom-lg': '30em',
            },
            spacing: {
                '0.5': '2px',
                '1.5': '8px',
                '3': '12px',
            },
            lineHeight: {
                'custom': '20px'
            },
            fontSize: {
                'small': '12px',
                'custom': '14px'
            },
            fontWeight: {
                medium: 500,
            },
            colors: {
                magenta: {
                    /*    100: '#ffccff',
                       200: '#ff99ff',
                       300: '#ff66ff',
                       400: '#ff33ff',
                       500: '#e2007e', */

                    100: '#6e56cf',
                    200: "#6B21A8",
                    500: "#6e56cf",
                },
                mauve: {
                    100: "#121113",
                    200: "#1a191b",
                    300: "#232225",
                    400: "#3B3C56",
                    600: "#ece9fd7c",
                    700: "#626280",
                    800: "#73748E",
                    900: '#2b292d',
                    1100: "#A5A6B3",
                    1200: "#CBCBD3",
                },
                purple: {
                    100: '#6e56cf',
                    500: "#7C3AED",
                    600: "#6B21A8",
                },
                accent: {
                    100: '#8354fe36',
                    200: '#baa7ff',
                    300: '#6550b9',
                    400: "#6D28D9",
                    800: '#33255b',
                    900: '#baa7ff',
                    1200: "#D8B4FE",
                },
            },
            backgroundColor: {
                'white-alpha-16': 'rgba(255, 255, 255, 0.16)'
            },
            textColor: {
                'white-alpha-16': 'rgba(255, 255, 255, 0.16)'
            },
            borderColor: {
                'white-alpha-16': 'rgba(255, 255, 255, 0.16)'
            }
        },
    },
    plugins: [],
};
