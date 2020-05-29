import multiprocessing
import parser
import socket
import threading
from config_file import ConfigParser

parser = ConfigParser()
parser.read('conf.ini')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_name = (socket.gethostbyname(socket.gethostname()), 4096)
IPAddr = socket.gethostbyname(socket.gethostname())
counter = 0
count = 0
pac_cap = parser.getboolean('Maximum', 'Start')
connection_hs = True
heartbeat_ = True


# Heartbeat funktionen
def heartbeat():
    if heartbeat_:
        threading.Timer(parser.getint('Heartbeat', 'time'), heartbeat).start()
        heartbeat_msg = 'con-h 0x00'
        heartbeat_msg_sent = sock.sendto(heartbeat_msg.encode(), server_name)
        print('test HB')

    else:
        print("No Heartbeat Action")
        sock.close()


def handshake_client():
    # den første besked til Serveren

    try:
        c_request = 'com-' + str(counter) + ' ' + IPAddr
        sent = sock.sendto(c_request.encode(), server_name)
        msg, server = sock.recvfrom(4096)
        msg_string = msg.decode()
        print('{}'.format(msg.decode()))
        data_spilt = msg.decode().split('t ', 1)
        # forsøg på hack protokol, beskeden og IP
        if msg_string.startswith('com-0 accept') and socket.inet_aton(data_spilt[1]):
            c_accept = 'com-' + str(counter) + ' accept'
            for c_accept in msg_string:
                print()
                sent = sock.sendto(c_accept.encode(), server_name)
            sent = sock.sendto(c_accept.encode(), server_name)

            if not parser.getboolean('Maximum', 'Start'):
                global heartbeat_
                heartbeat_ = parser.getboolean('Heartbeat', 'keepalive')
                heartbeat()
                if parser.getint('Heartbeat', 'time') == 3:
                    connection_hs()
                else:
                    connection_msg()

            else:
                heartbeat_ = parser.getboolean('Heartbeat', 'keepalive')
                heartbeat()
                package_cap()

        else:
            sent = sock.sendto('denied '.encode() + IPAddr.encode(), server_name)
            print('Con not allowed. Client closing')
            sock.close()
            exit()

    finally:
        # If connection to server not accepted close
        if connection_hs() == False and parser.getboolean('Maximum', 'Start') == False:
            print('Error')
            sock.close()
            exit()


# Søger efter Ny besked fra server
def connection_msg():
    while connection_hs:
        res_s, server = sock.recvfrom(4096)
        res_s_decoded = res_s.decode()
        if 'con-res ' in res_s_decoded:
            print(res_s_decoded)
            hb_msg = 'con-res 0xFF'
            hb_msg = sock.sendto(hb_msg.encode(), server_name)
            print("No Activity - Disconnecting Client")
            global heartbeat_
            heartbeat_ = False
            sock.close()
            exit()


def connection_hs():
    while True:
        print("Start Msg")
        message_input = input()
        global count
        msg = 'msg-' + str(count) + '=' + message_input

        sent = sock.sendto(msg.encode(), server_name)
        print(msg)
        print('sending {} bytes to {}'.format(sent, server_name))
        count += 1

        res_s, server = sock.recvfrom(4096)
        print(res_s.decode())
        count += 1


# Håndtering af antallet af packeges serveren kan modtage
def package_cap():
    while pac_cap:

        for x in range(parser.getint('Maximum', 'MaximumPackages')):
            msg = 'msg-' + str(counter) + '='

            multi_pro = multiprocessing.Process(target=sock.sendto, args=(msg.encode(), server_name))
            multi_pro.start()

        res_s, server = sock.recvfrom(4096)
        res_s_decoded = res_s.decode()
        print(res_s_decoded)
        global heartbeat_
        heartbeat_ = False
        sock.close()
        break


handshake_client()
