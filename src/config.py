"""
Path and other run configs
"""
import os

data_path = '/Users/vasu/TensorDynamics/NCSAMPLES/WRF/WRF-OUT'
output_path = os.path.join(os.getcwd(), '..', 'WRF_CSV_OUT')
lat = 28.70
lon = 77.10
vars = ['T2', 'U10', 'V10', 'SWDOWN']

os.makedirs(output_path, exist_ok=True)
