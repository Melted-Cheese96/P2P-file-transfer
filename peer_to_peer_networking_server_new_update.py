import socket
import threading
import os
import pickle
from time import sleep

class PTPServer:
    def __init__(self):
        self.host = '192.168.0.250'
        self.port = 1035
        self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_connection.bind((self.host, self.port))
        self.listen_to_server()

    @staticmethod
    def save_image(image_data, file_name):
        file_name = file_name.split(':')
        file_name = file_name[1]
        print(file_name)
        with open(file_name, 'wb') as image_file:
            #pickle.dump(image_data, image_file)
            image_file.write(image_data)

    def start_save_image_thread(self, data, file_name):
        print(file_name)
        thread3 = threading.Thread(target=self.save_image(data, file_name))
        thread3.start()

    def listen_to_server(self):
        self.socket_connection.listen()
        while True:
            print('Server running')
            c, addr = self.socket_connection.accept()
            print('Connection from {}'.format(addr))
            thread1 = threading.Thread(target=self.receive_information(c))
            thread1.start()

    @staticmethod
    def read_file(file_name):
        with open(file_name ,'r') as doc:
            file_content = doc.read()
        return file_content

    def receive_information(self, client):
        while True:
            data = client.recv(1024)
            if data:
                data = data.decode()
                if 'IMG' in data:
                    print('Img Query')
                    while True:
                        file_name = client.recv(1024)
                        file_name = file_name.decode()
                        #file_name = data.decode()
                        #print(file_name)
                        while True:
                            image_size = client.recv(1024)
                            print(image_size)
                            #image_size = image_size.decode()
                            while True:
                                #size = image_size.decode()
                                size = int(image_size)
                                image_bytes = client.recv(size)
                                self.start_save_image_thread(image_bytes, file_name)
                                client.sendall(b'Image saved!')
                                client.close()
                                self.listen_to_server()
                if 'FILENAME' in data:  # Checks if 'filename' is in the data that was just received. If so a text file is being sent
                    text_content = ''
                    while True:
                        file_name = client.recv(1024)
                        if file_name: # Runs this code if something has been sent
                            print(file_name.decode())
                            if file_name.decode() in os.listdir():
                                client.sendall(b'File already saved')
                                client.close()
                                self.listen_to_server()
                            else:
                                while True:
                                    information = client.recv(1024) # This is the text information that is being sent by client
                                    if len(information) <= 6: # The user will send over 'FINISH' when it's done sending all information. This checks if the length of the information received was 6 letter
                                        client.sendall(b'File stored!')
                                        client.close()
                                        self.listen_to_server()
                                    else: # If the length of the info received is more than 6 this runs.
                                        text_content += information.decode()
                                        with open(file_name, 'w') as doc:
                                            doc.write(text_content)
                elif 'RET' in data: # Tells the server that the client wants to retrieve a piece of information.
                    print('RETRIEVE REQUEST')
                    while True:
                        file_to_retrieve = client.recv(1024) # Gets file name from the client.
                        if file_to_retrieve:
                            file_information = self.read_file(file_to_retrieve.decode())
                            print(file_information)
                            client.sendall(str.encode(file_information))
                            client.close()
                            self.listen_to_server()
                else:
                    client.sendall(b'File name was not given!')

            else:
                client.close()
                self.listen_to_server()


server = PTPServer()
