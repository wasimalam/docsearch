import mysql.connector
import bcrypt
from passlib.context import CryptContext

from app.config import read_config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

configs = read_config()
# Define the database connection
def get_db_connection():
    return mysql.connector.connect(
        host= configs.db.host,
        user=configs.db.user,
        password=configs.db.password,
        database=configs.db.dbname
    )
# Authenticate user and generate token
def authenticate_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, password_hash, role FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and pwd_context.verify(password, user["password_hash"]):
        return user
    return None