import socket
import threading
import sqlite3
import json


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostbyname(socket.gethostname()), 8036))
server.listen()

db = sqlite3.connect('products.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT, password TEXT,
                    first_name TEXT, middle_name TEXT,
                    last_name TEXT, username TEXT UNIQUE,
                    creationdate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    address TEXT, owner_online INTEGER DEFAULT 0)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS products(
               product_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INT, product_name TEXT, 
               price REAL,description TEXT, category TEXT, 
               published_at DATETIME, image_url TEXT)""")
db.commit()

def register(conn):
    data = conn.recv(1024).decode('utf-8')
    details = data.split('|')
    if len(details) != 7:
        conn.send("Invalid registration data".encode('utf-8'))
        return
    email, password, first_name, middle_name, last_name, username, address = details
    try:
        cursor.execute("""INSERT INTO users(email, password, first_name, middle_name, last_name, username, address)
                          VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (email, password, first_name, middle_name, last_name, username, address,1))
        db.commit()
        user_i = cursor.lastrowid
        user_id=str(user_i)
        conn.send(f"Registration successful|{user_id}".encode('utf-8'))
    except sqlite3.IntegrityError:
        conn.send("Username already taken".encode('utf-8'))

def log_in(conn):
    data = conn.recv(1024).decode('utf-8')
    credentials = data.split('|')
    if len(credentials) != 2:
        conn.send("Invalid login data".encode('utf-8'))
        return
    username, password = credentials

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        user_id = user[0]
        user_i=str(user_id)
        cursor.execute("UPDATE users SET owner_online = 1 WHERE user_id = ?", (user_id,))
        db.commit()
        conn.send(f"Log in successful|{user_i}".encode('utf-8'))
    else:
        conn.send("Invalid login credentials".encode('utf-8'))

def add_product(conn):
    datae=conn.recv(1024)
    data=json.loads(datae.decode('utf-8'))
    infos=data.split('|')
    user_id,productnm,desc,price,image,category=infos
    cursor.execute(
        "INSERT INTO users (user_id INT, product_name TEXT, price REAL,description TEXT, category TEXT, published_at DATETIME, image_url TEXT, owner_online INT) VALUES (?, ?, ?, ?, ?, DATETIME('now'),?)", 
        (user_id, productnm, price, desc, category, image)
    )
    print("Products in the database:")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(user)

def viewprod(conn):
    cursor.execute("SELECT product_name, price ,description, image_url FROM products")
    rows = cursor.fetchall()
    columns = ["column1", "column2"]
    data = [dict(zip(columns, row)) for row in rows]
    jason= json.dumps(data)
    conn.sendall(jason.encode('utf-8'))
    print("Data sent to client.")

def handle_client(conn, addr):
    try:
        request = conn.recv(1024).decode('utf-8')
        if request == "register":
            register(conn)
        elif request == "log in":
            log_in(conn)
        else:
            conn.send("Invalid request".encode('utf-8'))
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Server is running and listening for connections...")
    while True:
        conn, addr = server.accept()
        print(f"Connected to {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()


#Jad Eido
def add_product(conn, cursor, db):
    product_name = conn.recv(1024).decode('utf-8')
    description = conn.recv(1024).decode('utf-8')
    price = float(conn.recv(1024).decode('utf-8'))
    category = conn.recv(1024).decode('utf-8')
    image_url = conn.recv(1024).decode('utf-8')
    
    product_id = random.randint(1000, 9999)
    owner_id = 1234  # This should be the logged-in user's ID
    cursor.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'), ?, 1)", 
                   (product_id, owner_id, product_name, price, description, category, image_url))
    db.commit()
    conn.send("Product added successfully.".encode('utf-8'))
#Jad Eido
def view_products(conn, cursor):
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    product_list = "\n".join([f"{p[0]}: {p[2]}, ${p[3]}, {p[4]}" for p in products])
    conn.send(product_list.encode('utf-8'))


