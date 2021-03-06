'''
Advanced trace usage example

This script will use the get_trace_adv() function of the dsa800 class
to perform an advanced trace measurement. The advanced trace allows you
to make a wide spectrum measurement with high resolution. You must provide
a start and stop frequency and the span to be used over that range.
The get_trace_adv function will break up the frequency range into 
segments of width specified by the span argument. The function then
makes a measurement for each of the segments and concatenates the traces
into one array. It returns a nx2 numpy array where the first column
represents the frequencies (Hz) and the second column the trace.
'''

from rigol import dsa800,storage
import time
import datetime
import sys
from component import component
from emc import limit
import json
import os

virtual = "True"

if __name__ == '__main__':
    
    """ 
    Measurement parameters
    The measurement parameters are stored in the file params.txt
    """
    param_file = 'params.json'
    try:
        # Load the parameters from the params.txt file
        with open(param_file) as fp:
            params = json.load(fp)
    except IOError:
        # Create default parameters and save the file
        params = {
            'title': 'Product X Radiated Emissions',
            'dir': 'trace_dir',
            "idn": "TCPIP0::169.254.128.164::hislip0::INSTR",
            'antenna': 'component\\ab900a.csv',
            'cable': 'component\\ASMA500B174L13.csv',
            'limit_std': 'cispr22classb',
            'limit_units': 'dBuV/m(3m)',
            'span': 100e6,
            'sweeps': 10,
            'start_freq': None,
            'stop_freq': None,
            'dsa_cfg': {
                'trace_mode': 'MAXHold',
                'preamp_en': True,
                'units': 'DBUV',
                'emi_filter_en': True,
                'rbw': 120000,
                }
            }
        with open(param_file,'w') as fp:
            json.dump(params,fp,indent=2)
    ## test only

    # Create the DSA object
    dsa = dsa800.dsa800()

    # Create the antenna and cable objects    
    antenna = component.component('Antenna factor',params['antenna'],loss = True)
    cable = component.component('Cable loss',params['cable'],loss = True)
    
    # Create the standard limit
    lim = limit.limit(params['limit_std'],params['limit_units'])
    
    # Start timing
    start_time = time.time()
    
    # Connect to the first detected DSA800

    try:
        dsa.connect(params['idn']) # add idn as parameter
    except Exception as e:
        print('Please make sure that your DSA is connected via UART, USB or TCP')
        print('Here is a list of the detected VISA resources:')
        for dev in dsa.list_devices():
            print('  ',dev)
        sys.exit()

    print("Connected to:", dsa.get_id())

    # DSA815 configuration
    # config = dsa800.dsa800_config()
    config = dsa800.dsa800_config(params['dsa_cfg'])
    # config = params['dsa_cfg']
    # Configure DSA815
    dsa.set_config(config)
    spectrumlist = params['spectrum']
    trace_data = dsa.get_trace_list(spectrumlist)
    dsa.close()
    
    #  Create a unique filename using the date and time
    d = datetime.datetime.now()
    filename = '%s\\trace-%s' % (params['dir'], d.strftime('%Y-%m-%d-%H%M%S'))
    
    # Create a directory for the measurement data
    if not os.path.exists(params['dir']):
        os.makedirs(params['dir'])
    
    # Write trace to CSV and PNG file
    measurement = storage.Measurement(params['title'],config)
    measurement.add_trace(trace_data)
    measurement.add_component(antenna)
    measurement.add_component(cable)
    measurement.add_limit(lim)
    measurement.save_to_csv('%s.csv' % filename)
    measurement.save_to_png('%s.png' % filename)
    
    # End the timer
    end_time = time.time()
    print('Execution time:',end_time-start_time)
    
    print('Completed')    
    
    