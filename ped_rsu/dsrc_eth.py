import socket
import json
import time
import threading
import Watcher as watch

UDP_IP_DSRC = "192.168.234.255"
UDP_BCAST_PORT=8888
bufsize = 8192 # Modify to suit your needs

UDP_NUK_ETH = '169.254.115.200'
UDP_NUK_BCAST_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_nuk_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # create udp socket
udp_nuk_sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)   ### for enabling broadcast
  
def broadcast(data):
    #print ('sending data over the udp nuk')
    udp_nuk_sock.sendto(data,(UDP_NUK_ETH,UDP_NUK_BCAST_PORT))
    #my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #my_socket.connect((TCP_IP, TCP_PORT))
    #my_socket.send(data)
    #print 'Data sent through eth'

def dsrc_transmiter():
    try:
        sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sockr.bind(('',5555))
        print ('start service ...')

        while True:
            message, from_dev = sockr.recvfrom(bufsize) 
            print ('psm message:'+ str(message))
    except Exception as err:
        print('Error in psm rx')
######################################################################
def receiver():
    try:
        sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sockr.bind(('',UDP_BCAST_PORT))
        print ('start service ...')

        while True :
            message, from_  = sockr.recvfrom(bufsize)
            #print 'message:'+ str(message)
            if(message == ''):
                print ('pipe broken')
                sockr.close()
                return
            else :
                print (str(message))
                start  = int(time.time()*1000.0)
                jdata = json.loads(str(message))
                jdata['rsu_timestamp'] = start
                end = jdata['timestamp']
                
                print ('time dif :  ' , (start-end) , ' ms')
                #pass
                broadcast(json.dumps(jdata))
				#pass				
    #print ('message from :'+ str(address[0]) , message)
    except Exception as err:
        print 'exception in comm::receiver()'  , err
                
if __name__ == "__main__" :
    watch.Watcher()
    threading.Thread(target=dsrc_transmiter).start()
    receiver()
