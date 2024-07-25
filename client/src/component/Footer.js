import React from "react";
import { Container, Navbar, Nav } from "react-bootstrap";
import axios from 'axios'
import fetchApi from "./fetchApi"
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";

const Footer = () => {

  const handleHistoryClick = () => {
    const res = fetchApi('/api/add_new')
    console.log(res)
  }
  return (
    <div className="fixed-bottom">
      <Nav variant="underline justify-content-around" defaultActiveKey="/home">
        <Nav.Item>
          <Nav.Link eventKey="link-2" className='p-1'>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              fill="currentColor"
              class="bi bi-person-circle"
              viewBox="0 0 16 16"
            >
              <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0" />
              <path
                fill-rule="evenodd"
                d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1"
              />
            </svg>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="link-1">監控</Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="link-3">歷史紀錄</Nav.Link>
        </Nav.Item>
      </Nav>
    </div>
  );
};

export default Footer;
