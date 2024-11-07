import { Navbar } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

const Header = () => {
  return (
    <Navbar expand="lg" className="bg-dark justify-content-center">
        <Navbar.Brand href="#home" className="text-white">伸運A-Box</Navbar.Brand>
    </Navbar>
  );
};

export default Header;
