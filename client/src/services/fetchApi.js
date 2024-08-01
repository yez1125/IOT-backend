import axios from 'axios'

const hostAddress = 'http://localhost:3002'

const fetchGetApi = async (api_address) => {
    try {
        return await axios.get(hostAddress + api_address);
    } catch (error) {
        console.error("Error: ", error);
    }
}

const fetchPostApi = async (api_address) => {
    try {
        return await axios.post(hostAddress + api_address);
    } catch (error) {
        console.error("Error: ", error);
    }
}

export {fetchGetApi, fetchPostApi}