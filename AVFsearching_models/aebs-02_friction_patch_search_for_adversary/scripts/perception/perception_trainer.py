from scripts.perception.data_loader import CarlaDataLoader
from scripts.perception.perception_net import PerceptionNet
from torch.utils.data import DataLoader
import torch
import time
import os

class PerceptionTrainer():
    def __init__(self, data_path, split, epoch):
        self.data_set = CarlaDataLoader(data_path, split=split)
        self.data_loader = DataLoader(self.data_set, batch_size=32, shuffle=True)
        self.epoch = epoch
    
    def fit(self):
        self.model = PerceptionNet()
        self.model = self.model.to('cuda')
        optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01, momentum=0.9, nesterov=True)
        loss_func = torch.nn.MSELoss()

        for epoch in range(self.epoch):
            loss_epoch = 0.0
            n_batches = 0
            epoch_start_time = time.time()
            for batch_idx, (images, gt_distances) in enumerate(self.data_loader):
                images = images.to(device='cuda', dtype=torch.float)
                gt_distances = gt_distances.to('cuda', dtype=torch.float)
                optimizer.zero_grad()

                outputs = self.model(images)
                loss = loss_func(outputs, gt_distances)
                loss.backward()
                optimizer.step()
                loss_epoch += loss.item()
                n_batches += 1

            epoch_train_time = time.time() - epoch_start_time
            print('Epoch {}/{}\t Time: {:.3f}\t Loss: {:.8f}'.format(epoch+1, self.epoch, epoch_train_time, loss_epoch/n_batches))
        return self.model
    
    def save_model(self, path='./models/perception'):
        if not os.path.exists(path):
            os.makedirs(path)
        torch.save(self.model.state_dict(), os.path.join(path, "perception.pt"))