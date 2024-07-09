from flask import Flask, render_template, request, redirect, url_for
import oracledb
from datetime import datetime
# from pymongo import MongoClient
from faker import Faker
 
app = Flask(__name__)
 
def get_db_connection():
    # Update these values with your actual database credentials
    # dsn = 'localhost:1521/xepdb1'
    # conn = oracledb.connect(user="dbuser", password="dbuser", dsn=dsn)

    # connect to rds instance
    dsn = "dbinsone.cj2624y4ut6p.eu-north-1.rds.amazonaws.com:1521/ORCL"
    conn = oracledb.connect(user="admin",password="ordbuser",dsn=dsn)
    
    return conn

def add_random_name_to_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor = connection.cursor()    
    add_column_query = "ALTER TABLE customer_details ADD COLUMN name VARCHAR(255)"
    cursor.execute(add_column_query)
    connection.commit()
    cursor.execute("SELECT * FROM customer_details")
    rows = cursor.fetchall()
    length=len(rows)
    print(length)
    for row in range(1,37084):
        fake_name = Faker.name()  # Generate a new fake name each iteration
        query = f"UPDATE customer_details SET name = '{fake_name}' WHERE Customer_id = {row}"
        cursor.execute(query)
        connection.commit() 
    connection.commit()
    cursor.close()
    connection.close()
    print ("Names added to all rows successfully")
    


 
 
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT table_name FROM user_tables")
 
    tables = [row[0] for row in cursor.fetchall( )]
    cursor.close()
    conn.close()
    return render_template('base.html', tables = tables)



# @app.route('/customerid-list')
# def cuslist():
#     print('hello world')
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT customer_id from customer_details order by customer_id")

#     customer_ids = [row[0] for row in cursor.fetchall()]

#     cursor.close()
#     conn.close()

#     return render_template('input.html', idlist = customer_ids)







   
@app.route('/table')
def view_table():

    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = request.args.get('table')
    # cursor.execute("SELECT table_name FROM user_tables")
    
    page = request.args.get('page',1,type=int)
    per_page = 15

    # query = f"SELECT * FROM {table_name}"
 
    # cursor.execute(query)
    # rows = cursor.fetchall()
    # columns = [desc[0] for desc in cursor.description]

    # cursor.close()
    # conn.close()
    # return render_template('tinfo.html', column_names= columns, rows=rows,table_name=table_name)

    query_count = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query_count)
    total_count = cursor.fetchone()[0]
    total_pages = (total_count // per_page) + (1 if total_count % per_page > 0 else 0)
    
    offset = (page - 1) * per_page
    limit = per_page

    
    cursor.execute(f"SELECT * FROM {table_name} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    return render_template('tinfo.html', column_names=columns, rows=rows, table_name=table_name, page=page, total_pages=total_pages)





 



@app.route('/edit/<table_name>/<string:row_id>', methods=['GET', 'POST'])
def edit_row(table_name, row_id):
    if request.method == 'POST':
        # Process form submission and update row in the database
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        update_query = f"UPDATE {table_name} SET "
        update_params = []
        for key, value in request.form.items():
            if key != 'submit':
                column_name = key
                update_query += f"{column_name} = :{column_name}, "
                update_params.append(value)
        update_query = update_query.rstrip(', ') + f" WHERE {columns[0]} = '{row_id}'"
        '''print(update_query)
        print(update_params)'''
        cursor.execute(update_query, update_params)
        connection.commit()
        cursor.close()
       
        return('/')
   
    # Fetch row data for editing
    connection = get_db_connection()
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    index_row=columns[0]
    cursor.close()  
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE {index_row} = :row_id", {'row_id': row_id})
    row = cursor.fetchone()
    cursor.close()
    row=list(row)
    dic=dict(zip(columns,row))
    return render_template('edittable.html', table_name=table_name, dic=dic) 





@app.route('/details', methods=['POST'])
def search():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        customer_id = request.form.get('customer_id')
        table = 'customer_details'
        row_id = 'customer_id'  # Adjust this to match your actual primary key column name
        
        cursor.execute(f"SELECT * FROM {table} WHERE {row_id} = :row_id", {'row_id': customer_id})
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            dic = dict(zip(columns, row))
            print(dic)
            return render_template('display.html', columns_rows=dic)
        else:
            return "No customer found with that ID."

    except Exception as e:
        return f"Error retrieving customer details: {str(e)}", 500
    
    finally:
        cursor.close()
        conn.close()





@app.route('/delete/<table_name>/<string:row_id>', methods=['POST'])
def delete_row(table_name, row_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        
        delete_query = f"DELETE FROM {table_name} WHERE EMPLOYEE_ID = :row_id"
        cursor.execute(delete_query, {'row_id': row_id})
        connection.commit()
    except Exception as e:
        connection.rollback()
        return f"Error deleting record: {str(e)}", 500
    finally:
        cursor.close()
        connection.close()

    # go back to the tabvle view
    return redirect(url_for('view_table', table=table_name))

 
if __name__ == '__main__':
    app.run(debug=True)
    add_random_name_to_table()
