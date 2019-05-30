'''
 Author : Mahfuz
 Date   : 11/17/2018
'''


import sys
import os
import cv2
import time
import math
import socket
import json
import threading
import numpy as np

#from darkflow.net.build import TFNet

import subprocess

###############################################

# Globals

###############################################

CUR_TIME = time.time()*1000.0
PREV_TIME = CUR_TIME

base_dir = 'gt/'
log_file_bsm = base_dir + 'data_bsm.txt'
log_file_psm = base_dir + 'data_psm.txt'
raw_imgs = base_dir + 'imgs/raw/test/'
annotated_imgs = base_dir + 'imgs/annotated/'

is_closed = False

##########################################

# Create a UDP/IP socket

##########################################

UDP_NUK_ETH = '169.254.115.100'
UDP_NUK_BCAST_PORT = 8989
bufsize = 8192

########################################

    

##########################################\

# Create Logs

##########################################

def clear_log():
    with open(log_file_bsm,'w') as f:
        print ('bsm log file cleared')
    with open(log_file_psm,'w') as f:
        print ('psm log file cleared')

def write_to_bsm_file(data):
    with open(log_file_bsm,'a') as f:
        f.write(data +  os.linesep)

def write_to_psm_file(data):
    with open(log_file_psm,'a') as f:
        f.write(data +  os.linesep)


clear_log()

#clear_imgs()

##########################################

# Create RX Thread

##########################################

def receiver():
    global CUR_TIME , is_closed
    try:
        sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sockr.bind(('',UDP_NUK_BCAST_PORT))
        print ('udp service started!')

        while (is_closed==False) :
            #print ('waitingg for data ...')
            data, from_  = sockr.recvfrom(bufsize)
            print (str(data))
            if(data == ''):
                print ('pipe broken')
                sockr.close()
                return
            else :
                start = time.time() * 1000.0
                jdata = json.loads(data)
                jdata['nuc_timestamp'] = start
                obu_time = int(jdata['timestamp'])
                rsu_time = int(jdata['rsu_timestamp'])
                CUR_TIME = obu_time
                write_to_bsm_file(str(jdata))
      
    except Exception as err:
        print ('exception in comm::receiver()'  , err)

        


################################################
# Create Video Cam Capture
################################################

cam = 1 # Use  local webcam.
capture = cv2.VideoCapture(cam)
colors = [tuple(255 * np.random.rand(3)) for i in range(5)]

################################################
# Main Thread
################################################

threading.Thread(target=receiver).start()

################################################

while (capture.isOpened()):
    #print('Stime :',stime)
    ret, frame = capture.read()
    #r_img = frame.copy()
    if ret:
        cv2.imshow('Frame', frame)

        if(CUR_TIME!=PREV_TIME):
            cv2.imwrite(raw_imgs + str(CUR_TIME) + '.jpg', frame)
            PREV_TIME = CUR_TIME
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_closed = True
            break
    else:
        capture.release()
        cv2.destroyAllWindows()
        is_closed = True
        break

capture.release()
cv2.destroyAllWindows()
is_closed = True
        
