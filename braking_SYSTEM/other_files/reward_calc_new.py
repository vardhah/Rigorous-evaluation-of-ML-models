class reward_calc():
    def __init__(self, a=1.0, d=1.0, base=1.9):
        self.A = a
        self.D = d
        self.B = base
        self.reward=0.0

    def reward_step(self, dist,dist_travelled):
        if dist<=5:
            self.reward=-50*dist_travelled
        elif (dist >5 and dist<=10):
            self.reward=0
        elif (dist >10) :
             self.reward=dist_travelled;
        
        return self.reward
