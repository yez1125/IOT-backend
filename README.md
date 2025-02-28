# AIoT Smart Monitoring System

## Overview

This AIoT Smart Monitoring System collects, visualizes, and analyzes real-time environmental sensor data. The frontend uses React.js and D3.js for dynamic data visualization, while the backend, powered by Flask and MySQL, handles API requests and database management. The system supports PLC communication for industrial integration and is containerized with Docker for scalability and reliability.

## Features

- **Real-time Sensor Data Visualization**: Uses D3.js to display dynamic charts.
- **User Authentication**: Login system for user authentication.
- **Remote API Communication**: Fetches data from a remote AIoT API via Axios.
- **Interactive Dashboard**: Provides an intuitive UI with Bootstrap for better user experience.
- **AI-Powered Insights**: Uses sensor data analytics for decision-making.

## Installation

### Prerequisites

Ensure you have the following installed:

- **Node.js** (v14 or later)
- **npm** or **yarn**

### Steps to Run

1. Clone the repository:
   ```sh
   git clone https://github.com/dcde22345/aiot-monitoring.git
   cd aiot-monitoring
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm start
   ```
   The application will be available at `http://localhost:3000/`.

## Technologies Used

- **React.js**: Frontend framework.
- **D3.js**: Real-time data visualization.
- **Bootstrap**: Responsive UI components.
- **Axios**: API communication.
- **Flask**: Backend API framework.
- **SQLAlchemy**: Database ORM.
- **MySQL**: Relational database for sensor data storage.
- **Ngrok**: Secure API tunneling.
- **PLC (Programmable Logic Controller)**: Hardware integration.
- **Pymodbus**: PLC communication.
- **Docker**: Containerization for deployment.

## API Communication

The system fetches real-time sensor data from a remote AIoT API using `fetchApi.js`. The backend provides the following API endpoints:

### Endpoints

#### `/api/get_instant_data` - Fetch the latest environmental data

```json
{
    "temperature": 25.4,
    "humidity": 55.1,
    "tvoc": 120,
    "co2": 450,
    "pm25": 35
}
```

#### `/api/toggle_status` - Toggle the ABox power state

#### `/api/get_status` - Retrieve the current ABox status

### PLC Communication

The backend integrates with a **PLC (Programmable Logic Controller)** for industrial automation. Data is fetched and stored in MySQL using the `app.py` script, which:

- Establishes a database connection.
- Connects to the PLC via **Pymodbus**.
- Reads sensor values from the PLC.
- Updates database records based on PLC status changes.
- Sends control commands to the PLC if database status changes.

### Docker Deployment

This system is containerized using Docker for streamlined deployment. To build and run the Docker container:

```sh
docker build -t aiot-monitoring .
docker run -d -p 3002:3002 aiot-monitoring
```

The backend and PLC integration run inside a containerized environment, ensuring portability and reliability.

### Example API Usage

```js
import { fetchGetApi } from './fetchApi';
fetchGetApi('/api/get_instant_data').then(response => console.log(response.data));
```

The backend is implemented using Flask and SQLAlchemy, handling real-time data processing and sensor status updates.

## Contribution

Contributions are welcome! Feel free to submit a pull request or open an issue.
