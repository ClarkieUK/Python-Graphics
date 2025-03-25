from dataclasses import dataclass
from datetime import datetime

@dataclass
class TimeManager() :
    
    # delta time
    last_frame          = 0.0
    anchor_time         = 0.0
    frame_count         = 0
    current_frame_time  = 0.0
    
    # sim properties
    unix_start      = 1735689600
    simulated_time  = 0
    sim_date        = ""
    
    
    @classmethod
    def calculate_deltatime(cls, this_frame) :
        
        dt = this_frame - cls.last_frame ; cls.last_frame  = this_frame
        cls.frame_count += 1 
        
        return dt

    @classmethod
    def update_average_framerate(cls, this_frame) -> None :
        
        if this_frame - cls.anchor_time >= 1.0 :
            
            print("Avg. FPS :", cls.frame_count)
            print("Simulated Time :", f"{cls.simulated_time/3.154e+7:.5f}" , 'yr')
            print(cls.sim_date)
            
            print('\n')
            
            cls.anchor_time = this_frame 
            cls.frame_count = 0
            
        elif this_frame > 10.0:
            pass
            
    @classmethod
    def update_sim_date(cls) :
        cls.sim_date = datetime.fromtimestamp(cls.unix_start+float(cls.simulated_time)).strftime("%A, %B %d, %Y %H:%M:%S")