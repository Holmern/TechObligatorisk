import configparser
import socket
import datetime

# Oprettelse af Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_name = (socket.gethostbyname(socket.gethostname()), 4096)
sock.bind(server_name)
ipAdress = socket.gethostbyname(socket.gethostname())
sock.settimeout(4)
counter = 1

datetime = datetime.datetime.now()
config = configparser.ConfigParser()
config.read('conf.ini')
connection = True
pac_count = 0


def handshake_server():
    # Her modtager vi information fra Clienten, som string fra det vi definerer som adresse. beskeden def som mes
    mes, address = sock.recvfrom(4096)
    print('{}'.format(mes.decode()))
    mes_c = mes.decode()
    data_spilt = mes.decode().split(' ', 1)

    # INET_Aton er en indbygget python metode til at validere IP adresser
    # besked til C sendes
    if mes_c.startswith('com-0') and socket.inet_aton(data_spilt[1]):
        accept_client = 'com-0 accept ' + ipAdress
        sent = sock.sendto(accept_client.encode(), address)
        print('com-0 accept ' + ipAdress)
        # Modtag næste besked
        mes_c, address = sock.recvfrom(4096)
        if "com-0 accept" in mes_c.decode():

            f = open('Log.txt', 'a')
            f.write("Handshake successful : " + str(datetime) + " : " + ipAdress + "\n")
            f.close()

            print("Handshake OK 41")
            first_msg()
        else:
            sock.close()
            print("Handshake bad. Closing socking")

            f = open('Log.txt', 'a')
            f.write("Handshake unsuccessful : " + str(datetime) + " : " + ipAdress + "\n")
            f.close()


# læser besked fra client og validere at det er msg-0
def first_msg():
    global address
    try:
        msg, address = sock.recvfrom(4096)
        msg_decoded = msg.decode()
        print(msg_decoded)
        if msg_decoded.startswith('msg-0'):
            send_msg(msg_decoded, address)
            msg_function()

        elif msg_decoded.startswith('con-h'):
            send_msg(msg_decoded, address)
            msg_function()

        else:
            print("Error in Message")
            sent = sock.sendto('not protocol '.encode() + ipAdress.encode(), address)

    except socket.timeout:
        _4_sec_inactive_msg = 'con-res 0xFE'
        _4_sec_inactive_sent = sock.sendto(_4_sec_inactive_msg.encode(), address)
        messages_4_sec_inactive, address = sock.recvfrom(4096)
        _4_sec_inactive_resp_client = messages_4_sec_inactive.decode()
        print("No Activity - Client disconnected " + _4_sec_inactive_resp_client)
        sock.close()
        exit()


def send_msg(use_msg_decoded, use_address):
    global pac_count
    # validering af counter, ved at oprette en counter der tager den sidste besked
    # og trækker den fra den besked
    if use_msg_decoded.startswith('msg-'):
        pre_count = use_msg_decoded.split('-')
        post_count = pre_count[1].split('=')
        global counter
        auto_res = 'res-' + str(counter) + '= I am server'
        if counter - int(post_count[0] == 1 and use_msg_decoded.startswith('msg-')):

            sent = sock.sendto(auto_res.encode(), use_address)
            pac_count += 1
            print(use_msg_decoded)
    elif use_msg_decoded.startswith('con-h'):
        print('Heartbeat OK')

        # MaxPac Check læst fra conf.ini
        if pac_count >= config.getint('Maximum', 'maximumpackages'):
            max_Cap = 'You can only pass 25 Pacs at a time'
            sent = sock.sendto(max_Cap.encode(), address)
            sock.close()
            exit()


def msg_function():
    while connection:
        global address
        msg, address = sock.recvfrom(4096)
        msg_decoded = msg.decode()
        send_msg(msg_decoded, address)


handshake_server()
