
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 09:46:08 2021

@author: OTTAA Bocho Team
"""

# -- Modules Import --
from roi import videoROI
from flags import Flags, clickFlags, funBar
import operations

# -- Libraries Import --
import cv2
import mouse

import statistics 

import numpy as np
from collections import deque

import time

from pynput.keyboard import Key, KeyCode, Listener

import autopy

# -- Setup --

#Screen Params       
wScr, hScr = autopy.screen.size()
print(wScr, hScr)

#Capture Params
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10001)
#print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#Base ROI Params

base_width = 640
base_height = 360

baseROI = videoROI(show_warnings = True)
baseROI.set_coord([cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2 - base_width/2, cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2 - base_height/2])
baseROI.set_size([base_width, base_height])

baseROI.showing_state()

show_roi_flag = Flags(init_flag = True, disables_tracking = True)
show_processed_flag = Flags(init_flag = False)

#Mouse Params
mouse_coord = (0, 0)
cent_coord = (0, 0)
prev_cent_coord = (0, 0)

absolute_movement_flag = Flags(init_flag = True)

#Smoothing params
min_smoothing = 2
max_smoothing = 16 
smoothing_points = 10
smoothing_high_range = 4

cicles_counter = 0

#Sensibility Params
min_sensibility = 1
max_sensibility = 11  #Should be defined once the new BOCHO webcam is available
sensibility_points = 10
sensibility = min_sensibility

sensibility_change_flag = Flags(init_flag = True)

sensibilityROI = videoROI()

# Mouse history Params 
history_deques_lenght = 100
min_history_deques_lenght = 10 #Used to define the minimum lenght from which the deque is used.
x_history = deque([], maxlen = history_deques_lenght)          
y_history = deque([], maxlen = history_deques_lenght)

#Auto-Click Params  
var_threshold = 10 #threshold beyond which the mouse is considered still. the smaller this threshold, the smaller distances the mouse can recognize (for clicking)
counter_for_click = 5 #starts counting when the mouse is considered still, when it reaches the chosen value it cicks

autoclick_flag = clickFlags(counter_lowthresh = counter_for_click, counter_uppthresh = counter_for_click, counter_leap = 1, counter_uppbound = counter_for_click+1, count_ontrue = True, message = "Click!")
autoclick_setup_flag = Flags(init_flag = False)

#Alarm Params
no_source_flag = Flags(message = "Can't get source of image", disables_tracking = True)
no_reflex_flag = Flags(counter_lowthresh = 40, counter_leap = 1, counter_uppbound = 50, message = "Can't detect reflex point")
brightness_flag = Flags(counter_lowthresh = 40, counter_leap = 1, counter_uppbound = 50, message = "Too much brightness in the background", disables_tracking = True)
multi_reflex_flag = Flags(counter_lowthresh = 40, counter_leap = 1, counter_uppbound = 50, message = "There are too many reflective stickers", disables_tracking = True)

#Keyboard Setup Params
def key_pressed(key):
    global sensibility
    global smoothing_high_range

    if key == KeyCode.from_char('\x01'):  #Toggle between absolute and relative modes, ctrl+a
        absolute_movement_flag.change_flag_state()
    elif key == KeyCode.from_char('\x1a'): #Toggle between showing and not showing camera image, ctrl+z
        show_roi_flag.change_flag_state()
    elif key == KeyCode.from_char('\x14'): #Toggle between showing processed or unprocessed image from camera, ctrl+t
        show_processed_flag.change_flag_state()
    elif key == Key.up:  #Raises sensibility value
        sensibility = min(sensibility+(max_sensibility-min_sensibility)/sensibility_points, max_sensibility) 
        sensibility_change_flag.raise_flag()
        print("Sensibility is", sensibility)
    elif key == Key.down: #Lowers sensibility value
        sensibility = max(sensibility-(max_sensibility-min_sensibility)/sensibility_points, min_sensibility)
        sensibility_change_flag.raise_flag()
        print("Sensibility is", sensibility)
    elif key == Key.right: #Raises Smoothing
        smoothing_high_range = min(smoothing_high_range +(max_smoothing-min_smoothing)/smoothing_points, max_smoothing)
        print("Smoothing_high_range is", smoothing_high_range)
    elif key == Key.left: #Lowers Smoothing
        smoothing_high_range = max(smoothing_high_range-(max_smoothing-min_smoothing)/smoothing_points, min_smoothing)
        print("Smoothing_high_range is", smoothing_high_range)
        
listener = Listener(on_press=key_pressed)
listener.start()

#------------------------ Function Bar -------------------------------------

l_fbar = funBar(init_flag = True, val = 0, leap = 1, flag = False )
r_fbar = funBar(init_flag = True, val = 0, leap = 1, flag = False )
ml_fbar = funBar(init_flag = True, val = 0, leap = 1, flag = False )
mr_fbar = funBar(init_flag = True, val = 0, leap = 1, flag = False )


def open_fun_bar(posic):

    background = np.zeros((100,60,3))
    background[0::, 0:14] = 255
    background[0::, 31:45] = 255
    if posic == 0:  
        background[0::, 0:14] = 255
        background[0::, 31:45] = 255
        
    if posic == 1:
        background[25:75,4:12] = 0       
    if posic == 2:
        background[25:75,19:27] = 255       
    if posic == 3:
        background[25:75,34:42] = 0               
    if posic == 4:
        background[25:75,49:57] = 255

    func_bar = cv2.namedWindow('Function bar', cv2.WINDOW_NORMAL)
    cv2.imshow('Function bar', background)
    func_bar = cv2.resizeWindow('Function bar', 100, 50)
    func_bar = cv2.moveWindow('Function bar', 1, 700)   
    cv2.setWindowProperty('Function bar', cv2.WND_PROP_TOPMOST, 1)  # Give the funbar window 
                                                                    # TOPMOST priority


def fun_bar_event(event, x, y, flags, params):
    #tal vez se podría hacer que el bajar las banderas se haga en 1 renglón usando clases, 
    #pero mi destreza programando es limitada jeje lo veo otro día.
    
    if x < 15:  # if the X-coord in function bar is lower than 16, then 
        l_fbar.increment()
        r_fbar.lower_flag()
        ml_fbar.lower_flag()
        mr_fbar.lower_flag()
        
        if l_fbar.flag: #if the flag is UP, activate double left click.
            open_fun_bar(1)
            autoclick_flag.set_button_and_type("left", "double_click")
            
    if (15 < x < 30):  # if the X-coord in function bar is between the given range, then:
        ml_fbar.increment()
        r_fbar.lower_flag()
        mr_fbar.lower_flag()
        l_fbar.lower_flag()
        
        if ml_fbar.flag: #is the flag is UP, activate simple left click
            open_fun_bar(2)
            autoclick_flag.set_button_and_type("left", "simple_click")  

    if (30 < x < 45):   #if the X-coord in function bar is higher than 33, then:
        mr_fbar.increment()
        l_fbar.lower_flag() 
        ml_fbar.lower_flag()
        r_fbar.lower_flag()
        
        if mr_fbar.flag:  #if the flag is up, disable both clicks.
            open_fun_bar(3)
            autoclick_flag.set_button_and_type("left", "None")
            autoclick_flag.set_button_and_type("right", "simple_click")
            
    if x > 45:   #if the X-coord in function bar is higher than 33, then:
        r_fbar.increment()
        l_fbar.lower_flag()
        ml_fbar.lower_flag()
        mr_fbar.lower_flag()        
        
        if r_fbar.flag:  #if the flag is up, disable both clicks.
            open_fun_bar(4)
            autoclick_flag.set_button_and_type("left", "None")
            autoclick_flag.set_button_and_type("right","None")
# ---------------------- End of Function Bar ------------------------------    
    
# ---------     Main Loop       ----------------

try:
    while True:
        
        #start = time.perf_counter() #Uncomment for FPS
        
        ret, frame = cap.read()
        
        #Image Processing
        processed_frame = operations.preprocess_image(frame, crop_corners = baseROI.get_corners(), threshold = 200)
        
        #Tracking
        cent_coord = operations.detect_centroid(processed_frame, prev_cent_coord)
        
        #Smoothing
        smoothing = operations.variance_smoothing(x_history,y_history,smoothing_high_range,min_smoothing, wScr, hScr)
        cent_coord = tuple([prev+(now-prev)/smoothing for prev, now in zip(prev_cent_coord, cent_coord)])
        rel_coord = [now-prev for prev, now in zip(prev_cent_coord, cent_coord)]
        prev_cent_coord = tuple(cent_coord)
        
        #Interpolation
        if sensibility_change_flag.flag:
            operations.apply_sensibility_roi(baseROI, sensibilityROI, [sensibility, sensibility])
            sensibility_change_flag.lower_flag()
            base_coord = baseROI.get_coord()
            interp_x = [s-base_coord[0] for s in sensibilityROI.get_xcorners()]
            interp_y = [s-base_coord[1] for s in sensibilityROI.get_ycorners()]
           
        if ret and not Flags.disable_tracking():
            #Mouse Movement: Nota a tener en cuenta: wScr y hScr antes eran screen_width y height. Ahora está automatizado.
            scaled_moves = operations.movement_scaling(cent_coord, rel_coord, (wScr, hScr), interp_x, interp_y, baseROI.get_size(), [sensibility, sensibility], absolute = absolute_movement_flag.flag)
            #scaled_moves = [np.interp(cent, interp, (0,screen)) for cent, interp, screen in zip(cent_coord, [interp_x, interp_y], [screen_width, screen_height])]

            mouse.move(scaled_moves[0], scaled_moves[1], absolute=absolute_movement_flag.flag, duration=0)
            
            # Reopen the window in case it's been closed. 

            if not cv2.getWindowProperty('Function bar', cv2.WND_PROP_VISIBLE):
                open_fun_bar(0) 
                cv2.setMouseCallback('Function bar', fun_bar_event, scaled_moves)
            
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
                
        # If NOT tracking, close the function bar window       
        if Flags.disable_tracking():
            cv2.destroyWindow('Function bar')
            
        Flags.check_all()
        
        #ROI WINDOW MANAGING
        if show_roi_flag.flag:
            if cv2.getWindowProperty('frame', 0) < 0: #open window if closed
                cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
                
            if not no_source_flag.flag:
                if show_processed_flag.flag:
                    frame = np.zeros(frame.shape, dtype=np.uint8)
                    x, y, x_trans, y_trans = baseROI.get_corners()
                    for d in range(frame.shape[-1]):
                        frame[y:y_trans, x:x_trans, d] = processed_frame
                    frame[int(y + cent_coord[1]-5): int(y + cent_coord[1]+6), int(x+cent_coord[0]-5):int(x+cent_coord[0]+6), :] = [0,0,255]
                else:
                    frame = cv2.flip(frame, 1)
                cv2.resizeWindow('frame', frame.shape[1], frame.shape[0])
                if baseROI.is_fixed:
                    frame = baseROI.draw_roi_onframe(frame, (10, 150, 220))
                    frame = sensibilityROI.draw_roi_onframe(frame, (255,255,10))
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
