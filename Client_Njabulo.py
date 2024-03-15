import socket
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

class ChatApp(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cou = 0
        self.cou1 = 0
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.d_addr = ''
        self.s_addr = ''
        self.name = ''
        self.ac_code = '123'
        
        self.setWindowTitle("Chat App")
        self.setGeometry(500, 500, 500, 500)
        layout = QVBoxLayout()  # Changed layout to QVBoxLayout
        self.setLayout(layout)
        self.setWindowIcon(QIcon("msg_icon.png"))

        ip_layout = QHBoxLayout()
        layout.addLayout(ip_layout)

        self.ip = QLineEdit()
        self.ip.setPlaceholderText("hostname,port#")
        ip_layout.addWidget(self.ip)

        self.conn = QPushButton("Connect")
        ip_layout.addWidget(self.conn)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Enter your name:")
        layout.addWidget(self.edit)

        self.lst = QListWidget()
        layout.addWidget(self.lst)

        choice_layout = QHBoxLayout()
        layout.addLayout(choice_layout)

        self.choice = QLineEdit()
        self.choice.setPlaceholderText("Choose")
        choice_layout.addWidget(self.choice)
        #self.choice.setEnabled(False)

        self.opt = QPushButton("Select")
        choice_layout.addWidget(self.opt)
        self.opt.setEnabled(False)

        msg_layout = QHBoxLayout()
        layout.addLayout(msg_layout)

        self.msg_edit = QLineEdit()
        self.msg_edit.setPlaceholderText("Enter your message here:")
        msg_layout.addWidget(self.msg_edit)

        self.sendbutton = QPushButton("Send")
        msg_layout.addWidget(self.sendbutton)
        self.sendbutton.setEnabled(False)
        self.combo = QComboBox()
        self.combo.addItem('text')
        self.combo.addItem('media')
        layout.addWidget(self.combo)

        self.quitB = QPushButton("Quit")  # Define quit button
        layout.addWidget(self.quitB)  # Add quit button to layout

        self.conn.clicked.connect(self.connect_to_server)
        self.opt.clicked.connect(self.send)
        self.sendbutton.clicked.connect(self.send_msg)
        self.recv_thread = threading.Thread(target=self.get_msg)
        self.quitB.clicked.connect(self.quit)  # Connect quit button to quit method
        self.g_t = threading.Thread(target=self.get_udp_msg, args=(self.s_addr, self.udp_socket))
    
    def connect_to_server(self):
        self.name = str(self.edit.text())
        self.host = str(self.ip.text()).split(',')
 
        while True:
            code, ok_pressed = QInputDialog.getText(self, 'Input Dialog', 'Enter the access code:')
            if ok_pressed:
                if code == self.ac_code:
                    break
                else:                    
                    QMessageBox.warning(self, 'Invalid Code', 'Invalid access code. Please try again.', QMessageBox.Ok)

        while True:
            try:
                self.tcp_socket.connect((self.host[0], int(self.host[1])))
                self.tcp_socket.send(self.name.encode("ascii"))
                send_thread = threading.Thread(target=self.send)
                self.conn.setEnabled(False)
                self.edit.setEnabled(False)
                self.ip.setEnabled(False)
                self.opt.setEnabled(True)
                #self.choice.setEnabled(True)
                break
            except:
                msg = QMessageBox()  
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("ERROR") 
                msg.setInformativeText("Connection error!\nPlease Try to connect again")
                msg.exec_()
                return
       
        send_thread.start()
        self.recv_thread.start()
    
    def get_msg(self):
        while True:
            msg = self.tcp_socket.recv(1024).decode('ascii')
            if msg.startswith('Request') or msg.startswith('Accept'):
                pass
            else:
                self.lst.addItem(QListWidgetItem(msg[msg.find(":")+1:]))
        
            if msg.startswith("Request"):
                d_addr = msg[msg.find(':')+1:msg.find('/')].strip('()').split(',')
                s_addr = msg[msg.find('/')+1:].strip('()').split(',')
                print(s_addr)
                print(d_addr)
                m_t = threading.Thread(target=self.start_p2p_connection, args=(d_addr,s_addr))
                m_t.start()
                global cou1
                self.cou1 = 1
                self.lst.addItem(QListWidgetItem("\n***********************\n              CHATS\n***********************"))
                self.sendbutton.setEnabled(True)
               # self.choice.setEnabled(True)
                break
            elif msg.startswith('Accept'):
                d_addr = msg[msg.find(':')+1:msg.find('/')].strip('()').split(',')
                s_addr = msg[msg.find('/')+1:].strip('()').split(',')
                m_t = threading.Thread(target=self.start_p2p_connection, args=(d_addr,s_addr))
                m_t.start()
                global cou
                self.cou = 1
                self.lst.addItem(QListWidgetItem("\n***********************\n              CHATS\n***********************"))
                self.sendbutton.setEnabled(True)
                #self.choice.setEnabled(True)
                break
            elif msg.startswith("Permission"):
                pass

    def send(self):
        text = str(self.choice.text())
        self.tcp_socket.send(text.encode('ascii'))
        self.choice.clear()

        if text == '3':
            self.tcp_socket.close()
            
    
    def get_udp_msg(self,s_addr,udp_socket):
        self.udp_socket = udp_socket
        x=0
        
        while True:
            msg, addr = self.udp_socket.recvfrom(1024)
            try:
                msg = msg.decode("ascii")
                self.lst.addItem(QListWidgetItem(msg[msg.find(';')+1:]))
            except:
                try:
                    with open( "/home/zwelibanzi/Music/output.txt", 'wb') as file:
                        x=x+1
                        file.write(msg)
                    print("File is fully received "+str(x))
                except:
                    print('failed to download file')

    def start_p2p_connection(self,d_addr, s_addr):
        self.d_addr = d_addr
        self.s_addr = s_addr
        so_address = (self.s_addr[0].strip("'"),int(self.s_addr[1].strip(')')))

        self.udp_socket.bind(so_address)
        self.g_t.start()

    def send_msg(self):
        txt = self.combo.currentText()
        msg = self.msg_edit.text()
        if txt=='text':
            
            self.udp_socket.sendto(("text;"+str(self.name)+": "+msg).encode('ascii'), (self.d_addr[0].strip("'"),int(self.d_addr[1])))
            self.msg_edit.clear()
            msg = msg
            self.lst.addItem(QListWidgetItem(self.name+': '+msg))
            print("message sent to",self.d_addr)
        else:
            try:
                with open(msg,'rb') as file:
                    #data = file.read(1024)
                    for data in iter(lambda: file.read(1024), b''):
                        self.udp_socket.sendto(data, (self.d_addr[0].strip("'"),int(self.d_addr[1])))
                self.msg_edit.clear()
                print('File sent!')
            except:
                print("failed to send data")
    def quit(self):
        self.udp_socket.close()
        self.tcp_socket.close()
        self.close()
        
def run_chat_app():

    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_chat_app()
