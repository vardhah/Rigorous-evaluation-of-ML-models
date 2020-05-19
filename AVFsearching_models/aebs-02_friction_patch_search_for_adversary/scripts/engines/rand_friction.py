class rand_friction():
    def __init__(self, x=1.0, y=1.0, z=2):
        self.A = a
        self.D = d
        self.B = base
        self.reward=0.0

    def reward_total(self, dist,CRS_speed):
           if dist<=10:
             self.reward= -1*(self.B**(10-dist))-2*CRS_speed
           elif (dist >10 and dist<=15) :
             self.reward=0
           elif dist>15 :
              self.x=(dist-15)/10
              self.y=(dist-15)%10
              self.reward_x= -10*self.x*(2*self.A+(self.x-1)*self.D)/2
              self.reward_y=self.y*-1*(self.x+1)
              self.reward=self.reward_x+self.reward_y
           return self.reward
