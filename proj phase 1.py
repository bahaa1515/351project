#server
import random
import sqlite3
import socket
#Bahaa hamdan
def generate_unique_user_id(cursor):
    while True:
        # Generate a random number between 1000 and 9999 inclusive => 4-digit
        user_id = random.randint(1000, 9999)

        cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]

        if count == 0:  # User ID not in database already
            return user_id  

db=sqlite3.connect('products.db')
cursor=db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INT, email TEXT, password TEXT, first_name TEXT, middle_name TEXT, last_name TEXT, username TEXT, creationdate DATETIME, address TEXT)") 

# phone number cannot be int due to leading zeros and other factors 

cursor.execute("CREATE TABLE IF NOT EXISTS products(product_id INT,user_id INT, product_name TEXT, price REAL,description TEXT, category TEXT, published_at DATETIME, image_url TEXT, owner_online INT)")
#owner_online is int because there is only one boolean representation either 0 or 1 however text can be true/false or yes/no etc...
#category may be used for cookies
db.commit()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostbyname(socket.gethostname()),8036))
server.listen()

conn, addr = server.accept()
request = conn.recv(1024).decode('utf-8')

#Bahaa hamdan
def register():
    user_email = conn.recv(1024).decode('utf-8')
    user_password = conn.recv(1024).decode('utf-8')
    first_name = conn.recv(1024).decode('utf-8')
    middle_name = conn.recv(1024).decode('utf-8')
    last_name = conn.recv(1024).decode('utf-8')
    username = conn.recv(1024).decode('utf-8')
    address = conn.recv(1024).decode('utf-8')
    
    
    user_id=generate_unique_user_id(cursor)
    cursor.execute("INSERT INTO users values(?,?,?,?,?,?,?, DATETIME('now'),?)", (user_id, user_email, user_password, first_name, middle_name, last_name, username, address))
    db.commit()

#Bahaa hamdan
def log_in():
    usernm=conn.recv(1024).decode('utf-8')
    user_pass =conn.recv(1024).decode('utf-8')
    cursor.execute("SELECT * FROM users WHERE username=? AND user_password=?",(usernm,user_pass))
    user=cursor.fetchone()
    if user:
        conn.send("Log in successfull".encode('utf-8'))
    else:
        conn.send("Log in failed".encode('utf-8'))    

if(request.lower()=="register"):
  register()
else:
    log_in()
    


db.close