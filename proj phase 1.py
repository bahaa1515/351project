import socket
import threading
import sqlite3
import json

socket.setdefaulttimeout(300)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostbyname(socket.gethostname()), 8036))
server.listen()

db = sqlite3.connect('products.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE, password TEXT,
                    first_name TEXT, middle_name TEXT,
                    last_name TEXT, username TEXT UNIQUE,
                    creationdate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    address TEXT, owner_online INTEGER DEFAULT 0)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS products(
               product_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INT, product_name TEXT, 
               price REAL,description TEXT, category TEXT, 
               published_at DATETIME, image_url TEXT)""")
db.commit()

def register(conn,addr):
    data = conn.recv(1024).decode('utf-8')
    details = data.split('|')
    if len(details) != 7:
        conn.send("Invalid registration data".encode('utf-8'))
        return
    email, password, first_name, middle_name, last_name, username, address = details
    
    try:
        #Check if username exists in table
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.send("Username already taken".encode('utf-8'))
            handle_thread = threading.Thread(target=handle_client, args=(conn, addr))
            handle_thread.start()
            handle_thread.join()
            return

        # Check if email exists in table
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.send("Email already registered".encode('utf-8'))
            handle_thread = threading.Thread(target=handle_client, args=(conn, addr))
            handle_thread.start()
            handle_thread.join()
            return

        cursor.execute("""INSERT INTO users(email, password, first_name, middle_name, last_name, username, address,owner_online)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                          (email, password, first_name, middle_name, last_name, username, address,1))
        db.commit()
        user_i = cursor.lastrowid
        user_id=str(user_i)
        conn.send(f"Registration successful|{user_id}".encode('utf-8'))
        view_thread = threading.Thread(target=viewprod, args=(conn,addr))
        view_thread.start()
        view_thread.join()
    except Exception as e:
        error_msg = f"Registration failed: {str(e)}"
        conn.send(error_msg.encode('utf-8'))
        handle_thread = threading.Thread(target=handle_client, args=(conn, addr))
        handle_thread.start()
        handle_thread.join()

def log_in(conn,addr):
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
        view_thread = threading.Thread(target=viewprod, args=(conn,addr))
        view_thread.start()
        view_thread.join()
        
    else:
        conn.send("Invalid login credentials".encode('utf-8'))
        handle_thread = threading.Thread(target=handle_client, args=(conn,addr))
        handle_thread.start()
        handle_thread.join() 

def check_specific_client_online(target_username):
    # Check if the specific target client is online
    cursor.execute("SELECT owner_online FROM users WHERE username=?", (target_username,))
    result = cursor.fetchone()
    return result is not None and result[0] == 1

def initiate_chat(conn1, target_username):
    # Check if the specific target client is online
    if not check_specific_client_online(target_username):
        conn1.send(f"Client '{target_username}' is not online.".encode('utf-8'))
        return

    # Wait for the specific target client to connect
    conn2, addr2 = server.accept()
    print(f"Connected to {addr2}")

    # Inform both clients that the chat can begin
    conn1.send(f"Chat initiated with {target_username}. You can start chatting!".encode('utf-8'))
    conn2.send("You can start chatting!".encode('utf-8'))

    # Function to handle communication between clients
    def forward_messages(sender_conn, receiver_conn):
        while True:
            try:
                message = sender_conn.recv(1024).decode()
                if message.lower() == 'exit':
                    break
                receiver_conn.send(message.encode())
            except:
                break

    # Create threads to handle the chat in both directions
    thread1 = threading.Thread(target=forward_messages, args=(conn1, conn2))
    thread2 = threading.Thread(target=forward_messages, args=(conn2, conn1))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
  
def add_product(conn):
    data=conn.recv(1024).decode('utf-8')
    
    infos=data.split('|')
    user_id,productnm,desc,price,image,category=infos
    """cursor.execute(
        "INSERT INTO users (user_id INT, product_name TEXT, price REAL,description TEXT, category TEXT, published_at DATETIME, image_url TEXT, owner_online INT) VALUES (?, ?, ?, ?, ?, DATETIME('now'),?,1)", 
        (user_id, productnm, price, desc, category, image)
    )"""
    cursor.execute(
        """
        INSERT INTO products 
        (user_id, product_name, price, description, category, published_at, image_url) 
        VALUES (?, ?, ?, ?, ?, DATETIME('now'), ?)
        """, 
        (user_id, productnm, float(price), desc, category, image)
    )
    db.commit()
    print("Products in the database:")
    cursor.execute("SELECT * FROM products")
    users = cursor.fetchall()
    for user in users:
        print(user)

def viewprod(conn,addr):
    cursor.execute("SELECT product_name, price ,description, image_url FROM products")
    rows = cursor.fetchall()
    columns = ["product_name", "price", "description", "image_url"]
    data = [dict(zip(columns, row)) for row in rows]
    jason= json.dumps(data)
    conn.sendall(jason.encode('utf-8'))
    print("Data sent to client.")
    handle2_thread = threading.Thread(target=handle_client2, args=(conn,addr))
    handle2_thread.start()
    handle2_thread.join()

def handle_client2(conn,addr):
    msg=conn.recv(1024).decode('utf-8')
    if(msg=="sell"):
        sell_thread = threading.Thread(target=add_product, args=(conn,))
        sell_thread.start()
        sell_thread.join() 
    elif(msg=="buy"):
        buy_thread = threading.Thread(target=buy_product, args=(conn,))
        buy_thread.start()
        buy_thread.join()    
    elif(msg=="view products of an owner"):
        view_thread = threading.Thread(target=viewprod, args=(conn,))
        view_thread.start()
        view_thread.join()
    elif(msg=="chat"):
        chat_thread = threading.Thread(target=chat, args=(conn,))
        chat_thread.start()
        chat_thread.join()        
    else:
        handle_client2(conn,addr)    

def handle_client(conn, addr):
    try:
        request = conn.recv(1024).decode('utf-8')
        if request == "register":
            register_thread = threading.Thread(target=register, args=(conn,addr))
            register_thread.start()
            register_thread.join()
        elif request == "log in":
            login_thread = threading.Thread(target=log_in, args=(conn,addr))
            login_thread.start()
            login_thread.join()
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

def buy_product(conn, cursor, db):
    product_id = int(conn.recv(1024).decode('utf-8'))
    cursor.execute("UPDATE products SET owner_online=0 WHERE product_id=?", (product_id,))
    db.commit()
    conn.send("Purchase successful! Collect from AUB post office on the specified date.".encode('utf-8'))


