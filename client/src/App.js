import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./styles/App.css";
import React, { useState } from "react";

import { BrowserRouter } from 'react-router-dom';
import { Header } from "./component/components";
import Routers from "./routes/Routers";

const App = () => {
  const [data, setData] = useState([]);

  return (
    <BrowserRouter>
      <Header />
      <Routers />
    </BrowserRouter>
  );
};

export default App;
