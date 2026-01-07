# import requests

# r = requests.get("https://api-inference.huggingface.co")
# print(r.status_code)



import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("Connecting to:", os.getenv("DATABASE_URL"))

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
print("Connected successfully!")
conn.close()
