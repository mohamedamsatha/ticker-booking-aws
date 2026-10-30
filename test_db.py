from db import get_db_connection

try:
    connection = get_db_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE() AS database_name")
        result = cursor.fetchone()

    print("Database Connected Successfully!")
    print(result)

    connection.close()

except Exception as error:
    print("Database Connection Failed!")
    print(error)
