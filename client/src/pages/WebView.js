import Home from "./Home"
import Test from "./Test"
import "../../node_modules/bootstrap/dist/css/bootstrap.css"


const WebView = () => {
    return (
        <div className="d-flex justify-content-center">
            <Home />
            <Test />
        </div>
    )
}

export default WebView