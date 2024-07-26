import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./App.css"

import axios from "axios";
import React, { useState, useEffect } from "react";
import { Container, Row, Col, Button, Navbar, Nav } from "react-bootstrap";
import {NavbarComponent, TemperatureChart, HumidityChart, Infomation, ABoxSwitch, Footer} from './component/components';

// ------測試用-------
import fetchApi from './component/fetchApi'
// ------------------
const App = () => {
  const [data, setData] = useState([]);


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
          <Footer />
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
        <Button onClick={() => {}}>測試按鈕</Button>
        </Container>
      </div>
    </>
  );
};

export default App;
