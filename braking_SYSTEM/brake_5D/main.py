#!/usr/bin/python3
import os
import argparse
from scripts.engines.setup_world import SetupWorld
from scripts.rl_agent.ddpg_agent import ddpgAgent
from scripts.rl_agent.input_preprocessor import InputPreprocessor
import numpy as np
from scripts.engines.AVF_search import AVF_search
from scripts.engines.Priority_replay_AVF import PR_AVF

def args_assertions(args):
    collect_1 = args.collect_perception is not None
    collect_2 = args.collect_detector is not None
    collect = {"option": 0, "path": None}
    assert (collect_1 and collect_2) != True, "don't set collect_detector and collect_perception simultaneously"
    if collect_1:
        collect = {"option": 1, "path": args.collect_perception} # collect data for perception training
    elif collect_2:
        collect = {"option": 2, "path": args.collect_detector} # collect data for detector training
    return collect

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assurance Monitoring for RL-based emergency braking system.')
    parser.add_argument("-g", "--gui", help="set gui mode.", action="store_true")
    parser.add_argument("-t", "--testing", help="set testing mode", action="store_true", default=False)
    parser.add_argument("-cp", "--collect_perception", help="collect the data for perception training")
    parser.add_argument("-ca", "--collect_detector", help="collect the data for detector training")
    parser.add_argument("-p", "--perception", help="set the path of perception neural network")
    parser.add_argument("-e", "--episode", help="set the number of episode", type=int, default=1)

    args = parser.parse_args()

    try:
        os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"]="1"  # specify which GPU(s) to be used
        collect = args_assertions(args)
        env = SetupWorld(mass=1300, wheel_radius=0.04, dt=0.05, collect=collect)
        agent = ddpgAgent(Testing=args.testing)
        input_preprocessor = InputPreprocessor()
        agnt_number=8000;                            # select agent
        pr_avf=PR_AVF(agnt_number)                   # Priority replay avf class declaration
        avf=AVF_search()                             # avf search class declaration  
        stopdist=6.0
        print('Number of episodes :',args.episode)
        for episode in range(args.episode):
         while stopdist>5.0:
            friction=0.7
            numberofsamples=2000
            initial_distance = np.random.normal(100, 1)  
            
            ##Vanilla Monte Carlo sampler---------------------------------------------------------------    
            """
            initial_speed = np.random.normal(38,11)                            # Vanilla sampling 
            friction_of_patch=np.random.normal(0.7,0.15)
            if friction<=0 : friction=0 ;
            size_of_patch= np.random.normal(20,5)       # Size of patch (total width)
            if size_of_patch<0 : size_of_patch=0
            location_of_patch= np.random.normal(50,12)       # location of patch (center of patch)
            """
            ## AVF based sampler -------------------------------------------------------------
           
            data= avf.avf_predictor(numberofsamples,agnt_number)    # AVF based Sampling
            initial_speed=data[0][1]
            friction_of_patch=data[0][2]
            location_of_patch=data[0][3]
            size_of_patch=data[0][4]
            
            #-------------------------------------------------------------------------------

            #initial_speed = pr_avf.pr_sampler()                               # PR sampling
            # ------------------------------------------------------------------------------                                
            if initial_speed <1 : initial_speed=1
            #print('spawned velocity is',initial_speed)
            
            

            
            R = env.reset(initial_distance, initial_speed,friction,friction_of_patch,size_of_patch,location_of_patch)
            #print('came from SetupWorld')
            

            s=R[0:3]
            #print('s is :',s)
            s = input_preprocessor(s) 
            #print('Out from input preprocessor')
            epsilon = 1.0 - (episode+1)/(args.episode)


            while True:
                #print('In while loop')
                a = agent.getAction(s, epsilon)
                s_, r, done= env.step(a[0][0])
                s_ = input_preprocessor(s_)
                if args.testing is False:
                    agent.storeTrajectory(s, a, r, s_, done)
                    agent.learn()
                    #print('In learing loop')
                s = s_
                #print('Out learing loop')
                if done:
                    stopdist=s[0]*120
                    break

            if(stopdist<=5):
                print(' => => YEAH !!!  Found a crashed case')
            if args.testing is False:
                if np.mod(episode, 50) == 0:
                    agent.save_model()
                if np.mod(episode,1000) == 0:
                    agent.save_intermittent_model(episode)
        env.closefile()
        print('finished')
        
    except AssertionError as error:
        print(repr(error))
    except Exception as error:
        print('Caught this error: ' + repr(error))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")


