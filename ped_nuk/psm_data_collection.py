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
from darkflow.net.build import TFNet
import subprocess
###############################################
# Globals
###############################################
CUR_TIME = time.time()*1000.0

base_dir = 'gt/'
log_file_bsm = base_dir + 'data_bsm.txt'
log_file_psm = base_dir + 'data_psm.txt'
raw_imgs = base_dir + 'imgs/raw/'
annotated_imgs = base_dir + 'imgs/annotated/'

count = 0
x1=0
y1=0
t=0
Cx=0
Cy=0
Lx=0
Ly=0
speed=0
dist=0
##########################################
# Create a UDP/IP socket
##########################################
UDP_NUK_ETH = '169.254.115.255'
UDP_NUK_BCAST_PORT = 9999
bufsize = 8192



########################################
def udp_to_dsrc_psm(data):
    UDP_TO_DSRC = '169.254.115.221'
    UDP_TO_DSRC_PORT = 5555    
    udp_nuk_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # create udp socket
    udp_nuk_sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)   ### for enabling broadcast


    udp_nuk_sock.sendto(data,(UDP_TO_DSRC,UDP_TO_DSRC_PORT))
    print ('sending to dsrc...')
    
##########################################\
# Create Logs
##########################################
def clear_imgs():
    print ('clearing imgs')
    subprocess.call([r'gt\imgs\clear.bat'])
    print ('Imgs clean done!')
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
    global CUR_TIME
    try:
        sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sockr.bind(('',UDP_NUK_BCAST_PORT))
        print ('udp start service ...')

        while True :
            data, from_  = sockr.recvfrom(bufsize)
            #print 'message:'+ str(message)
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
        
###############################################
# Transformation Functions
###############################################
def pixeltogeo(cx,cy):
    global Lx, Ly
    Lx = 34.668316 +  (0.000027/800)*cx
    Ly = -82.826304 + (0.000043/1000)*cy

def get_speed(Time,Cx,Cy):
    global speed, dist

    d = ((x1-Cx)*(x1-Cx) + (y1-Cy)*(y1-Cy))
    dt = math.sqrt(d)
    dist = dt*(20/1680)
    
    time = (Time-t)
    if time > 0:
        speed = (dist/time)
    else:
        speed = 0
################################################
# Load TF Modules
################################################
option = {
    'model': 'cfg/yolo.cfg',
    'load': 'bin/yolov2.weights',
    'threshold': 0.40,
    'gpu': 1.0
}

tfnet = TFNet(option)
objects = ['person']

################################################
# Create Video Cam Capture
################################################
cam = 0 # Use  local webcam.
capture = cv2.VideoCapture(cam)
colors = [tuple(255 * np.random.rand(3)) for i in range(5)]

################################################
# Main Thread
################################################

threading.Thread(target=receiver).start()

while (capture.isOpened()):
    stime = time.time()
    #print('Stime :',stime)
    ret, frame = capture.read()
    r_img = frame.copy()
    if ret:
        pred_start_time  = time.time()
        results = tfnet.return_predict(frame)
        pred_end_time  = time.time()
        pred_time  = (pred_end_time - pred_start_time)*1000.0
        #print (results)
        for color, result in zip(colors, results):
            tl = (result['topleft']['x'], result['topleft']['y'])
            br = (result['bottomright']['x'], result['bottomright']['y'])
            label = result['label'] + ":" + str('%0.2f' %result['confidence'])
            if(result['label'] in objects ):

                cx = int((result['topleft']['x'] + result['bottomright']['x'] )/2.0)
                cy = int((result['topleft']['y'] + result['bottomright']['y'] )/2.0)
            
                frame = cv2.rectangle(frame, tl, br, (0,255,0), 4)
                frame = cv2.putText(frame, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                frame = cv2.circle(frame,(cx,cy), 4, (0,0,255), -1)
               
               
                cp_frame = frame.copy()
                
                get_speed(stime,cx,cy)
                pixeltogeo(cx,cy)
        
                x1 = cx
                y1 = cy
                t = stime
                
                data = {'id':count,
                        'obu_timestamp' : CUR_TIME,
                        'nuc_timestamp' : t,
                        'object':label,
                        'xpixel-cordinate':cx,
                        'ypixel-coordinate':cy,
                        'latitude':Lx,
                        'longitude':Ly,
                        'prediction_time':pred_time,
                        'distance':dist,
                        'speed':speed}
                #print (data)

                write_to_psm_file(str(data))
                message=json.dumps(data)
                udp_to_dsrc_psm(str(message).encode())

                cv2.imwrite(annotated_imgs + str(CUR_TIME) + '.jpg',frame)
                cv2.imwrite(raw_imgs + str(CUR_TIME) + '.jpg',r_img)
                
        cv2.imshow('rgb',frame)
        

        print ('frame id : \t' , count )
        count+=1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
                
    else:
        capture.release()
        cv2.destroyAllWindows()
        
        break


   
