# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 09:46:08 2021

@author: OTTAA Bocho Team
"""

# -- Modules Import --
from roi import videoROI
from flags import Flags, clickFlags
from videofile import videoFile
import operations

# -- Libraries Import --
import cv2
import mouse

import numpy as np
from collections import deque

import time

from pynput.keyboard import Key, KeyCode, Listener
#import pandas as pd

# -- Setup --

#Screen Params
screen_width = 1920
screen_height = 1080

#Capture Params
cap = videoFile("./sample.mp4", fps = 60)

#Zoom ROI Params
zoomROI = videoROI()
zoomROI.set_roi_ratio(screen_width/screen_height)
zoomROI.set_image_size((cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

zoomed_width = 640
zoomed_height = 360

create_zoom_flag = Flags(init_flag = True, message = "Set zoom ROI", disables_tracking = True)

#Mouse Params
mouse_coord = (0, 0)
cent_coord = (0, 0)
prev_cent_coord = (0, 0)

absolute_movement_flag = Flags(init_flag = True)

sensibility = (1,1)

#Auto-Click Params

history_deques_lenght = 10
var_threshold = 20
x_history = deque([], maxlen = history_deques_lenght)          
y_history = deque([], maxlen = history_deques_lenght)

autoclick_flag = clickFlags(counter_lowthresh = 20, counter_uppthresh = 20, counter_leap = 1, counter_uppbound = 50, count_ontrue = True, message = "Click!!!")
autoclick_setup_flag = Flags(init_flag = False)

#Alarm Params
no_source_flag = Flags(message = "Can't get source of image", disables_tracking = True)
no_reflex_flag = Flags(counter_lowthresh = 40, counter_leap = 1, counter_uppbound = 50, message = "Can't detect reflex point")
brightness_flag = Flags(counter_lowthresh = 40, counter_leap = 1, counter_uppbound = 50, message = "Too much brightness in the background", disables_tracking = True)
multi_reflex_flag = Flags(counter_lowthresh = 40, counter_leap = 1, counter_uppbound = 50, message = "There are too many reflective stickers", disables_tracking = True)

image_props_flag = Flags(init_flag = False)

#Keyboard Setup Params
def key_pressed(key):
    global sensibility
    sensibilities = np.arange(1,6)
    sensibilities_bool = [key == KeyCode.from_char(str(s)) for s in sensibilities]
    if key == KeyCode.from_char('a'):
        absolute_movement_flag.change_flag_state()
    elif key == KeyCode.from_char('z'):
        create_zoom_flag.change_flag_state()
        zoomROI.hidden_state()
    elif key == KeyCode.from_char('r'):
        image_props_flag.change_flag_state()  
    elif key == KeyCode.from_char('c'):  
        autoclick_setup_flag.raise_flag()
    elif any(sensibilities_bool):
        print("Sensibility set to ", sensibilities[sensibilities_bool][0])
        sensibility = (0.2*sensibilities[sensibilities_bool][0], 0.2*sensibilities[sensibilities_bool][0])
        
listener = Listener(on_press=key_pressed)
listener.start()

# -- Main Loop --

try:
    while True:
        
        #start = time.perf_counter() #Uncomment for FPS
        
        ret, frame = cap.read()
        
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)#is easier to read videoFiles in grayscale, so for the processing we triplicate it
        
        if ret and not Flags.disable_tracking():
            
            #Tracking
            processed_frame = operations.preprocess_image(frame, crop_corners = zoomROI.get_corners(), threshold = 230, apply_image_props = image_props_flag.flag)
            zoomed_frame = operations.zoom_image(processed_frame, expected_size = (zoomed_width, zoomed_height))
            
            cent_coord = operations.detect_centroid(zoomed_frame)
            cent_moves = [(c1-c0*int(not absolute_movement_flag.flag)) for c1,c0 in zip(cent_coord, prev_cent_coord)] #List comprehension to switch between absolute and relative movement
            prev_cent_coord = cent_coord
            scaled_moves = operations.movement_scaling(cent_moves, (screen_width, screen_height), (zoomed_frame.shape[1], zoomed_frame.shape[0]), sensibility = sensibility, absolute = absolute_movement_flag.flag)
            mouse.move(scaled_moves[0], scaled_moves[1], absolute=absolute_movement_flag.flag)
            
            if absolute_movement_flag.flag:
                mouse_coord = scaled_moves
            else:
                mouse_coord = mouse.get_position()
        
            x_history.append(mouse_coord[0])
            y_history.append(mouse_coord[1])
            
            if operations.check_stillness(x_history, y_history, var_threshold):
                autoclick_flag.raise_flag()
            else:
                autoclick_flag.lower_flag()
        
        Flags.check_all()
        
        #zoomROI window Managing
        if create_zoom_flag.flag:
            if zoomROI.is_active:
                cv2.setMouseCallback('frame', zoomROI.on_mouserelease)
            else:
                cv2.setMouseCallback('frame', zoomROI.on_mousepress)
                
            if cv2.getWindowProperty('frame', 0) < 0: #open window if closed
                cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            
            if not no_source_flag.flag:
                cv2.resizeWindow('frame', frame.shape[1], frame.shape[0])
                frame = cv2.flip(frame, 1)
                if zoomROI.is_fixed:
                    frame = zoomROI.draw_roi_onframe(frame)
                cv2.imshow('frame', frame)    
        else:
            cv2.setMouseCallback('frame', lambda *args : None) #so it doesn't do anything when set zoom is inactive
            
            if cv2.getWindowProperty('frame', 0) >= 0: #destroy window if open
                cv2.destroyWindow('frame')
        
        #The waitKey is necessary for the image to be shown, seems like OpenCV prevents you from opening the window without a key associated to close it
        if cv2.waitKey(1) & 0xFF == ord('q'):             
            break
            
        if autoclick_setup_flag.flag:
            autoclick_flag.setup()
            autoclick_setup_flag.lower_flag()
        
        #cv2.setWindowTitle('frame', str(1/(time.perf_counter()-start)) + " FPS") #Uncomment for FPS
        #!cls #a way to clear the screen, not too effective, would recommend another method
    cap.release()
    cv2.destroyAllWindows()
    listener.stop()
    
except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
    listener.stop()
    
except Exception as e:
    cap.release()
    cv2.destroyAllWindows()
    listener.stop()
    raise e        
