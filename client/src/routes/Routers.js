import MoblieRoutes from "./MobileRoute"
import WebRoute from "./WebRoute"


const Routers = () => {
    console.log(window.innerWidth <= 768)
    return window.innerWidth <= 768 ? <MoblieRoutes /> : <WebRoute />
}



export default Routers