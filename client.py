#client

import socket

client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostbyname(socket.gethostname()),8036))

message=input("register or log in")
client.send(message.encode('utf-8'))

def register():
    user_email = input("Please enter your email: ")
    user_password = input("Please enter your password: ")
    first_name = input("Please enter your first name: ")
    middle_name = input("Please enter your middle name (optional, press Enter to skip): ")
    last_name = input("Please enter your last name: ")
    username = input("Please choose a username: ")
    address = input("Please enter your address: ")
    
    client.send(user_email.encode('utf-8'))
    client.send(user_password.encode('utf-8'))
    client.send(first_name.encode('utf-8'))
    client.send(middle_name.encode('utf-8') if middle_name else ''.encode('utf-8'))
    client.send(last_name.encode('utf-8'))
    client.send(username.encode('utf-8'))
    client.send(address.encode('utf-8'))
    
def log_in():
    username = input("Please choose a username: ")
    user_password = input("Please enter your password: ")
    client.send(username.encode('utf-8'))
    client.send(user_password.encode('utf-8'))
    message=client.recv(1024).decode('utf-8')
    print(message)
    if(message=="Log in successfull"):
        print("Do you want to sell or buy a product? (respond by 'sell' or 'buy' only)")

"""get a list of products immediatly"""
"""can 1)view products of a particular owner
2) check if product owner is online and communicate with him through !!server!!
3)buy products then get a message to get them from AUB post office on a certain date
4)add product the count is one// provide name, description, image, price and category(we suggest for him a number of categories and he should choose from them)
5)if product bought can see buyer basic infos (name,...)
"""    
"""server should keep track of all the users together maybe using multiple sockets(master socket)...UDP differ from TCP review chp.3
+ should be able to send messages between different users for each client there should be a port number different from the other """

if(message.lower()=="register"):
    register()
else:
    log_in()


