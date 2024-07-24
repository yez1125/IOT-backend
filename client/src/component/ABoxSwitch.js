import {useEffect, useRef, useState} from "react";
import { Button } from "react-bootstrap";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import './styles/ABoxSwitch.css'


const ABoxSwitch = () => {
    const elementRef = useRef(null)
    
    const handleBtnClick = () => {
        // 後續邏輯要改成看目前status
        if(elementRef.current){
            const element = elementRef.current
            if(element.classList.contains('circle-button-rotated')){
                element.classList.remove('circle-button-rotated')
            }else{
                element.classList.add('circle-button-rotated')
            }
        }
    }

    return (
    <Button ref={elementRef} onClick={handleBtnClick} className='p-0 d-flex justify-content-center align-items-start circle-button'>
        <div className='line'></div>
    </Button>
  )
};

export default ABoxSwitch