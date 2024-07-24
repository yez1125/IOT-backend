import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/App.css'

import  {handleBtnClick, handleToggleClick}  from './Handlers';

import axios from "axios";
import TemperatureChart from "./component/TemperatureChart";
import HumidityChart from "./component/HumidityChart";
import React, { useState, useEffect } from "react";
import { Container, Row, Col, Button } from "react-bootstrap";

const App = () => {
  const [data, setData] = useState([]);
  const address = '//18.182.5.142:3002'

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
    <div className="App d-flex justify-content-center align-items-center">
      <Container>
        <h1 className='text-center p-3 display-4 fw-bold'>Sensor Monitor</h1>
        <Button id='contral-btn' onClick={() => handleBtnClick(address)}>近一分鐘Data</Button>
        <Button id='contral-btn' onClick={() => handleToggleClick(address)}>Toggle</Button>

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
  );
};

export default App;
