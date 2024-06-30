import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import TemperatureChart from "./component/TemperatureChart";
import HumidityChart from "./component/HumidityChart";
import { Container, Row, Col } from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.min.css'

const App = () => {
  const [data, setData] = useState([]);
  const address = 'https://0bbb-2402-7500-a2c-2f11-9470-83d-53ae-823c.ngrok-free.app'

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(address + "/api/1min-data");

        res.data.forEach((item) => (item.time = new Date(item.time)));
        setData(res.data);
        console.log(res.data);
      } catch (error) {
        console.error("Error: ", error);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App d-flex justify-content-center align-items-center">
      <Container>
        <h1 className='text-center p-3 display-4 fw-bold'>Sensor Monitor</h1>
        <Row className='mt-5'>
          <Col xs='12' lg='6'>
            <h2 className='m-3 text-center display-6 fw-bold'>溫度</h2>
            <TemperatureChart data={data} />
          </Col>
          <Col xs='12' lg='6'>
            <h2 className='m-3 text-center display-6 fw-bold'>濕度</h2>
            <HumidityChart data={data} />
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default App;
