import React from "react";
import { Container, Col, Row } from "react-bootstrap";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";

const types = ["溫度", "濕度", "TVOC", "PM2.5", "CO2"];
const amounts = [25, 50.0, 200, 400, 1000];

const Column = ({ type, amount }) => {
  return (
    <Col xs={6}>
      <h1>{type}</h1>
      <p>{amount}</p>
    </Col>
  );
};

const Infomation = () => {
  return (
    <Container>
      <Row>
        {types.map((type, i) => {
          return <Column key={i} type={type} amount={amounts[i]} />;
        })}
      </Row>
    </Container>
  );
};

// 之後要從資料庫抓改成下面
// const Infomation = ({amounts}) => {
//     return (
//       <Container>
//         <Row>
//           {types.map((type, i) => {
//             return <Column key={i} type={type} amount={amounts[i]} />;
//           })}
//         </Row>
//       </Container>
//     );
//   };

export default Infomation;
