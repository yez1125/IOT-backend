import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./App.css"

import axios from "axios";
import React, { useState, useEffect } from "react";
import { Container, Row, Col, Button, Navbar, Nav } from "react-bootstrap";
import {NavbarComponent, TemperatureChart, HumidityChart, Infomation, ABoxSwitch} from './component/components';

const App = () => {
  const [data, setData] = useState([]);
  const address = "//18.182.5.142:3002";

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const res = await axios.get(address + "/api/1min_data");

  //       res.data.forEach((item) => (item.time = new Date(item.time)));
  //       setData(res.data);
  //     } catch (error) {
  //       console.error("Error: ", error);
  //     }
  //   };
  //   fetchData();
  //   const interval = setInterval(fetchData, 1000);
  //   return () => clearInterval(interval);
  // }, []);

  return (
    <>
      <NavbarComponent />
      <div className="App d-flex justify-content-center align-items-center">
        <Container>
          <Container className='wrap d-flex justify-content-center align-items-center w-100'>
            <ABoxSwitch />
          </Container>
          <Infomation />

          {/* <Row className='mt-5'>
          <Col xs='12' sm='6'>
            <h2 className='m-3 text-center display-6 fw-bold'>溫度</h2>
            <TemperatureChart data={data} />
          </Col>
          <Col xs='12' sm='6'>
            <h2 className='m-3 text-center display-6 fw-bold'>濕度</h2>
            <HumidityChart data={data} />
          </Col>
        </Row> */}
        </Container>
      </div>
    </>
  );
};

export default App;
