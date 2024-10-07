import { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import "../../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import {fetchGetApi} from "../components";
import "./ABoxSwitch.css";

const ABoxSwitch = ({ address }) => {
  const elementRef = useRef(null);
  const [isDisabled, setDisable] = useState(false);

  // 判斷DB中的status與btn的status是否一致
  const change_btn_status = (dbStatus) => {

    // 如果Ref目前有掛到元素
    if (elementRef.current) {
      const element = elementRef.current;

      // 取得目前status
      // 如果circle-button-rotated則代表開啟狀態
      const btnStatus = element.classList.contains(
        "circle-button-rotated"
      );

      // 如果dbStatus與btnStatus都為false，則加入"circle-button-rotated" class
      if (dbStatus && btnStatus) {
        element.classList.add("circle-button-rotated");
      }

      // 如果dbStatus與btnStatus都為True，則移除"circle-button-rotated" class
      if (!dbStatus && btnStatus) {
        element.classList.remove("circle-button-rotated");
      }

      // 如果dbStatus與btnStatus一者為True一者為False，則以btnStatus為準，
    }
  };

  const handleBtnClick = async () => {
    setDisable(true);

    // 執行toggle_status
    await fetchGetApi("/api/toggle_status");

    // 讀取目前最新一筆record的status
    const res = await fetchGetApi("/api/get_status");
    const status = res.data.status;

    change_btn_status(status);

    setTimeout(() => {
      setDisable(false);
    }, 500);
  };


  // 當網頁第一次渲染過後，執行一次
<<<<<<< HEAD
  // useEffect(() => {
  //   const fetchData = async () => {
  //     const res = await fetchGetApi("/api/get_status");
  //     const status = res.data.status;
  //     change_btn_status(status);
  //   };
  //   fetchData();
  // }, []);
=======
  useEffect(async () => {
    const res = await fetchGetApi("/api/get_status");
    const dbStatus = res.data.status;
    change_btn_status(dbStatus);
  }, []);
>>>>>>> 3f5f078f2744497b913b9e2306e6fc5883c530b4

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
