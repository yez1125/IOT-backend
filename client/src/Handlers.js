import axios from "axios"

export const handleBtnClick = async (address) => {
  try{
    console.log(address)
    const res = await axios.get(address + "/api/1min_data")
    console.log(res)
  } catch (error){
    console.error('Error: ' + error)
  }
};

export const handleToggleClick = async (address) => {
  try{
    console.log(address)
    const res = await axios.get(address + '/api/toggle_status')
    console.log(res)
  }catch(error){
    console.error("Error: " + error)
  }
}