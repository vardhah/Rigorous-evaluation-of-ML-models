#!/usr/bin/python3
import os
import argparse
from scripts.engines.server_manager import ServerManagerBinary
from scripts.engines.setup_world import SetupWorld
from scripts.rl_agent.ddpg_agent import ddpgAgent
from scripts.rl_agent.input_preprocessor import InputPreprocessor
import numpy as np
import re
import tensorflow as tf

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
        total_episode_count=[]
        avf_model = tf.keras.models.load_model('./DATA/saved_model/my_model')
        samples_per_iteration=100
        container = np.load('./DATA/stdmean.npz')

       
        for episode in range(args.episode):
            #Generating data stream 
            random_seed=np.random.randint(1,10000)
            np.random.seed(random_seed)
            candidate_initial_speed =5+40*(np.random.rand(samples_per_iteration,1).reshape(-1,1))
            random_seed=np.random.randint(1,10000)
            np.random.seed(random_seed)
            candidate_friction_value=(0.387*np.random.randn(samples_per_iteration,1)+0.5).reshape(-1,1) 
            data=np.concatenate((candidate_initial_speed,candidate_friction_value),axis=1)
            data_normalised=np.divide(np.subtract(data,container['mean']),container['std'])
            #prediction using AVF
            predicted_y=avf_model.predict(data_normalised,batch_size=8)
            max_value=np.amax(predicted_y)
            array_position=np.where(predicted_y==max_value)[0]
            data_final=np.concatenate((data[array_position,:],predicted_y[array_position,:]),axis=1)
            print('selected data is:',data_final)


            initial_distance = np.random.normal(100, 1)
            initial_speed = data_final[0,0]
            patch_location=np.random.uniform(1,100)
            friction_value=data_final[0,1]

            R = env.reset(initial_distance, initial_speed,patch_location,friction_value)
            #R = env.reset(initial_distance, initial_speed)
            if R[2]==True: 
                print("-----Trapped")
                continue
            #print("Episode {} is started, target distance: {}, target speed: {}, initial distance: {}, initial speed: {}".format(episode, initial_distance, initial_speed, s[0], s[1]))
    
            s=R[0:2]
            s = input_preprocessor(s) 
            epsilon = 1.0 - (episode+1)/args.episode
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
                    break

            if args.testing is False:
                if np.mod(episode, 20) == 0:
                    agent.save_model()
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

