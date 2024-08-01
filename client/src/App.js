import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./styles/App.css";
import React, { useState } from "react";

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Footer } from "./component/components";
import {Home} from './pages/Pages'

const App = () => {
  const [data, setData] = useState([]);

  return (
    <BrowserRouter>
      <Footer />
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
