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

clients = {}

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

def buy_product(conn):
    try:
        # Ask the client for the name of the product they want to buy
        product_name = conn.recv(1024).decode('utf-8').strip()

        # Check if the product exists in the database
        cursor.execute("SELECT * FROM products WHERE product_name = ?", (product_name,))
        product = cursor.fetchone()

        if not product:
            conn.send("Product not found.".encode('utf-8'))
            return

        # Send product details to the client for confirmation
        conn.send(" Confirm purchase? (yes/no): ".encode('utf-8'))
        confirmation = conn.recv(1024).decode('utf-8').strip().lower()

        if confirmation == "yes":
            # Remove the product from the database
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product[0],))
            db.commit()
            conn.send("Purchase successful. The product has been removed from the database.".encode('utf-8'))
        else:
            conn.send("Purchase canceled.".encode('utf-8'))
    except Exception as e:
        conn.send(f"Error during purchase: {str(e)}".encode('utf-8'))


"""def handle_client3(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            # The format for sending a private message is: /msg [recipient_username] [message]
            if message.startswith("/msg"):
                _, recipient, private_msg = message.split(" ", 2)
                if recipient in clients:
                    clients[recipient].send(f"[{username} -> You]: {private_msg}".encode('utf-8'))
                    client_socket.send(f"[You -> {recipient}]: {private_msg}".encode('utf-8'))
                else:
                    client_socket.send(f"User {recipient} is not online.".encode('utf-8'))
            else:
                client_socket.send("Invalid command. Use /msg [username] [message] to send a private message.".encode('utf-8'))
        except:
            break

    # Remove disconnected user
    print(f"{username} disconnected")
    client_socket.close()
    del clients[username]
    print(f"{username} has left the chat.")"""


"""def initiate_chat(conn):
    target_username = conn.recv(1024).decode('utf-8').strip()

    if target_username in clients:
        target_conn = clients[target_username]
        conn.send(f"User {target_username} is online. Starting chat...".encode('utf-8'))
        target_conn.send(f"User wants to chat with you. Starting chat...".encode('utf-8'))
        
        # Start chat session
        chat_thread = threading.Thread(target=chat_session, args=(conn, target_conn))
        chat_thread.start()
    else:
        conn.send("User is not online or does not exist.".encode('utf-8'))

def chat_session(conn1, conn2):
    while True:
        try:
            message = conn1.recv(1024).decode('utf-8')
            if message.lower() == "exit":
                conn1.send("Chat ended.".encode('utf-8'))
                conn2.send("Chat ended.".encode('utf-8'))
                break
            conn2.send(message.encode('utf-8'))
        except:
            break"""

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

def get_products_by_owner(conn, user_id):
    cursor.execute("SELECT product_name, price, description, image_url FROM products WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    columns = ["product_name", "price", "description", "image_url"]
    data = [dict(zip(columns, row)) for row in rows]
    jason = json.dumps(data)
    conn.sendall(jason.encode('utf-8'))
    print(f"Products for user ID {user_id} sent to client.")
    handle2_thread = threading.Thread(target=handle_client2, args=(conn,addr))
    handle2_thread.start()
    handle2_thread.join()

def handle_client2(conn,addr,):
    msg=conn.recv(1024).decode('utf-8')
    if(msg=="sell"):
        sell_thread = threading.Thread(target=add_product, args=(conn,))
        sell_thread.start()
        sell_thread.join() 
    elif(msg=="buy"):
        buy_thread = threading.Thread(target=buy_product, args=(conn,))
        buy_thread.start()
        buy_thread.join()    
    elif(msg=="owner"):
        user_id = conn.recv(1024).decode('utf-8')  # Get user_id from client
        owner_thread = threading.Thread(target=get_products_by_owner, args=(conn, user_id))  # Fetch products for the specific owner
        owner_thread.start()
        owner_thread.join()
    elif(msg=="view"):
        view_thread = threading.Thread(target=viewprod, args=(conn,addr))
        view_thread.start()
        view_thread.join()
    elif(msg=="chat"):
        chat_thread = threading.Thread(target=handle_client3, args=(conn,))
        chat_thread.start()
        chat_thread.join()       
    elif(msg =="exit"):
        conn.close()

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


