# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 09:46:15 2021

@author: OTTAA Bocho Team
"""

#FLAG CLASS

import mouse 

class Flags:
    
    instance_list = []
    
    def __init__(self, init_flag = False, 
                 init_counter = 0, counter_lowthresh = 0, counter_uppthresh = float('inf'), 
                 counter_leap = 0, counter_lowbound = 0, counter_uppbound =  float('inf'),
                 reset_onfalse = True, count_ontrue = False,
                 disables_tracking = False,
                 message = "", 
                 action = None):
        
        self.flag = init_flag #Flag boolean, True means flag is raised and False means flag is lowered
        
        self.counter = init_counter                #Flag counter, adds up values when flag is raised, reset or counts down when lowered
        self.counter_lowthresh = counter_lowthresh #Lower threshold for counter to activate
        self.counter_uppthresh = counter_uppthresh #Upper threshold for counter to be active
        self.counter_leap = counter_leap           #amount to add up on every loop if flag is raised
        self.counter_lowbound = counter_lowbound   #least value the counter can have
        self.counter_uppbound = counter_uppbound   #highest value the counter can have
        self.reset_onfalse = reset_onfalse         #wether to reset or just discount the counter when the flag is lowered
        self.count_ontrue = count_ontrue           #wether to keep counting or not once the flag reached the active state
        
        self.disables_tracking = disables_tracking   # wether or not the raised flag disables the tracking of the mouse
        
        self.has_message = (message != "") #if the flag has a message asssociated when raised
        self.message = message #flag raised message
        
        self.has_action = not action is None #if the flag has an action associated when raised
        self.action = action #flag raised action
        self.action_return = None #flag action returned value
        
        if self not in Flags.instance_list:
            Flags.instance_list.append(self)
            
    def change_flag_state(self):
        self.flag = not self.flag
        
    def raise_flag(self):
        if not self.flag:
            self.flag = True
        
    def lower_flag(self):
        if self.flag:
            self.flag = False
        
    def add_counter(self, leap = 1):
        if self.counter < self.counter_uppbound:
            self.counter += leap
        
    def sub_counter(self, leap = 1):
        if self.counter > self.counter_lowbound:
            self.counter -= leap
        
    def set_counter(self, value = 0):
        self.counter = value
        
    def set_counter_thresh(self, lowthresh = 0, uppthresh = float('inf')):
        self.counter_lowthresh = lowthresh
        self.counter_uppthresh = uppthresh
        
    def set_message(self, message):
        self.has_message = (message != "")
        self.message = message
        
    def erase_message(self):
        self.set_message("")
        
    def set_action(self, function):
        self.has_action = not (function is None)
        self.action = function
        
    def erase_action(self):
        self.set_action(None)
        
    def check(self):
        if self.flag:
            if self.counter >= self.counter_lowthresh and self.counter <= self.counter_uppthresh:
                self.act()
                if self.count_ontrue:
                    self.add_counter(self.counter_leap)
            else:
                self.add_counter(self.counter_leap)
        
        else:
            if self.reset_onfalse:
                self.set_counter(0)
            else:
                self.sub_counter(self.counter_leap)
                
    def act(self):
        if self.has_message:
            #pass
            print(self.message)
        if self.has_action:
            self.action_return = self.action()
                
    @classmethod
    def check_all(cls):
        for instance in cls.instance_list:
            instance.check()
            
    @classmethod
    def disable_tracking(cls):
        return any([F.flag for F in cls.instance_list if F.disables_tracking == True])
    

# CLICK FLAG CLASS

class clickFlags(Flags):
    
    def __init__(self, init_flag = False, 
                 init_counter = 0, counter_lowthresh = 0, counter_uppthresh = float('inf'), 
                 counter_leap = 0, counter_lowbound = 0, counter_uppbound =  float('inf'),
                 reset_onfalse = True, count_ontrue = False,
                 disables_tracking = False,
                 message = "", 
                 action = None):
        
        super().__init__(init_flag, init_counter, counter_lowthresh, counter_uppthresh, 
                 counter_leap, counter_lowbound, counter_uppbound,
                 reset_onfalse, count_ontrue, disables_tracking,
                 message, action)
        
        self.available_buttons = ["left", "middle", "right"]
        self.button = "left"
        self.type = {"simple_click": False,
                    "double_click": False,
                    "click_and_drag": False}
        
    def set_button(self, new_button):
        
        if new_button in self.available_buttons:
            self.button = new_button
        else:
            raise ValueError("That is not a valid button!")
            
    def change_button_toleft(self):
        self.button = "left"
        
    def change_button_tomiddle(self):
        self.button = "middle"
        
    def change_button_toright(self):
        self.button = "right"
        
    def set_type(self, type):
        for k in self.type:
            if k == type:
                self.type[k] = True
            else:
                self.type[k] = False

    def set_button_and_type(self, button, type):
        self.set_button(button)
        self.set_type(type)

    def set_type_and_button(self, type, button):
        self.set_type(type)
        self.set_button(button)
 
    def set_simple_click(self):
        self.set_type("simple_click")
        
    def set_double_click(self):
        self.set_type("double_click")
        
    def set_click_and_drag(self):
        self.set_type("click_and_drag")
        
    def setup(self):
        
        print("---------------------------\n Set click button:")
        
        for n, b in enumerate(self.available_buttons):
            print(n,": ",b,"\n")
            
        self.set_button(self.available_buttons[int(input(n))])
        
        print("---------------------------\n Set click type:")
        
        for n, k in enumerate(self.type):
            print(n,": ",k,"\n")
        print(n+1,": ", "None")
            
        self.set_type((list(self.type)+[" "])[int(input(n))])
        
    def click_event(self): 
        if self.type["simple_click"]:
            mouse.click(self.button)
        if self.type["double_click"]:
            mouse.double_click(self.button)
        if self.type["click_and_drag"]: 
            if mouse.is_pressed(self.button):
                mouse.release(self.button)
            else:
                mouse.press(self.button)
                
    def act(self):
        super().act()
        self.click_event()


class funBar:
    
    def __init__(self, init_flag = False, val = 0, leap = 1, flag = False, mode = (0,0,0,0), position = 0):
                
        self.init_flag = init_flag
        self.val = val
        self.leap = leap
        self.flag = flag
    
    
    def increment(self):
        self.val += self.leap
        if self.val > 19 and self.flag == False:
            self.flag = True
        if self.flag:
            self.val = 0
            
    def lower_flag(self):
        self.flag = False


        
        
        
            
            
    
            
        
        
        
        
        
        
        