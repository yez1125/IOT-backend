import {useEffect, useState} from "react";
import { Container, Col, Row } from "react-bootstrap";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import {fetchGetApi} from './components'

const types = ["溫度", "濕度", "TVOC", "PM2.5", "CO₂"];
const units = ["℃", "%", "ppm", "μg/m³", "ppm"];

const Column = ({ type, amount, unit }) => {
  if (type === "PM2.5") {
    return (
      <Col xs={6}>
        <h1>PM<sub className='fs-6 fw-bold'>2.5</sub></h1>
        <p>{amount + " " + unit}</p>
      </Col>
    );
  }

  return (
    <Col xs={6}>
      <h1>{type}</h1>
      <p>{amount + " " + unit}</p>
    </Col>
  );
};

const Infomation = () => {
  const [amounts, setAmounts] = useState([])

  const get_instant_data = async () => {
    const res = await fetchGetApi('/api/get_instant_data')
    const data = res.data
    setAmounts([data.temperature, data.humidity, data.tvoc, data.pm25, data.co2])
    
  }
  
  useEffect(() => {
    const interval = setInterval(get_instant_data, 1000)
    return () => clearInterval(interval)
  }, []);

  return (
    <Container>
      <Row>
        {types.map((type, i) => {
          return (
            <Column key={i} type={type} amount={amounts[i]} unit={units[i]} />
          );
        })}
      </Row>
    </Container>
  );
};

export default Infomation;
