import numpy as np
import math
from physics_sim import PhysicsSim


class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

 
    
    
    def get_reward(self):
        """Uses current pose of sim to return reward.""" 
       
        x_factor = abs(self.sim.pose[0] - self.target_pos[0])
        y_factor = abs(self.sim.pose[1] - self.target_pos[1])
        z_factor = abs(self.sim.pose[2] - self.target_pos[2])
        
        xyz_factor = (x_factor ** 2) + (y_factor ** 2) + 0.5 * (z_factor  ** 2)       
        
        euler_factor = abs(self.sim.pose[3]+self.sim.pose[4]+self.sim.pose[5])            
        
        velocity_factor = abs(self.sim.v[0]) + abs(self.sim.v[1]) + abs(self.sim.v[2])        
        
        #velocity_factor = abs(math.sqrt(xyz_factor) - total_velocity)               
          
        total_penalty = (xyz_factor + velocity_factor + euler_factor) 

        
        distance_to_target = math.sqrt((x_factor ** 2) + (y_factor ** 2) + (z_factor ** 2))
        
        

        target_reward = 0.0
        
        if distance_to_target >= 0.75 and distance_to_target < 1.0:
            target_reward = 250      
        elif distance_to_target >= 0.25 and distance_to_target < 0.75:
            target_reward = 400   
        elif distance_to_target < 0.25:
            target_reward = 500

        reward = target_reward - 0.1 * total_penalty  + 100
        
        return reward
    
    
   
    
    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state