# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 11:32:12 2021

@author: OTTAA Bocho Team
"""

import cv2

class videoROI:
    
    def __init__(self, show_warnings = False):
        self.is_active = False #boolean to recognize an active ROI, meaning a ROI that is being drawn
        self.is_fixed = False
        self.origin = "upper-left"
        self.coord = (0, 0)
        self.size = (0, 0)
        self.image_size = None
        self.roi_ratio = None
        
        self.show_warnings = show_warnings
    
    def drawing_state(self):
        self.is_active = True
        self.is_fixed = True
        
    def showing_state(self):
        self.is_active = False
        self.is_fixed = True
        
    def hidden_state(self):
        self.is_active = False
        self.is_fixed = False
    
    def set_coord(self, new_coord):
        if new_coord is not list:
            new_coord = [new_coord[0], new_coord[1]]

        if self.image_size is not None:
            new_coord[0] = min(new_coord[0], self.image_size[0])
            new_coord[0] = int(max(new_coord[0], 0))
            new_coord[1] = min(new_coord[1], self.image_size[1])
            new_coord[1] = int(max(new_coord[1], 0))
        else:
            new_coord[0] = int(new_coord[0])
            new_coord[1] = int(new_coord[1])
            if self.show_warnings:
                print("Warning: ROI is not limited by an image size because image size is not set.")
        
        self.coord = tuple(new_coord)
        
    def set_size(self, new_size):
        if new_size is not list:
            new_size = [new_size[0], new_size[1]] #Still have to add validation of tuple size too
           
        if self.image_size is not None:
            new_size[0] = min(new_size[0], self.image_size[0]-self.coord[0])
            new_size[0] = int(max(new_size[0], 0))
            new_size[1] = min(new_size[1], self.image_size[1]-self.coord[1])
            new_size[1] = int(max(new_size[1], 0))
        else:
            if self.show_warnings:
                print("Warning: ROI is not limited by an image size because image size is not set.")
            
        if self.roi_ratio is not None:
            if new_size[0] != 0 and new_size[1] != 0:
                if round(new_size[0] / new_size[1], 2) != round(self.roi_ratio, 2):
                    new_size = [int(new_size[0]), int(new_size[0]/self.roi_ratio)]                          
        else:
            new_size[0] = int(new_size[0])
            new_size[1] = int(new_size[1])
            if self.show_warnings:
                print("Warning: the ROI size is not fixed to an specific ratio.")
        
        self.size = tuple(new_size)
    
    def set_size_from_coord(self, new_coord):
        x_size = new_coord[0] - self.get_coord()[0]
        y_size = new_coord[1] - self.get_coord()[1]
        
        self.set_size((x_size, y_size))
                            
    def set_roi_ratio(self, ratio):
        if ratio <= 0:
            raise ValueError("Ratio must be higher than cero")
        else:
            self.roi_ratio = ratio
    
    def set_image_size(self, size):
        if any([side <= 0 for side in size]):
            raise ValueError("One or both sides of the image size is null or negative")
        else:
            self.image_size = size
            self.size = size #If image_size is set, the initial size of the ROI is image_size
        
    def get_coord(self):
        return self.coord
    
    def get_size(self):
        return self.size
    
    def get_corners(self): #returns upper left and lowe right corner coordinates
        x, y = self.coord
        x_trans, y_trans = x + self.size[0], y + self.size[1]
        return x, y, x_trans, y_trans

    def get_xcorners(self):
        corners = self.get_corners()
        return corners[0], corners[2]
        
    def get_ycorners(self):
        corners = self.get_corners()
        return corners[1], corners[3]
    
    def draw_roi_onframe(self, frame, color = (255, 255, 255), show_dims = False):
        x, y, x_trans, y_trans = self.get_corners()
        rSize = self.get_size()
        tSize = cv2.getTextSize(str((x, y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, None)[0]
        
        if show_dims:
            cv2.putText(frame, str((x, y)), (x-tSize[0], y+tSize[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color)
        
        cv2.line(frame, (x, y), (x_trans, y), color, 2, cv2.LINE_4)
        cv2.line(frame, (x, y), (x, y_trans), color, 2, cv2.LINE_4)
        cv2.line(frame, (x_trans, y), (x_trans, y_trans), color, 2, cv2.LINE_4)
        cv2.line(frame, (x, y_trans), (x_trans, y_trans), color, 2, cv2.LINE_4)
        
        tSize = cv2.getTextSize(str(rSize), cv2.FONT_HERSHEY_SIMPLEX, 0.5, None)[0]
        
        if tSize[0] < rSize[0] and tSize[1] < rSize[1] and show_dims:
            cv2.putText(frame, str(rSize), (x + int((rSize[0]-tSize[0])/2), y + int((rSize[1])/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color)
        
        return frame
    
    #Functions to be called on mouse callback
    def on_mousepress(self, event, x, y, flags, param):
    
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing_state()                               
            self.set_coord((x, y))
            self.set_size((0, 0))
    
    def on_mouserelease(self, event,x,y,flags,param):
        
        self.set_size_from_coord((x, y))
            
        if event == cv2.EVENT_LBUTTONUP: 
            self.showing_state()  
    
if __name__ == "__main__":
    pass