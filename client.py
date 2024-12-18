import socket
import threading
import json
import time
socket.setdefaulttimeout(300)
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
        print(ms[0])
        if(ms[0]=="Registration successful"):
            user_id=int(ms[1])
            view_thread = threading.Thread(target=view_prod, args=(client,user_id))
            view_thread.start()
            view_thread.join()
        elif(ms[0]=="Invalid registration data"):
            print(ms[0])
            return
        else:
            handle_thread = threading.Thread(target=start, args=(client,))
            handle_thread.start()
            handle_thread.join()       
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
            print(user_id)
            view_thread = threading.Thread(target=view_prod, args=(client,user_id))
            view_thread.start()
            view_thread.join()
             
        elif(mess[0]=="Invalid login data"):
            print(mess[0])
            return
        else:
            handle_thread = threading.Thread(target=start, args=(client,))
            handle_thread.start()
            handle_thread.join() 
    except ConnectionAbortedError:
        print("Connection was aborted by the server.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def initiate_chat(client):
    username2 = input("Enter the username of the person you want to chat with: ")
    client.send(username2.encode('utf-8'))
    
    response = client.recv(1024).decode('utf-8')
    print(response)
    if "Starting chat" in response:
        chat_thread = threading.Thread(target=chat_session, args=(client,))
        chat_thread.start()
        chat_thread.join()

def chat_session(client):
    print("You can start chatting now. Type 'exit' to end the chat.")
    while True:
        message = input("You: ")
        client.send(message.encode('utf-8'))
        if message.lower() == "exit":
            break
        response = client.recv(1024).decode('utf-8')
        print(f"Other: {response}")


def add_product(client,user_id):
    productnm=input("Enter product name: ")
    desc=input("Enter product description: ")
    price=input("Enter product price: ")
    image=input("Enter product image URL: ")
    category=input("Enter product category (e.g. Books, electronics...): ")
    prodi=f"{user_id}|{productnm}|{desc}|{price}|{image}|{category}"
    for attempt in range(3):
        try:
            client.send(prodi.encode('utf-8'))
            print("Product data sent successfully.")
            handle2_thread = threading.Thread(target=handle_client2, args=(client,user_id))
            handle2_thread.start()
            handle2_thread.join()
            break
        except (ConnectionAbortedError, ConnectionResetError) as e:
            print(f"Connection lost. Attempting to reconnect... ({attempt + 1}/3)")
            time.sleep(2)  # Pause before reconnecting
            # Reconnect client
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((socket.gethostbyname(socket.gethostname()), 8036))
        except Exception as e:
            print(f"Failed to send data: {e} / program will stop")  
            break 
        

def view_prod(client,user_id):
    data = client.recv(4096)
    if data:
        # Decode JSON data to display
        data = json.loads(data.decode('utf-8'))
        print("Received data from server:")
        
        # Display the received data
        for item in data:
            print(item)
    handle2_thread = threading.Thread(target=handle_client2, args=(client,user_id))
    handle2_thread.start()
    handle2_thread.join() 

def buy_product(client,user_id):
    for attempt in range(3):
        try:
            # Ask the user for the product name
            product_name = input("Enter the name of the product you want to buy: ")
            client.send(product_name.encode('utf-8'))

            # Receive and display product details or an error message
            message = client.recv(1024).decode('utf-8')
            print(message)

            if "Confirm" in message:
                # Ask the user to confirm the purchase
                confirmation = input("Type 'yes' to confirm purchase, or 'no' to cancel: ").strip().lower()
                client.send(confirmation.encode('utf-8'))

                # Receive the result of the purchase
                result = client.recv(1024).decode('utf-8')
                print(result)
            else:
                buy_thread = threading.Thread(target=buy_product, args=(client,user_id))
                buy_thread.start()
                buy_thread.join() 
        except (ConnectionAbortedError, ConnectionResetError) as e:
                print(f"Connection lost. Attempting to reconnect... ({attempt + 1}/3)")
                time.sleep(2)  # Pause before reconnecting
                # Reconnect client
                client.close()
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((socket.gethostbyname(socket.gethostname()), 8036))
        except Exception as e:
            print(f"Error during purchase: {str(e)}")
        handle2_thread = threading.Thread(target=handle_client2, args=(client,user_id))
        handle2_thread.start()
        handle2_thread.join() 

def owner_view(client,owner_id,user_id):
        client.send(owner_id.encode('utf-8'))  # Send the user_id to the server
        data = client.recv(4096)
        if data:
            # Decode JSON data to display
            data = json.loads(data.decode('utf-8'))
            print("Received data from server:")
            
            # Display the received data
            for item in data:
                print(item)
        handle2_thread = threading.Thread(target=handle_client2, args=(client,user_id))
        handle2_thread.start()
        handle2_thread.join()

def handle_client2(client,user_id):
    msge=input("Do you want to chat,sell,buy,view,or view owner specific products(respond by 'chat' or 'sell' or 'buy' or 'view' or 'owner' only)")
    client.send(msge.encode('utf-8'))
    if(msge=="sell"):
        sell_thread = threading.Thread(target=add_product, args=(client,user_id))
        sell_thread.start()
        sell_thread.join() 
    elif(msge=="buy"):
        buy_thread = threading.Thread(target=buy_product, args=(client,user_id))
        buy_thread.start()
        buy_thread.join()    
    elif(msge=="owner"):
        owner_id = input("Enter the owner ID to view products: ")
        owner_thread = threading.Thread(target= owner_view,args=(client,owner_id,user_id))
        owner_thread.start()
        owner_thread.join()
    elif(msge=="chat"):
        chat_thread = threading.Thread(target= initiate_chat, args=(client,))
        chat_thread.start()
        chat_thread.join()  
    else:
        handle2_thread = threading.Thread(target=handle_client2, args=(client,user_id))
        handle2_thread.start()
        handle2_thread.join()

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
        handle_thread = threading.Thread(target=start, args=(client,))
        handle_thread.start()
        handle_thread.join() 

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((socket.gethostbyname(socket.gethostname()), 8036))
    start(client)
    client.close()

if __name__ == "__main__":
    connect_to_server()
  


