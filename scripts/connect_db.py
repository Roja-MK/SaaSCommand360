
import psycopg2
from getpass import getpass

try:
    print("Connecting to SaaSCommand360 PostgreSQL database...")

    password = getpass("Enter your PostgreSQL password: ")

    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="saascommand360",
        user="postgres",
        password=password
    )

    print("Successfully connected to PostgreSQL!")

    cursor = connection.cursor()
    cursor.execute("SELECT version();")

    version = cursor.fetchone()
    print("\nPostgreSQL Version:")
    print(version[0])

    cursor.close()
    connection.close()

    print("\nDatabase connection closed.")

except Exception as error:
    print("Database connection failed!")
    print(error)
