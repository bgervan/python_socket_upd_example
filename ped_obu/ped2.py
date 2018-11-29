# python code for test1 
# uses gpsd and json python libs
# udp client for data sending


import os
from gps import *
from time import *
import time
import threading
import socket
import json

UDP_IP = "192.168.234.255"
UDP_PORT=8888
carid=02
teststring= "test1"

pckcnt=0

gpsd = None #seting the global variable
 
os.system('clear') #clear the terminal (optional)
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # create udp socket
  sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)   ### for enabling broadcast

  message="" #empty string 
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
      #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc
 
      os.system('clear')
 
      print
      print ' GPS reading'
      print '----------------------------------------'
      print 'latitude    ' , gpsd.fix.latitude
      print 'longitude   ' , gpsd.fix.longitude
      print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
      #print 'altitude (m)' , gpsd.fix.altitude
      #print 'eps         ' , gpsd.fix.eps
      #print 'epx         ' , gpsd.fix.epx
      #print 'epv         ' , gpsd.fix.epv
      #print 'ept         ' , gpsd.fix.ept
      print 'speed (m/s) ' , gpsd.fix.speed 
      #print 'climb       ' , gpsd.fix.climb
      #print 'track       ' , gpsd.fix.track
      #print 'mode        ' , gpsd.fix.mode
      print
      #print 'sats        ' , gpsd.satellites
      # send packet through udp
      #message +=  "\'" +"{" + """carid:""" + str(carid) + "," + """seq:""" + str(pckcnt) + "," + str(gpsd.fix.latitude) + "," + str(gpsd.fix.longitude) + "," + str(gpsd.fix.speed) + "}"
      ts = long(time.time() * 1000.0) 
      msg_py = {'pedid':carid,'seq':pckcnt,'timestamp':ts,'latitude':gpsd.fix.latitude,'longitude':gpsd.fix.longitude,'speed':gpsd.fix.speed * 2.237,}  
      message=json.dumps(msg_py)    
      test = json.loads(message) 
      sock.sendto(message, (UDP_IP,UDP_PORT))

      print type(gpsd.fix.time)
      print msg_py
      print message
      print test
      print
      message = "" #empty message	
      pckcnt = pckcnt +1 	
      time.sleep(0.1) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."



