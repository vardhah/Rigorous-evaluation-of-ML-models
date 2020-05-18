#!/usr/bin/python3
import os
import argparse
from scripts.engines.server_manager import ServerManagerBinary
from scripts.engines.setup_world import SetupWorld
from scripts.rl_agent.ddpg_agent import ddpgAgent
from scripts.rl_agent.input_preprocessor import InputPreprocessor
import numpy as np
import re

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
        collect = args_assertions(args)
        carla_server = ServerManagerBinary({'CARLA_SERVER': os.environ["CARLA_SERVER"]})
        carla_server.reset(port=2002)
        carla_server.wait_until_ready()
        env = SetupWorld(town=1, gui=args.gui, collect=collect, perception=args.perception)
        agent = ddpgAgent(Testing=args.testing)
        input_preprocessor = InputPreprocessor()
        stop_dist=1.0
        total_episode_count=[]
        number_of_loop=0
        
        if args.testing is False:
            total_episode_count.append=args.episode
            number_of_loop=1
            actor_files=['actor']
        elif args.testing is True:
            trained_models=os.listdir("./models/controller/intermittent")
            print("=> Trained Models:",trained_models )
            regex = re.compile(r'actor\d+.pt')
            actor_files = list(filter(regex.search, trained_models))
            print('==> Actor Files:',actor_files)
            number_of_loop=len(actor_files)
            print('Number of loops:',number_of_loop)
            p = re.compile(r'\d+') 
            for element in actor_files:
                   z = int(p.findall(element)[0])
                   total_episode_count.append(z)
            print('==> Episode List:',total_episode_count)
        

        for loop in range(number_of_loop): 
         if args.testing is True:
            agent.loadTestModels(actor_files[loop])
         print('Current Episode:',total_episode_count[loop])
         for episode in range(total_episode_count[loop]):

            initial_distance = np.random.normal(100, 1)
            initial_speed = np.random.uniform(5,45)
            patch_location=np.random.uniform(1,100)
            friction_value=np.random.normal(0.5,0.15)

            R = env.reset(initial_distance, initial_speed,patch_location,friction_value,actor_files[loop])
            #R = env.reset(initial_distance, initial_speed)
            if R[2]==True: 
                print("-----Trapped")
                continue
            #print("Episode {} is started, target distance: {}, target speed: {}, initial distance: {}, initial speed: {}".format(episode, initial_distance, initial_speed, s[0], s[1]))
    
            s=R[0:2]
            s = input_preprocessor(s) 
            epsilon = 1.0 - (episode+1)/(total_episode_count[loop])
            #epsilon=1.0
            while True:
                a = agent.getAction(s, epsilon)
                s_, r, done= env.step(a[0][0])
                s_ = input_preprocessor(s_)
                if args.testing is False:
                    agent.storeTrajectory(s, a, r, s_, done)
                    agent.learn()
                s = s_
                

                if done:
                    #stop_dist=120*s[0] 
                    #print("Episode {} is done, the reward is {}".format(episode,r))
                    break

            if args.testing is False:
                if np.mod(episode, 20) == 0:
                    agent.save_model()
                if np.mod(episode,500) == 0:
                    agent.save_intermittent_model(episode)
            #episode=episode+1
        env.closefile()
        carla_server.stop()
        
    except AssertionError as error:
        print(repr(error))
    except Exception as error:
        print('Caught this error: ' + repr(error))
        carla_server.stop()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        carla_server.stop()
