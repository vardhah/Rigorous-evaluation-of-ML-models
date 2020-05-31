#!/usr/bin/python3
import os
import argparse
from scripts.engines.setup_world import SetupWorld
from scripts.rl_agent.ddpg_agent import ddpgAgent
from scripts.rl_agent.input_preprocessor import InputPreprocessor
import numpy as np


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
        
        print('Number of episodes :',args.episode)
        for episode in range(args.episode):
            #print('in for loop')
            initial_distance = np.random.normal(100, 1)
            initial_speed = np.random.uniform(5,70)
            #print('spawned velocity is',initial_speed)
            friction=np.random.normal(0.5,0.15)
            variance_fric= 0.2*np.random.random_sample()+0.1    # estimate varince between maximum and kinetic friction
            
            R = env.reset(initial_distance, initial_speed,friction,variance_fric)
            #print('came from SetupWorld')
            if R[2]==True: 
                print("-----Trapped")
                continue
            #print("Episode {} is started, target distance: {}, target speed: {}, initial distance: {}, initial speed: {}".format(episode, initial_distance, initial_speed, s[0], s[1]))
            #print('Not trapped')
            s=R[0:2]
            s = input_preprocessor(s) 
            #print('Out from input preprocessor')
            epsilon = 1.0 - (episode+1)/(args.episode)

            while True:
                #print('In while loop')
                a = agent.getAction(s, epsilon)
                s_, r, done= env.step(a[0][0])
                s_ = input_preprocessor(s_)
                #print('In whily loop')
                if args.testing is False:
                    agent.storeTrajectory(s, a, r, s_, done)
                    agent.learn()
                    #print('In learing loop')
                s = s_
                #print('Out learing loop')
                if done:
                    break

            if args.testing is False:
                if np.mod(episode, 20) == 0:
                    agent.save_model()
        env.closefile()
        print('finished')
        
    except AssertionError as error:
        print(repr(error))
    except Exception as error:
        print('Caught this error: ' + repr(error))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")


