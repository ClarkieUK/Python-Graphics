from poliastro.maneuver import Maneuver
from poliastro.core.iod import izzo
from astropy import units as u
from poliastro.bodies import Sun, Earth, Mars
from poliastro.twobody import Orbit
from datetime import datetime
import bisect
import numpy as np
from poliastro.core.iod import vallado
from lamberthub import izzo2015

def lambert(host : str, target : str, t0 : float, r0 : np.array, desired_mission_duration : int) -> dict :

    # load positions [x,y,z] , velocities [vx,vy,vz]
    dates_target = np.genfromtxt(f'traces\{target}_TRACE.csv',delimiter=',',usecols=[0],skip_header=True,dtype=str) 
    
    # loads i'th row for j'th component of row [i][j]
    _data_target = np.genfromtxt(f'traces\{target}_TRACE.csv',delimiter=',',usecols=[1,2,3],skip_header=True) 
    _data_v_target = np.genfromtxt(f'traces\{target}_TRACE.csv',delimiter=',',usecols=[4,5,6],skip_header=True) 
    
    _sun = np.genfromtxt('traces\SUN_TRACE.csv',delimiter=',',usecols=[1,2,3],skip_header=True)
    _sun_v = np.genfromtxt('traces\SUN_TRACE.csv',delimiter=',',usecols=[4,5,6],skip_header=True)
    
    # convert to heliocentric (?#)
    data_target = _data_target - _sun
    data_v_target = _data_v_target - _sun_v

    info = get_dt(t0, host, target, dates_target, data_target, data_v_target, desired_mission_duration)

    r = info[f'{target}_LOC_LOWER']
    corrected_duration = info['LOWER_DT']
    
    v_i,v_f = izzo(Sun.k,r0,r,corrected_duration,0,True,False,150,1e-8)
    #v_i,v_f = izzo2015(Sun.k,r0,r,corrected_duration,0,True,True,35,0.00001,1e-6)
        
    return v_i, info[f'{target}_VEL_LOWER'], corrected_duration

def get_dt(t0 : float, host : str, target :str, target_dates : np.array, target_trace : np.array, target_velocity_trace : np.array, mission_duration : float)  :
    """get_dt _summary_

    _extended_summary_

    Parameters
    ----------
    t0 : float
        current t in runtime sim
    target_dates : np.array
        all possible dates of mars
    target_trace : np.array
        all possible locations of mars
    mission_duration : float
        desired mission duration
    """
    
    periods = {
        "MARS" : 686.980 *24*60*60,
        "EARTH" : 365 *24*60*60
    }
    
    # convert to unix timestamps
    timestamps = [datetime.strptime(ts, "%A %B %d %Y %H:%M:%S").timestamp() for ts in target_dates]

    # convert duration to seconds
    delta_t = mission_duration*24*60*60  

    # target time
    t_target = t0 + delta_t

    # correct
    orbit_time = periods[f'{target}']
    
    while t_target > timestamps[-1]:  # If t_target is beyond available data
        t_target -= orbit_time  # Move back by one full Mars year

    while t_target < timestamps[0]:  # If t_target is too early (unlikely)
        t_target += orbit_time  # Move forward by one full Mars year

    # find floor and ceil using bisect
    idx = bisect.bisect_left(timestamps, t_target)  # First index >= t_target

    # get floor and ceil values
    t_floor = timestamps[max(0, idx - 1)] if idx > 0 else timestamps[0]
    t_ceil = timestamps[min(idx, len(timestamps) - 1)]

    # convert back to readable format
    t_floor_dt = datetime.fromtimestamp(t_floor)
    t_ceil_dt = datetime.fromtimestamp(t_ceil)

    #print("Target Time:", datetime.fromtimestamp(t_target))
    #print("Floored Time:", t_floor_dt)
    #print("Ceiled Time:", t_ceil_dt)

    return {
        f"{target}_LOC_LOWER" : target_trace[max(0, idx - 1)] if idx > 0 else timestamps[0],
        f"{target}_LOC_UPPER" : target_trace[min(idx, len(timestamps) - 1)],
        f"{target}_VEL_LOWER" : target_velocity_trace[max(0, idx - 1)] if idx > 0 else timestamps[0],
        f"{target}_VEL_UPPER" : target_velocity_trace[min(idx, len(timestamps) - 1)],
        "LOWER_DT" : t_floor-t0,
        "UPPER_DT" : t_ceil-t0,
        "LOWER_TIME" : t_floor_dt,
        "UPPER_TIME" : t_ceil_dt
    }
    
def cycle(start,where,orbit_time) -> float :
    difference = where - start 
    
    if difference > start + orbit_time :
        return difference % orbit_time
    else :
        return where