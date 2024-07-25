import { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import axios from 'axios'
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./styles/ABoxSwitch.css";
import fetchApi from "./fetchApi"

const ABoxSwitch = ({address}) => {
  const elementRef = useRef(null);

  const handleBtnClick = async () => {
    // 後續邏輯要改成看目前status
    
    const res = await fetchApi('/api/toggle_status')
    let status = res.data.status
    console.log(status)
    if (elementRef.current) {
      const element = elementRef.current;
      if(status && (!element.classList.contains("circle-button-rotated"))){
        element.classList.add("circle-button-rotated");
      }else if((!status) && element.classList.contains("circle-button-rotated")){
        element.classList.remove("circle-button-rotated");
      }
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetchApi('/api/get_status')
      let status = res.data.status
      if (elementRef.current) {
        const element = elementRef.current;
        if(status && (!element.classList.contains("circle-button-rotated"))){
          element.classList.add("circle-button-rotated");
        }else if((!status) && element.classList.contains("circle-button-rotated")){
          element.classList.remove("circle-button-rotated");
        }
      }
    }
    fetchData()
  }, [])

  return (
    <div className='w-75 relative'>
      <Button
        ref={elementRef}
        onClick={handleBtnClick}
        className="p-0 d-flex justify-content-center align-items-start circle-button w-100"
      >
        <div className="line"></div>
      </Button>
        <span className="open">ON</span>
        <span className="close">OFF</span>
    </div>
  );
};

export default ABoxSwitch;
