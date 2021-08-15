"""
Functions for processing
"""
import os
import shutil
from math import cos, asin, sqrt
import numpy as np
import pandas as pd
import xarray as xr


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def create_temp_dir(parent_dir):
    temp_path = os.path.join(parent_dir, 'temp')
    if os.path.exists(temp_path):
        remove(temp_path)
    os.makedirs(temp_path)
    return temp_path


def is_folder_empty(path_):
    exclude = ['.DS', 'temp']
    files = [file for file in os.listdir(path_) if all(x not in file for x in exclude)]
    return len(files) == 0


def get_req_nc_filename(parent_dir):
    files = [file for file in os.listdir(parent_dir) if os.path.isfile(os.path.join(parent_dir, file))]
    exclude = ['.DS', 'd']
    req_files = [file for file in files if all(x not in file for x in exclude)]
    if len(req_files) != 1:
        raise IndexError(f"Found multiple Wrf files for {parent_dir} {req_files}")
    file = req_files[0]
    # shutil.copyfile(os.path.join(parent_dir, file), os.path.join(parent_dir, 'temp', file))
    return file


def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))


def closest(data, v):
    return min(data, key=lambda p: distance(v['XLAT'], v['XLONG'], p['XLAT'], p['XLONG']))


def read_var(temp_dir, file_name, vars, lat, long):
    ndf = xr.open_dataset(os.path.join(temp_dir, file_name))
    data_frame = ndf.to_dataframe()
    take = ['XLONG', 'XLAT'] + vars
    data_frame = data_frame[take].copy()

    # FIND CLOSES LAT LONG
    lat_longs = data_frame[['XLONG', 'XLAT']].drop_duplicates().reset_index(drop=True).copy()
    lat_long_list = [{'XLAT': r['XLAT'], 'XLONG': r['XLONG']} for i, r in lat_longs.iterrows()]
    req_lat_lon = {'XLAT': lat, 'XLONG': long}
    best_match = closest(data=lat_long_list, v=req_lat_lon)

    # FILTER DATA FRAME
    data_frame = data_frame[(data_frame['XLAT'] == best_match['XLAT']) &
                            (data_frame['XLONG'] == best_match['XLONG'])]
    data_frame = data_frame.reset_index(drop=False)

    # CLEAN DATA FRAME
    data_frame['Date'] = data_frame['Times'].apply(lambda x: pd.to_datetime(int(x), format='%Y%m%d'))
    data_frame.drop(['y', 'x', 'Times'], axis=1, inplace=True)
    data_frame = data_frame.iloc[:96, :]
    data_frame['Time'] = pd.date_range("00:00", "23:45", freq="15min").time
    order_vars = ['Date', 'Time', 'XLAT', 'XLONG'] + vars
    simulation_date = data_frame['Date'].apply(lambda x: x.strftime('%Y-%m-%d')).unique()[0]
    return simulation_date, data_frame[order_vars]


def get_meta(xr_data):
    meta = xr_data.info()


def export_csv(data, export_path, lat, long, file_name, **kwargs):
    export_file_to = os.path.join(export_path, f'{lat}N_{long}E')
    os.makedirs(export_file_to, exist_ok=True)
    data.to_csv(os.path.join(export_file_to, file_name), **kwargs)
