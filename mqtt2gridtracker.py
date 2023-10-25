

#
# Script for subscribing to mqtt.pskreporter and relaying to an instance of GridTracker
#

import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client

from socket import *
from sys import *

import datetime
from datetime import timezone

import json
import random
import struct
import sys
import time

import wsjtmess


# {"sq":38536561290,"f":14081487,"md":"FT4","rp":-3,"t":1691146394,"sc":"R3XBD","sl":"KO74xb","rc":"G8IXM","rl":"JO02pp29","sa":54,"ra":223,"b":"20m"}
# https://sourceforge.net/p/wsjt/wsjtx/ci/wsjtx-2.5.2/tree/Network/NetworkMessage.hpp

mycall = "MYCALL"
myloc = "XXYY"
showrec = True
showmyrec = True

version = '5'
mytransport = 'tcp'

broker = 'mqtt.pskreporter.info'
client_id = f'python-mqtt-{random.randint(0, 1000)}'
brokerport = 1883


## Set the socket parameters for Gridtracker
host = "192.168.1.158"
port = 2237
buf = 1024
addr = (host,port)

debug = True
debug = False

def connect_mqtt():
    print('Connecting to MQTT')
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, brokerport)
    return client


def processpacket(json_data):
    #pdiff = int(datetime.datetime.now().timestamp() - json_data['t'])
    printpkt(json_data)
    payload = createpacket_22(json_data)
    sendpacket(payload)        


def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        json_data = json.loads(msg.payload.decode())
        processpacket(json_data)

    print("Subscribing to: ", topic)     
    client.subscribe(topic)
    client.on_message = on_message


def sendpacket(data):
    if data[0:4] != b'\xad\xbc\xcb\xda':
        print("Bad magic number")
        return
        
    # 32-bit unsigned integer schema number
    schema=int.from_bytes(data[4:8], byteorder='big')
    sid=int.from_bytes(data[8:12], byteorder='big')

    if debug:
            print("Schema", schema, sid)

    if(UDPSock.sendto(data,addr)):
            if debug:
                    print("UDP:",data)

def utf8bytes(data):
        result = []
        strl = len(data)
        if strl == 0:
                strl = 4294967295
        if debug:
                print("size:", data, strl)
        result.append(strl.to_bytes(4,'big'))
        result.append(data.encode("utf-8"))
        return b''.join(result)

# Heartbeat     Out/In    0                      quint32
#                         Id (unique key)        utf8
#                         Maximum schema number  quint32
#                         version                utf8
#                         revision               utf8

def create_heartbeat():
    packet = []
    if debug:
        print("heartbeat")
    # magicnumber
    packet = [ b'\xad', b'\xbc', b'\xcb', b'\xda']
    # Schema + sid
    nm_schema = 2
    nm_sid = 0
    packet.append(nm_schema.to_bytes(4, 'big'))
    packet.append(nm_sid.to_bytes(4, 'big'))

    # id
    data = utf8bytes('WSJT-X')
    if debug:
        print("id:",data)
    packet.append(data)
    # max schema
    packet.append(int(2).to_bytes(4, 'big'))

    data = utf8bytes('1.0')
    if debug:
        print("versi:",data)
    packet.append(data)

    data = utf8bytes('abc')
    if debug:
        print("revis:",data)
    packet.append(data)

    if debug:
        print(packet)
    packet = b''.join(packet)
    return packet
        

# Status        Out       1                      quint32
#                         Id (unique key)        utf8
#                         Dial Frequency (Hz)    quint64
#                         Mode                   utf8
#                         DX call                utf8
#                         Report                 utf8
#                         Tx Mode                utf8
#                         Tx Enabled             bool
#                         Transmitting           bool
#                         Decoding               bool
#                         Rx DF                  qint32
#                         Tx DF                  qint32
#                         DE call                utf8
#                         DE grid                utf8
#                         DX grid                utf8
#                         Tx Watchdog            bool
#                         Sub-mode               utf8
#                         Fast mode              bool
#                         Special operation mode quint8
#                         Frequency Tolerance    quint32
#                         T/R Period             quint32
#                         Configuration Name     utf8
#                         Tx Message             utf8

def createpacket_21(jsonobj):
        # magicnumber
        packet = [ b'\xad', b'\xbc', b'\xcb', b'\xda']
        # Schema + sid
        nm_schema = 2
        nm_sid = 1
        packet.append(nm_schema.to_bytes(4, 'big'))
        packet.append(nm_sid.to_bytes(4, 'big'))

        # id
        data = utf8bytes('WSJT-X')
        if debug:
                print("id:",data)
        packet.append(data)

        # Dial freq
        dial_freq = jsonobj['f'].to_bytes(8,'big')
        if debug:
                print("dial:",dial_freq)
        packet.append(dial_freq)
    
        # Mode
        data = utf8bytes(jsonobj['md'])
        if debug:
                print("mode:",data)
        packet.append(data)

        # DX call (sender)
        data = utf8bytes(jsonobj['sc'])
        if debug:
                print("dx:",data)
        packet.append(data)

        # Report
        data = utf8bytes(str(jsonobj['rp']))
        if debug:
                print("report:",data)
        packet.append(data)

        # Tx-mode
        data = utf8bytes(jsonobj['md'])
        if debug:
                print(data)
        packet.append(data)

        # Status - txenable, transmit, decode
        packet.append(b'\x00\x00\x00')

        # TX & RX drift
        packet.append(int(0).to_bytes(4,'big'))
        packet.append(int(0).to_bytes(4,'big'))

        # DE call
        data = utf8bytes(jsonobj['rc'])
        if debug:
                print("de-call",data)
        packet.append(data)

        # DE grid
        data = utf8bytes(jsonobj['rl'])
        if debug:
                print("de-grid",data)
        packet.append(data)

        # DX grid
        data = utf8bytes(jsonobj['sl'])
        if debug:
                print("dx-grid",data)
        packet.append(data)

        # Tx Watchdog
        packet.append(b'\x00')
        
        # Sub-Mode
        data = utf8bytes('submode')
        if debug:
                print(data)
        packet.append(data)
    
        # Fast mode
        packet.append(b'\x00')

        # Special operation mode
        packet.append(int(0).to_bytes(1,'big'))

        # Frequency Tolerance    quint32
        packet.append(int(0).to_bytes(4, 'big'))

        # T/R Period             quint32
        packet.append(int(0).to_bytes(4, 'big'))
        
        # Configuration Name     utf8
        data = utf8bytes('conf')
        if debug:
                print(data)
        packet.append(data)
        
        # Tx Message             utf8
        data = utf8bytes('txmess')
        if debug:
                print(data)
        packet.append(data)
        
        if debug:
                print(packet)
        packet = b''.join(packet)
        return packet


#
# Decode        Out       2                      quint32
#                         Id (unique key)        utf8
#                         New                    bool
#                         Time                   QTime
#                         snr                    qint32
#                         Delta time (S)         float (serialized as double)
#                         Delta frequency (Hz)   quint32
#                         Mode                   utf8
#                         Message                utf8
#                         Low confidence         bool
#                         Off air                bool

# {"sq":38536561290,"f":14081487,"md":"FT4","rp":-3,"t":1691146394,"sc":"R3XBD","sl":"KO74xb","rc":"G8IXM","rl":"JO02pp29","sa":54,"ra":223,"b":"20m"}


def createpacket_22(jsonobj):
        # magicnumber
        packet = [ b'\xad', b'\xbc', b'\xcb', b'\xda']
        # Schema + sid
        nm_schema = 2
        nm_sid = 2
        packet.append(nm_schema.to_bytes(4, 'big'))
        packet.append(nm_sid.to_bytes(4, 'big'))

        # id
        data = utf8bytes('WSJT-X')
        if debug:
                print("id:",data)
        packet.append(data)

        # New
        packet.append(b'\x01')

        # Time
        timestamp = jsonobj['t']
        julian = (timestamp % (24 * 3600)) * 1000
        if debug:
                print("julian",julian)
        packet.append(julian.to_bytes(4, 'big'))
        
        # SNR
        packet.append(jsonobj['rp'].to_bytes(4,'big', signed =True))
        if debug:
                print(packet)
        
        strl = int.from_bytes(data[0:4], byteorder='big')
        report = data[4:4+strl].decode("utf-8")
        data = data[4+strl:]
        
        # Delta time
        dti = struct.pack("d", 0.0)
        if debug:
                print("dtime:",dti)
        packet.append(dti)

        # Delta freq
        dfq = int(0).to_bytes(4,'big')
        if debug:
                print("dial:",dfq)
        packet.append(dfq)
    
        # Mode
        data = utf8bytes(jsonobj['md'])
        if debug:
                print("mode:",data)
        packet.append(data)

        # Mess
        if showrec and jsonobj['rc'] != mycall:
                data = utf8bytes('CQ '+jsonobj['rc']+' '+jsonobj['rl'][0:4])
        if showmyrec and jsonobj['rc'] == mycall:
                data = utf8bytes('CQ DX '+jsonobj['sc']+' '+jsonobj['sl'][0:4])

                
        if debug:
                print("message", data)
        packet.append(data)

        # Low confidence & Off air
        packet.append(b'\x00\x00')

        packet = b''.join(packet)
        return packet




# pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}/{sendercountry}/{receivercountry}

def mqtt_run():
    client = connect_mqtt()
    if showrec:
            topic = 'pskr/filter/v2/+/+/"+mycall+"/#'
            subscribe(client, topic)
    if showmyrec:
            topic = 'pskr/filter/v2/+/+/+/"+mycall+"/#'
            subscribe(client, topic)
    # client.loop_forever()
    client.loop_start()

mqtt = True
# mqtt = False


fake_pkt_21 = {"sq":38536561290,"f":14081487,"md":"FT4","rp":-3,"t":1691146394,"sc":mycall,"sl":myloc,"rc":mycall,"rl":myloc,"sa":54,"ra":223,"b":"20m"}

def printpkt(pkt):
        time = datetime.datetime.fromtimestamp(pkt['t'])
        pdiff = int(datetime.datetime.now().timestamp() - pkt['t'])
        print("%s Age: %3ss %6.0fkHz  %2s %3ddB Sender: %-10s loc %-10s Receiver: %-10s loc %-10s" % (time, pdiff, int(pkt['f'])/1000, pkt['md'],int(pkt['rp']), pkt['sc'], pkt['sl'], pkt['rc'], pkt['rl']))

              

if __name__ == '__main__':
    ## Create socket 
    UDPSock = socket(AF_INET,SOCK_DGRAM)

    # Start mqtt 
    mqtt_run()

    
    while True:
        payload = create_heartbeat()
        sendpacket(payload)
        payload = createpacket_21(fake_pkt_21)
        sendpacket(payload)
        time.sleep(30)



## Close socket
UDPSock.close()
