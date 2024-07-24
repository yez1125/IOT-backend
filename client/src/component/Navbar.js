import React from "react";
import { Container, Navbar, Nav } from "react-bootstrap";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";

const NavbarComponent = () => {
  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container className='justify-content-center'>
        <Navbar.Brand href="#home">伸運A-Box</Navbar.Brand>
      </Container>
    </Navbar>
  );
};

export default NavbarComponent;
