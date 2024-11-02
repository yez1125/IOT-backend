from ..config.db import get_db_connection

class Data():
    def __init__(self, sensor_id, temperature, humidity, pm25, pm10, pm25_average_in_one_hour, pm10_average_in_one_hour, tvoc, co2):
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.humidity = humidity
        self.pm25 = pm25
        self.pm10 = pm10
        self.pm25_average_in_one_hour = pm25_average_in_one_hour
        self.pm10_average_in_one_hour = pm10_average_in_one_hour
        self.tvoc = tvoc
        self.co2 = co2

    def save(self):
        connection = get_db_connection()
        try:
                with connection.cursor() as cursor:
                    query = "INSERT INTO data (sensor_id, temperature, humidity, pm25, pm10, pm25_average_in_one_hour, pm10_average_in_one_hour, tvoc, co2) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    
                    cursor.execute(query, (
                        self.sensor_id,
                        self.temperature,
                        self.humidity,
                        self.pm25,
                        self.pm10,
                        self.pm25_average_in_one_hour,
                        self.pm10_average_in_one_hour,
                        self.tvoc,
                        self.co2
                    ))
                
                connection.commit()
                return self
        except Exception as e:
             print(f'Error: {e}')
             connection.rollback()
             return None
        finally:
             connection.close()