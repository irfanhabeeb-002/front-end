import psycopg2
try:
    conn = psycopg2.connect("dbname=proxihealth user=postgres password=irfan host=localhost port=5432")
    print("Connected successfully!")
except Exception as e:
    print(f"Failed to connect: {e}")

DATABASE_URL = "postgresql://postgres:irfan@localhost/proxihealth"
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:irfan@localhost:5432/proxihealth'


