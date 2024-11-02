from ..config.db import get_db_connection

class Abox:
    def __init__(self, plc_id, plc_output, abox_status):
        self.plc_id = plc_id
        self.plc_output = plc_output
        self.abox_status = abox_status

    def save(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 做正規化表示
                query = "INSERT INTO abox (plc_id, plc_output, abox_status) VALUES (%s, %s, %s)"

                cursor.execute(query, (
                    self.plc_id,
                    self.plc_output,
                    self.abox_status
                ))
            connection.commit()
            return self
        except Exception as e:
            print(f'Error : {e}')
            connection.rollback()
            return None
        finally:
            connection.close()