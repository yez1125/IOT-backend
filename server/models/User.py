from ..config.db import get_db_connection
import bcrypt

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        # 對密碼進行hash
        # decode後為字串較方便存入資料庫
        self.password_hash = bcrypt.hashpw(password.encode('utf-8', bcrypt.gensalt()).decode("utf-8"))



    def save(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 做正規化表示
                query = "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)"

                cursor.execute(query, (
                    self.username,
                    self.email,
                    self.password_hash
                ))
            connection.commit()
            return self
        except Exception as e:
            print(f'Error : {e}')
            connection.rollback()
            return None
        finally:
            connection.close()

    # static代表即便沒有建立User()，也可以call User.login()
    @staticmethod
    def login(username, password):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 找出對應username的user
                query = 'SELECT username, password_hash FROM users WHERE username = %s'
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                # 如果有結果
                if result:
                    # 檢查密碼是否正確
                    if bcrypt.checkpw(password.encode("utf-8"), result['password_hash'].encode("utf-8")):
                        # 回傳這個User的資料，並以json的形式送到前端
                        return {
                            "username": result['username'],
                            "email": result['email'],
                        }
                    else:
                        # 密碼錯誤
                        print("密碼不正確")
                        return None
                else:
                    # 沒有結果
                    print("沒有這個使用者")
                    return None

        except Exception as e:
            print(f'Error: {e}')
            return None
        finally:
            connection.close()                
    
    # 忘記密碼
    # 使用者建立與登入時寄Email