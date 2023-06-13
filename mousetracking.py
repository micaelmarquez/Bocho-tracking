# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 10:52:41 2021

@author: Juanma
"""

from collections import deque
import mouse
import time

from flags import Flags, clickFlags
import operations

from pynput.keyboard import Key, KeyCode, Listener

mouse_coord = (0, 0)

history_deques_lenght = 20
var_threshold = 20
x_history = deque([], maxlen = history_deques_lenght)          
y_history = deque([], maxlen = history_deques_lenght)

autoclick_flag = clickFlags(counter_lowthresh = 20, counter_uppthresh = 20, counter_leap = 1, counter_uppbound = 50, count_ontrue = True, message = "Click!!!")
autoclick_setup_flag = Flags(init_flag = False)

def key_pressed(key):
    if key == KeyCode.from_char('c'):  
        autoclick_setup_flag.raise_flag()
        
listener = Listener(on_press=key_pressed)
listener.start()

# -- Main Loop --

try:
    while True:
        
        time.sleep(0.0333)
        mouse_coord = mouse.get_position()
        
        x_history.append(mouse_coord[0])
        y_history.append(mouse_coord[1])
            
        if operations.check_stillness(x_history, y_history, var_threshold):
            autoclick_flag.raise_flag()
        else:
            autoclick_flag.lower_flag()
            
        Flags.check_all()
        
        if autoclick_setup_flag.flag:
            autoclick_flag.setup()
            autoclick_setup_flag.lower_flag()
            
        
    listener.stop()
    
except KeyboardInterrupt:
    listener.stop()
    
except Exception as e:
    listener.stop()
    raise e

print(Flags.instance_list)