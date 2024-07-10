from faker import Faker
import oracledb
# Initialize Faker
faker = Faker()

def get_db_connection():
    
    # connect to rds instance
    dsn = "dbinsone.cj2624y4ut6p.eu-north-1.rds.amazonaws.com:1521/ORCL"
    conn = oracledb.connect(user="admin",password="ordbuser",dsn=dsn)
   
    return conn
 
 
 
def add_random_name_to_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM customer_details")
    rows = cursor.fetchall()
    length=len(rows)
    print(length)
    for row in range(1,37084):
        fake_name = faker.name()  # Generate a new fake name each iteration
        query = f"UPDATE customer_details SET name = '{fake_name}' WHERE Customer_id = {row}"
        cursor.execute(query)
        connection.commit()
    connection.commit()
    cursor.close()
    connection.close()
    print ("Names added to all rows successfully")
   
 
if __name__ == '__main__':
    add_random_name_to_table()