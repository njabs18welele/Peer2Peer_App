from socket import *
import time
import threading

tcp_socket = socket(AF_INET, SOCK_STREAM)
tcp_socket.bind(('localhost', 2036))  
tcp_socket.listen(2)
clients = []
Names = []
addresses = []
c_name =''
options = 'Options:\n[1]. Get available clients.\n[2]. Chats\n[3]. Quit\n'
def tcp_connect():
    x=0
    print("Waiting for clients")
    while True:
        try:
            conn, addr = tcp_socket.accept()  #The code will wait here until the client is connected
            print(addr)
            clients.append(conn)
            addresses.append(addr)

            print(" client is connected to server")
            #for option in options:
            conn.send(options.encode('ascii'))
            msg_thread = threading.Thread(target=tcp_handle_msg, args=(conn,))
            msg_thread.start()
            #print()

        except:
            print("The server have reached the maximum number of clients that can connnect to it.")
   

def tcp_handle_msg(client):
    x=clients.index(client)
    while True:
        msg = client.recv(1024).decode('ascii')
        if not msg:
            break
        if msg == '1':
            string = "ACTIVE CLIENTS:\n"
            cou=1
            for name in Names:
                if name == None:
                    pass
                else:
                    string = string + ">> "+str(name)+'\n'
                    cou = cou+1
            string = string+"\n------------------------------\n"
            client.send((string+'\n'+options).encode("ascii"))
            #client.send(options.encode('ascii'))
        elif msg == '2':
            #if msg =='2':
            client.send('Who do you want to connect to?\n'.encode('ascii'))
            nm=''
            for i in range(len(Names)):
                nm = nm+f"{str(i+1)}. {Names[i]}\n"
                #client.send((str(i+1)+". "+Names[i]+'\n').encode('ascii'))
            nm = nm+'------------------------------\n'
            client.send(nm.encode('ascii'))
            opt = int(client.recv(1024).decode('ascii'))
            clients[opt-1].send(("Permission:------------------------------\n"+str(c_name)+" want to chat with you. Are you in? \n[a]. Yes\n[b]. No\n------------------------------").encode('ascii'))
            
            response = clients[opt-1].recv(1024).decode("ascii")
            if response == 'a':
                s_address = addresses[x]
                d_address = addresses[opt-1]
                client.send(('Requested address:'+str(d_address)+'/'+str(s_address)).encode('ascii'))
                clients[opt-1].send(('Accept request..:'+str(s_address)+'/'+str(d_address)).encode('ascii'))

                client.send((f":{Names[opt-1]} accepted your request").encode())
            else:
               client.send((f"{Names[opt-1]} rejected you request").encode("ascii"))

        elif msg == '3':
            
            clients.remove(client)
            print(Names[x],"exited the chat.")
            Names[x]= None
            if len(Names)==0:
                tcp_socket.close()
               
            
        else:
            if len(msg)<2:
                pass
            else:
                Names.append(msg)
                c_name = msg

def main():
    tcp_connect()
main()