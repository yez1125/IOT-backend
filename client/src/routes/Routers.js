import Home from "../pages/Home"
import Test from "../pages/Test"
import Login from "../pages/Login"
import {Routes, Route, Navigate} from "react-router-dom"

const Routers = () => {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/login"/>} />
            <Route path="/login" element={<Login />} />
            <Route path="/home" element={<Home />} />
            <Route path="/test" element={<Test />} />
        </Routes>
    )
}

export default Routers