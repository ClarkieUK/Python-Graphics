# wants to load all major bodies first, then fills in the rest by looping over leftover id's
import requests
import re
import numpy as np
from scipy.constants import G

def search(ID):
    
    query = ("https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='{ID}'"
             "&OBJ_DATA='YES'&MAKE_EPHEM='YES'&EPHEM_TYPE='VECTORS'&START_TIME='2020-01-01'"
             "&STOP_TIME='2020-01-02'&STEP_SIZE='2d'&VEC_TABLE='2'&CENTER='@ssb'&OUT_UNITS='KM-S'"
             "") # command is target body
    
    response = requests.get(query.format(ID=ID))
    
    data = response.text
    
    #print(data)
    
    # Mass x10^22 (kg)      = 1.307+-0.018
    # Mass, 10^24 kg        = ~1988410
    # Mass (10^20 kg )        =  1.08 (10^-4)
    mass_pattern = r"Mass(,)? *x? *\(?10\^(?P<power>-?\d+) *\(?(?P<units>kg|g) *\)? *= *(~)?(?P<base>\d+((\.\d+)?)) *(\(10\^(?P<modifier>-?\w)+\))? *(\+- *(?P<error>\d* *(\.\d+)?)?)?"
    # GM= n.a. 
    # GM= 62.6284 
    # GM, km^3/s^2          = 132712440041.93938
    # GM (km^3/s^2)          = 5959.9155+- 0.004
    gm_pattern = r"GM(,)? *(\(?km\^3\/s\^2\)?)? *= *(~)?(?P<base>\d+((\.\d+)?)) *(\+- *(?P<error>\d* *(\.\d+)?)?)?"
    # Target body name: Pluto (999)  
    # Target body name: 176 Iduna (A877 TB)
    name_pattern = r" *Target *body *name: *(\d+)? *(?P<ID>(\w+(-\w+)?) *(\w+)?) *\((\d+\)|(\w \w))?"
    
    # Search 
    mass_flag = re.search(mass_pattern, data)
    gm_flag   = re.search(gm_pattern, data)
    name_flag = re.search(name_pattern, data)
    
    if mass_flag != None :
        if 'kg' in mass_flag.group('units') :
            mass_value = float(mass_flag.group('base')) * 10 ** float(mass_flag.group('power'))
        elif mass_flag.group('units') == 'g' :
            mass_value = float(mass_flag.group('base'))/1000 * 10 ** float(mass_flag.group('power'))
            
    if mass_flag != None :
        if mass_flag.group('modifier') != None :
            mass_value *= 10**(float(mass_flag.group('modifier')))
        
    # try GM value instead
    else : 
        if gm_flag != None :
            if gm_flag.group() == 'n.a.' :
                mass_value = "Unknown Mass" 
            else :
                mass_value = float(gm_flag.group('base'))/G
        else :
            mass_value = "Unknown Mass"
        
    print(mass_value)
    print(name_flag.group('ID').strip())
    
    
def search_2(ID) :
    
    query = ("https://api.le-systeme-solaire.net/rest/bodies/{ID}/rowData=true") # command is target body
    
    response = requests.get(query.format(ID=ID))
    
    data = response.text
    
    print(data)
    
    
IDS = np.arange(199,1000,50)

ID = 'jupiter'

for a in IDS :
    search(a)
    
