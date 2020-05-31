import sys
import logging
import os
import queue
import random
from scripts.engines.reward_calc import reward_calc
from scripts.engines.collect_data import collectData
import math
import numpy as np
import cv2

class SetupWorld():
    def __init__(self, mass=1300, wheel_radius=0.04, dt=0.05, collect={"option":0, "path": None}):
        self.mass=1300 #Kg
        self.r=0.04    # 16 inch=40 cm 
        self.dt=0.05   # frequency = 20 Hz 
        self.g= 9.8    # graviataional acceleration (in m/s^2)
        self.j=1       # kg-m^2 (Moment of Intertia of tire)

        self.w=0.0         # angular acceleration
        self.A=0.0         # Friction Phenomenal curve Coefficient
        self.m=0.0         # friction phenomenal curve coefficient 
        self.c=0.0         # friction phenomenal curve coefficient 
        self.distance=0.0  
        self.velocity=0.0 

        self.episode = 0
        self.flag=0
        self.kickspd=0.0
        self.crossing_velocity=0.0
        self.friction_of_patch=0.0
        self.variance_friction=0.0
        self.collect = collect
        
    
    def reset(self, initial_distance, initial_speed,friction,variance_fric):  
        self.kickspd=initial_speed
        self.friction_of_patch=friction
        self.variance_friction=variance_fric
        self.rewards = reward_calc(a=1.0,d=1.0,base=1.9)
        self.w=initial_speed/self.r 
        self.A= (friction+variance_fric)
        self.m=-1*variance_fric
        self.c=self.A
        self.distance=initial_distance

        if self.collect["option"] != 0 and self.flag!=1 :
            self.flag=1
            self.episode=0 
            self.collect_data = collectData(self.collect["path"])
            
        
        self.step_count = 0
        self.velocity= initial_speed *4/9     # convert velocity is m/s   
        vehicle_stop=self.velocity<=0.0
        

        return [self.distance, self.velocity ,vehicle_stop]
    
    def step(self, action):
        self.step_count += 1
       
        dw= 20*action
        if action<0.9 and self.w>15 : 
            self.w=self.w-dw 
        elif action<0.9 and self.w<=15 :
            self.w=0 
        elif action>=0.9 :
            self.w=0 
        
        slip = abs((self.velocity-self.r*self.w)/self.velocity)
        mu_s= -self.A*np.exp(-20*slip)+self.m*slip +self.c
        accel= -1*mu_s*self.g
        #print('mu_s is',mu_s)
        distance_travelled= self.velocity *self.dt +0.5*accel*np.square(self.dt) 
        self.distance= self.distance-distance_travelled
        self.velocity= self.velocity+accel*self.dt
        friction_force= mu_s*self.mass*self.g 
        applied_brake_force= mu_s*self.mass*self.g -(self.j *dw)/self.r
        
        if self.distance >5 and self.distance<10:
            self.crossing_velocity= self.velocity         
        #rint('current velocity is :',self.velocity)
    
        isStop = self.velocity <= 0.05
        isCollision = self.distance<=0
        done = isStop or isCollision
    
        if done: 
            groundtruth_distance=self.distance
            reward = self.rewards.reward_total(groundtruth_distance,self.crossing_velocity)
            print("====> Stopped & Episode: {},,KickSpd:{}, CRS_spd: {},Reward: {}, Stop_Dist: {}".format(self.episode,self.kickspd,self.crossing_velocity,reward, groundtruth_distance))
            if self.collect["option"] != 0:
               self.collect_data(self.episode, self.kickspd, self.friction_of_patch,self.variance_friction, reward,groundtruth_distance)
            self.episode+=1
        else:
            reward = 0

        return [[self.distance, self.velocity], reward, done] 


    def closefile(self):
        self.collect_data.close_csv()
