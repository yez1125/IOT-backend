import { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import axios from "axios";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import fetchApi from "./fetchApi";
import "./styles/ABoxSwitch.css";

const ABoxSwitch = ({ address }) => {
  const elementRef = useRef(null);
  const [isDisabled, setDisable] = useState(false);

  // 判斷status與btn的狀態是否一致
  const change_btn_status = (status) => {
    if (elementRef.current) {
      const element = elementRef.current;
      const isContainRotateClass = element.classList.contains(
        "circle-button-rotated"
      );

      // status: false -> true
      // 如果status為true並且classList裡沒有 "circle-button-rotated"，則加入
      if (status && !isContainRotateClass) {
        element.classList.add("circle-button-rotated");
      }

      // status: true -> false
      // 如果status為false並且classList裡有 "circle-button-rotated"，則移除
      if (!status && isContainRotateClass) {
        element.classList.remove("circle-button-rotated");
      }
    }
  };

  const handleBtnClick = async () => {
    setDisable(true);

    // 執行toggle_status
    await fetchApi("/api/toggle_status");

    // 讀取目前最新一筆record的status
    const res = await fetchApi("/api/get_status");
    const status = res.data.status;

    change_btn_status(status);

    setTimeout(() => {
      setDisable(false);
    }, 500);
  };


  // 當網頁第一次渲染過後，執行一次
  useEffect(() => {
    const fetchData = async () => {
      const res = await fetchApi("/api/get_status");
      const status = res.data.status;
      change_btn_status(status);
    };
    fetchData();
  }, []);

  return (
    <div className="w-75 relative">
      <Button
        ref={elementRef}
        onClick={handleBtnClick}
        className="p-0 d-flex justify-content-center align-items-start circle-button w-100"
        disabled={isDisabled}
      >
        <div className="line"></div>
      </Button>
      <span className="open">ON</span>
      <span className="close">OFF</span>
    </div>
  );
};

export default ABoxSwitch;
