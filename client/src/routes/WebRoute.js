import WebView from "../pages/WebView"
import {Routes, Route} from "react-router-dom"

const WebRoute = () => {
    return (
        <Routes>
            <Route path="/" element={<WebView />} />
        </Routes>
    )
}

export default WebRoute