class reward_calc():
    def __init__(self, a=1.0, d=1.0, base=1.9):
        self.A = a
        self.D = d
        self.B = base
        self.reward=0.0

    def reward_total(self, dist,CRS_speed):
        if dist<=2:
            self.reward= -1*(self.B**(2-dist))
        elif (dist >2 and dist<=5) :
             self.reward=0
        elif dist>5 :
              self.x=(dist-5)/10
              self.y=(dist-5)%10
              self.reward_x= -10*self.x*(2*self.A+(self.x-1)*self.D)/2
              self.reward_y=self.y*-1*(self.x+1)
              self.reward=self.reward_x+self.reward_y
        
        return self.reward
