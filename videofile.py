# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 09:45:25 2021

@author: OTTAA Bocho Team
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

class videoFile:
    
    def __init__(self, path, fps, reset = True, flipped = True):
        self.path = path
        self.reset_bool = reset
        
        print("Loading video file...")
        self.frame_array = self.load_frames(path, flipped)
        self.length = self.frame_array.shape[0]
        self.current_frame = 0
        self.current_frame_time = 0
        self.frame_rate = fps
        print("Video File Successfully Loaded!! It has", str(self.length), "frames")
        
    def load_frames(self, path, flipped):
        if self.path != path:
            self.path = path
        cap = cv2.VideoCapture(path)
        b = True
        array = None
        
        while b:
            b, frame = cap.read()
            
            if b:
                if flipped:
                    frame = cv2.flip(frame, 1) #video recordings are normally flipped by the software they are using, so we'll flip it again
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if array is None:
                    array = frame[np.newaxis, :, :]
                else:
                    array = np.append(array, frame[np.newaxis, :, :], axis = 0)
        
        cap.release()
        
        return array
    
    def next_frame(self, print_info = False):
        
        if self.current_frame >= self.length:
            if self.reset_bool:
                self.current_frame = 0
                if print_info:
                    print("- Video Reset -")
            else:
                self.current_frame = self.length - 1 #If reset_bool = False then the video stays on the last frame 
                if print_info:
                    print("- Video Ended -")
                    
        if print_info:
            print("Returning frame", str(self.current_frame+1), "out of", str(self.length))
        
        if (time.perf_counter() - self.current_frame_time) >= 1/self.frame_rate: #only when it overpass the fps time it will give another frame
            self.current_frame += 1 #So that the next self.next_frame goest to the next frame
            self.current_frame_time = time.perf_counter()
            return self.frame_array[self.current_frame - 1] #since we forwaded one frame, for the next one, we go one back, i believe this is the fastest way
        else:
            return self.frame_array[self.current_frame]
        
    def read(self): #Same function as next_frame to be called similar as the cap.read() from cv2
        return True, self.next_frame()
    
    def get(self, value): #redirects to cap.get so as to use our videoFile similarly as cv2.videoCapture
        return cv2.VideoCapture(self.path).get(value)
    
    def release(self): #since capture is released earlier, we don't need this command to do anything, but it's used for the normal videoCapture so we define it so as to use our videoFile similarly as cv2.videoCapture
        pass