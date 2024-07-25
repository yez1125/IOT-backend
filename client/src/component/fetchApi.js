import axios from 'axios'

const hostAddress = 'https://f6ba-49-217-61-47.ngrok-free.app'

const fetchApi = async (api_address) => {
    try {
        return await axios.get(hostAddress + api_address);
    } catch (error) {
        console.error("Error: ", error);
    }
}

export default fetchApi