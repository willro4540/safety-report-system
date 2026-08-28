import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    raise Exception("DB 미연결 — 로컬 모드로 동작")

'''def get_connection():
    return pymysql.connect(
        host = os.getenv("DB_HOST", "localhost"),
        user = os.getenv("DB_USER", "root"),
        password = os.getenv("DB_PASSWORD", ""),
        database = os.getenv("DB_NAME", "safety_report"),
        charset = "utf8mb4"
    )'''
