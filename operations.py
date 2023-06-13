# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 15:18:08 2021

@author: OTTAA Bocho Team
"""

import cv2
import mouse

from skimage import io, measure, img_as_ubyte

import pandas as pd
import numpy as np
import statistics

def preprocess_image(image, crop_corners, threshold = 230):
    
    image = image[crop_corners[1]:crop_corners[3], crop_corners[0]:crop_corners[2]]
    
    proc_image = cv2.flip(image, 1)
    proc_image = cv2.cvtColor(proc_image, cv2.COLOR_BGR2GRAY)
    #ret, proc_image = cv2.threshold(proc_image, threshold, 255, cv2.THRESH_OTSU)
    proc_image = cv2.GaussianBlur(proc_image, (5,5), 0)
    ret, proc_image = cv2.threshold(proc_image, threshold, 255, cv2.THRESH_TOZERO)
    ret, proc_image = cv2.threshold(proc_image, 255, 255, cv2.THRESH_TOZERO_INV)
            
    return proc_image

def zoom_image(image, expected_size):
    current_size = image.shape[::-1] #since shape gives (rows, columns) and image sizes are measured (width, height)
    if current_size[0] < expected_size[0] or current_size[1] < expected_size[1]:
        return cv2.resize(image, (expected_size[0],expected_size[1]))
    return image

def detect_centroid(image, prev_cent):
    M = cv2.moments(image)
    if M["m00"] != 0:
        cX = M["m10"] / M["m00"]
        cY = M["m01"] / M["m00"]
    else:
        cX, cY = prev_cent
    
    return cX,cY
    
def movement_scaling(original, rel_original, screen_dim, interp_x, interp_y, roi_size, sensibility, absolute = True):
    scaled = []
    if absolute:
        interp = [interp_x, interp_y]
        return movement_scaling_absolute(original, screen_dim, interp)
    else:
        return movement_scaling_relative(rel_original, screen_dim, roi_size, sensibility)

def movement_scaling_absolute(original, screen_dim, interp):
    return [int(np.interp(original[axis], interp[axis], (0, screen_dim[axis]))) for axis in range(2)]

def movement_scaling_relative(original, screen_dim, roi_size, sensibility):
    return [int(screen_dim[axis]*np.tanh(sensibility[axis]*original[axis]/roi_size[axis])) for axis in range(2)] #the formula was screen_dim*tanh(sensibility*scaling*original/screen_dim) where scaling was screen_dim/roi_size

def check_stillness(x_hist, y_hist, var_thresh):
    if len(x_hist) == x_hist.maxlen and len(y_hist) == y_hist.maxlen:
        return all([mean_and_var(hist, 8 , 1)[1] < var_thresh for hist in [x_hist, y_hist]])  # It is prefer not to change the arguments of the mean_and_var function, instead if needed, change the values ​​of var_threshold and counter_for_click in main
    
def apply_sensibility_roi(original_roi, new_roi, sensibility):
    new_roi.set_size([o_dim/sens for sens, o_dim in zip(sensibility, original_roi.get_size())])
    
    new_roi.set_coord([o_corner + o_dim/2 - n_dim/2 for o_corner, o_dim, n_dim in zip(original_roi.get_coord(), original_roi.get_size(), new_roi.get_size())])
    
    return new_roi

# ---------     Mean and var operation       ----------------  
            
def mean_and_var(deque, quant, leap):
    start_point = -((quant-1)*leap+1) 
    history = (list(deque)[start_point::leap])
    
    if (abs(start_point) > len(deque)):
        print ("Error, the desired start point of the deque is bigger than the size of the deque") 
        new_variance = 0
        new_mean = 0
    else:
        new_mean = statistics.mean(history)  
        new_variance = statistics.variance(history, new_mean)
        
    return new_mean, new_variance

# ------- Smoothing with variance --------------     

def variance_smoothing(x_hist, y_hist, smoothing_high_range,min_smoothing, width, height):
    
    screen_size = width*height 
    min_cte_var = 5/(1366*768) #5 and 9 are the min and max var values that worked well on a 1366x768 pc. Divide those numbers by that resolution and then multiply it for the current screen size in order to extraplate those values to all resolutions
    max_cte_var = 9/(1366*768)
      
    min_var = min_cte_var * screen_size  
    max_var = max_cte_var * screen_size 
    
    if len(x_hist) == x_hist.maxlen and len(y_hist) == y_hist.maxlen:
        var_module = pow(pow((mean_and_var(x_hist, 5 , 1)[1]),2)+ pow((mean_and_var(y_hist, 5 , 1)[1]),2), 0.5) 
        smoothing = np.interp(var_module, [min_var, max_var], [smoothing_high_range, min_smoothing])
    else: 
        smoothing = min_smoothing
    return smoothing
        

# -----------------------------------------------------------

if __name__ == "__main__":
    pass