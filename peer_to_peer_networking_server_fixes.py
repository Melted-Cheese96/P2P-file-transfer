import socket
import threading
import os
import pickle

class PTPServer:
    def __init__(self):
        self.host = '192.168.0.250'
        self.port = 1035
        self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_connection.bind((self.host, self.port))
        self.listen_to_server()

    @staticmethod
    def save_information(information, file_name): # Saves a text file
        file_name = str(file_name)
        if file_name in os.listdir():
            pass
        else:
            with open(file_name, 'w') as doc:
                doc.write(str(information))

    @staticmethod
    def save_image(image_data, file_name):
        file_name = file_name.split(':')
        file_name = file_name[1]
        print(file_name)
        with open(file_name, 'wb') as image_file:
            #pickle.dump(image_data, image_file)
            image_file.write(image_data)

    def start_save_information_thread(self, information, file_name):
        thread2 = threading.Thread(target=self.save_information(information, file_name))
        thread2.start()

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

    @staticmethod
    def cleanup(file_name):
        words = []
        text_content = ''
        with open(file_name, 'r') as doc:
            for line in doc:
                for word in line.split():
                    words.append(word)
        for item in words:
            if item == 'FINISH':
                pass
            else:
                text_content += item
                text_content += ' '
        with open(file_name, 'w') as doc:
            doc.write(text_content)

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
                            #image_bytes = client.recv(1024)
                            #print(image_bytes)
                            #self.start_save_image_thread(image_bytes, file_name)
                            #client.sendall(b'Image has been saved!')
                            #self.listen_to_server()

                if 'FILENAME' in data:  # Checks if 'filename' is in the data that was just received.
                    text_content = ''
                    buff_size = 512
                    while True:
                        file_name = client.recv(1024)
                        if file_name:
                            print(file_name.decode())
                            print('Buffer')
                            while True:
                                information = client.recv(1024)
                                text_content += information.decode()
                                print(len(information))
                                #print(text_content)
                                with open(file_name, 'w') as doc:
                                    doc.write(text_content)
                                if information.decode() == 'FINISH':
                                    client.sendall(b'File stored!')
                                    client.close()
                                    self.cleanup(file_name)
                                    self.listen_to_server()
                                '''
                                if len(information) < 400:
                                    self.start_save_information_thread(text_content, file_name.decode())
                                    client.sendall(b'File stored!')
                                    client.close()
                                    text_content = ''
                                    self.listen_to_server()
                                '''

                                '''
                                print(information.decode())
                                self.start_save_information_thread(information.decode(), file_name.decode())
                                client.sendall(b'File has been stored!')
                                client.close()
                                self.listen_to_server()
                                '''
                    '''
                    while True:  # This loop waits for other data, which is the text data. Once received it saves.
                        data = client.recv(1024)
                        if data:
                            print(data)
                            data = data.decode()
                            self.save_information(data, file_name)
                            client.sendall(b'File stored!')
                            client.close()
                            self.listen_to_server()
                            '''
                elif 'RET' in data:
                    print('RETRIEVE REQUEST')
                    while True:
                        file_to_retrieve = client.recv(1024)
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
