import Home from "../pages/Home"
import Test from "../pages/Test"
import {Routes, Route} from "react-router-dom"

const MoblieRoutes = () => {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/test" element={<Test />} />
        </Routes>
    )
}

export default MoblieRoutes