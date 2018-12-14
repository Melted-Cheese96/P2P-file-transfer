import socket
import os
import shutil 
from time import sleep
import getpass
import sys 

hostname = getpass.getuser()

def send_image_file(image_bytes, file_name):
    host = '192.168.0.250'
    port = 1035
    img_query = 'IMG'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.sendall(str.encode(img_query))
        file_name = 'FILENAME:{}'.format(file_name)
        print(file_name)
        s.sendall(str.encode(file_name))
        #print(type(image_bytes))
        #print(image_bytes)
        image_size = len(image_bytes)
        image_size = str(image_size)
        print(image_size)
        s.sendall(str.encode(image_size))
        s.sendall(image_bytes)
        response = s.recv(1024)
        print(response.decode())
        s.close()
        print('Restarting... \n')
        sleep(2)
        prompt()
    except ConnectionRefusedError:
        print('Server appears to be down or you are not connected to the internet! Restarting... \n')
        prompt()


def send_text_file(information, file_name):
    host = '192.168.0.250'
    port = 1035
    file_name_query = 'FILENAME'
    #print(file_name)
    #print(file_name_query)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(str.encode(file_name_query))
    s.sendall(str.encode(file_name))
    #check_if_file_already_saved = s.recv(1024)
    sleep(2)
    s.sendall(str.encode(information))
    sleep(4)
    s.sendall(b'FINISH')
    response = s.recv(1024)
    print(response.decode())
    s.close()
    print('Restarting... \n')
    sleep(2)
    prompt()


def retrieve_file(direc, name, file_type): # Gets the file from local machine and sets it up to send to the server..
    try:
        os.chdir(direc)
    except FileNotFoundError:
        print('That directory was not found')
        prompt()
    if file_type == '1':
        file_content = ''
        try:
            with open(name, 'r') as user_selected_file:
                file_content = user_selected_file.read()
            print(file_content)
            send_text_file(file_content, name)
        except FileNotFoundError:
            print('That file name was not found!')
            prompt()
    elif file_type == '2':            
        try:
            with open(name, 'rb') as image_file:
                image_content = image_file.read()
            #send_information_to_server(image_content, file_type)
            send_image_file(image_content, name)
        except FileNotFoundError:
            print('The file name that you entered was not found!')


def get_saved_file(file_name): # Gets file from the server that the user has asked for.
    retrieve_query = 'RET:{}'.format(file_name)
    host = '192.168.0.250'
    port = 1035
    byte_size = 512
    text_content = '' 
    download_folder_path = '/home/{}/Downloads'.format(hostname)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(b'RET')
        sleep(2)
        s.sendall(str.encode(file_name))
        sleep(2)
        while True:
            response = s.recv(byte_size)
            text_content += response.decode()
            if len(response) < byte_size:
                break
        s.close()
        print(text_content)
        os.chdir(download_folder_path)
        with open(file_name, 'w') as doc:
            doc.write(text_content)
        print('File has been retrieved and saved in your downloads folder!')
        print('Restarting... \n')
        sleep(2)
        prompt()
    except ConnectionRefusedError:
        print('Error connecting to the server, check your internet connection and the server\'s status')
        prompt()



def prompt():
    print('Type in 1 to send a text file or type in 2 to send an image file. Or type in 3 to retrieve a file that you have saved. Type in 4 to quit \n')
    type_of_file = input()
    if type_of_file == '1':            
        directory = input('Enter directory where file is stored')
        file_name = input('Enter file name')
        retrieve_file(directory, file_name, type_of_file)
    elif type_of_file == '2':
        directory = input('Enter directory where image is stored')
        image_name = input('Enter image name')
        retrieve_file(directory, image_name, type_of_file)
    elif type_of_file == '3':
        file_name = input('Enter filename: ')
        get_saved_file(file_name)
    elif type_of_file == '4':
        print('Quitting... \n')
        sys.exit()
    else:
        print('Error, input not recognized. Please enter either 1,2,or 3')
        prompt()


prompt()
