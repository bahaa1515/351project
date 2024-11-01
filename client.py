import socket
import threading
import json

def register(client):
    try:
        user_email = input("Please enter your email: ")
        user_password = input("Please enter your password: ")
        first_name = input("Please enter your first name: ")
        middle_name = input("Please enter your middle name (optional, press Enter to skip): ")
        last_name = input("Please enter your last name: ")
        username = input("Please choose a username: ")
        address = input("Please enter your address: ")

        message = f"{user_email}|{user_password}|{first_name}|{middle_name}|{last_name}|{username}|{address}"
        client.send(message.encode('utf-8'))
        print("Registration information sent")
        mse=client.recv(1024).decode('utf-8')
        ms=mse.split('|')
        if(ms[0]=="Registration successful"):
            user_id=int(ms[1])
            handle_thread = threading.Thread(target=handle_client2, args=(client,user_id))
            handle_thread.start()
            handle_thread.join()
        else:
                print("Invalid login credentials.")    
    except ConnectionAbortedError:
        print("Connection was aborted by the server.")
    except Exception as e:
        print(f"Unexpected error: {e}")           


def log_in(client):
    try:
        username = input("Please enter your username: ")
        user_password = input("Please enter your password: ")
        msg = f"{username}|{user_password}"
        print(f"Sending login data: {msg}")
        client.send(msg.encode('utf-8'))

        message = client.recv(1024).decode('utf-8')
        mess=message.split('|')
        print("Response from server:", mess)
        
        if mess[0] == "Log in successful":
            user_id=int(mess[1])
            handle_thread = threading.Thread(target=handle_client2, args=(client,user_id))
            handle_thread.start()
            handle_thread.join() 

        else:
            print("Invalid login credentials.")
    except ConnectionAbortedError:
        print("Connection was aborted by the server.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def add_product(client,user_id):
    productnm=input("Enter product name: ")
    desc=input("Enter product description: ")
    price=input("Enter product price: ")
    image=input("Enter product image URL: ")
    category=input("Enter product category (e.g. Books, electronics...): ")
    prodi=f"{user_id}|{productnm}|{desc}|{price}|{image}|{category}"
    prod=json.dumps(prodi)
    client.send(prod.encode('utf-8'))

def view_prod(client):
    data = client.recv(4096)
    if data:
        # Decode JSON data to display
        data = json.loads(data.decode('utf-8'))
        print("Received data from server:")
        
        # Display the received data
        for item in data:
            print(item)

def handle_client2(client,user_id):
    msge=input("Do you want to sell or buy a product? (respond by 'sell' or 'buy' or 'view' only)")
    
    if(msge=="sell"):
        sell_thread = threading.Thread(target=add_product, args=(client,user_id))
        sell_thread.start()
        sell_thread.join() 
    elif(msge=="view"):
        view_thread = threading.Thread(target=view_prod, args=(client,))
        view_thread.start()
        view_thread.join()  
    else:
        handle_client2(client,user_id)

def start(client):
    action = input("Type 'register' or 'log in': ").strip().lower()

    if action == "register":
        client.send(action.encode('utf-8'))
        register_thread = threading.Thread(target=register, args=(client,))
        register_thread.start()
        register_thread.join()
    elif action == "log in":
        client.send(action.encode('utf-8'))
        log_in_thread = threading.Thread(target=log_in, args=(client,))
        log_in_thread.start()
        log_in_thread.join()
    else:
        print("Invalid option. Please type 'register' or 'log in' only.")
        start(client)

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((socket.gethostbyname(socket.gethostname()), 8036))
    start(client)
    client.close()

if __name__ == "__main__":
    connect_to_server()
    
"""get a list of products immediatly"""
"""can 1)view products of a particular owner
2) check if product owner is online and communicate with him through !!server!!
3)buy products then get a message to get them from AUB post office on a certain date
4)add product the count is one// provide name, description, image, price and category(we suggest for him a number of categories and he should choose from them)
5)if product bought can see buyer basic infos (name,...)
"""    
"""server should keep track of all the users together maybe using multiple sockets(master socket)...UDP differ from TCP review chp.3
+ should be able to send messages between different users for each client there should be a port number different from the other """

def add_product():
    product_name = input("Enter product name: ")
    description = input("Enter product description: ")
    price = float(input("Enter product price: "))
    category = input("Enter product category (e.g., electronics, fashion, etc.): ")
    image_url = input("Enter image URL (or leave blank if none): ")
    
    client.send("add_product".encode('utf-8'))
    client.send(product_name.encode('utf-8'))
    client.send(description.encode('utf-8'))
    client.send(str(price).encode('utf-8'))
    client.send(category.encode('utf-8'))
    client.send(image_url.encode('utf-8'))
    print(client.recv(1024).decode('utf-8'))

def view_products():
    client.send("view_products".encode('utf-8'))
    products = client.recv(4096).decode('utf-8')
    print("Available products:\n", products)


def buy_product():
    product_id = input("Enter the product ID you wish to buy: ")
    client.send("buy_product".encode('utf-8'))
    client.send(product_id.encode('utf-8'))
    confirmation = client.recv(1024).decode('utf-8')
    print(confirmation)


