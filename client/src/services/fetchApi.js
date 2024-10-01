import axios from 'axios'

const hostAddress = 'https://182a-2402-7500-92c-3818-8c46-b926-4e5a-c487.ngrok-free.app'

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