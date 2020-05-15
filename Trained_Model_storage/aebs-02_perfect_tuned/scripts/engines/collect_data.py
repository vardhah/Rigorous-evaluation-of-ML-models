import os
import sys
import csv
from carla import Image

class collectData():
    def __init__(self, path, isPerception):
        self.path = path
        self.isPerception = isPerception
        self.count = 0
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        csv_file = os.path.join(self.path, "Data.csv")
        self.f = open(csv_file, 'w')
        self.csv_writer = csv.writer(self.f)
        if self.isPerception:
            self.csv_writer.writerow(["image_path", "true_dist", "predicted_dist", "velocity", "brake", "precipitation"])
        else:
            self.csv_writer.writerow(["Episode","Kick_Speed","NN_start_speed", "CRS_speed", "Rewards","Stop_Distance"])

    def __call__(self, episode,kickspd,nn_start_speed,CRS_speed,reward, gt_distance):
        
        self.csv_writer.writerow([episode, round(kickspd, 3),round(nn_start_speed, 3), round(CRS_speed, 3),round(reward, 3), round(gt_distance, 3)])
    
    def close_csv(self):
        self.f.close()
