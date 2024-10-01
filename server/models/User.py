from ..config.db import get_db_connection

class User:
    def __init__(self, username, email, password_hash, created_at=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    def save(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 做正規化表示
                query = "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)"

                cursor.execute(query, (
                    self.username,
                    self.email,
                    self.password_hash,
                    self.created_at
                ))
            connection.commit()
            return self
        except Exception as e:
            print(f'Error : {e}')
            connection.rollback()
            return None
        finally:
            connection.close()

    @staticmethod
    def find_by_username(username):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = 'SELECT username FROM users WHERE username = %s'
                cursor.execute(query, (username))
                result = cursor.fetchone()
                if result:
                    return User(
                        username=result
                    )
