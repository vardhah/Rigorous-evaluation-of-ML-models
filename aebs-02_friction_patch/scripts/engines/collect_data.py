import os
import sys
import csv
from carla import Image

class collectData():
    def __init__(self, path, isPerception,current_actor):
        self.path = path
        self.isPerception = isPerception
        self.count = 0
        data_file='Data_'+current_actor+'.csv'
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        csv_file = os.path.join(self.path, data_file)
        self.f = open(csv_file, 'w')
        self.csv_writer = csv.writer(self.f)
        if self.isPerception:
            self.csv_writer.writerow(["image_path", "true_dist", "predicted_dist", "velocity", "brake", "precipitation"])
        else:
            self.csv_writer.writerow(["Episode","Kick_Speed","NN_start_speed", "CRS_speed","location_of_patch","friction", "Rewards","Stop_Distance"])

    def __call__(self, episode,kickspd,nn_start_speed,CRS_speed,location,friction,reward, gt_distance):
        
        self.csv_writer.writerow([episode, round(kickspd, 2),round(nn_start_speed, 2), round(CRS_speed, 2),round(location, 2),round(friction, 2),round(reward, 2), round(gt_distance, 2)])
    
    def close_csv(self):
        self.f.close()
