import {Button} from "react-bootstrap"

const CustomButton = ({text}) => {
    return (
        <Button variant="primary" type="submit" className="w-100 bg-dark">
              {text}
        </Button>
    ) 
}

export default CustomButton