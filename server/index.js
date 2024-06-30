const express = require('express')
const mysql = require('mysql2')
const cors = require('cors')

const app = express()
const port = 3001

app.use(cors())

//資料庫
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'root',
    database: 'plc'
})

db.connect(err=>{
    if(err){
        console.error('Error: ', err)
        return
    }
    console.log('已連接到資料庫')
})

app.get('/api/1min-data', (req, res) => {
    const query = 'SELECT temperature, humidity, time FROM data ORDER BY time DESC LIMIT 60'

    db.query(query, (err, result) => {
        if(err){
            console.error("Error: ", err)
            return
        }

        res.json(result)
    })
})


app.listen(port, () => {
    console.log(`Server已在http://localhost:${port}啟動`)
})