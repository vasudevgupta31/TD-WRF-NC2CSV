"""
fetches selected vars from wrf out (nc) to csv
"""
from tqdm import tqdm
import funcs
import config


for folder in tqdm(funcs.os.listdir(config.data_path)):
    folder_path = funcs.os.path.join(config.data_path, folder)
    if funcs.os.path.isdir(folder_path) and not funcs.is_folder_empty(path_=folder_path):

        file_name = funcs.get_req_nc_filename(parent_dir=folder_path)

        simulation_date, data = funcs.read_var(temp_dir=folder_path,
                                               file_name=file_name,
                                               vars=config.vars,
                                               lat=config.lat,
                                               long=config.lon)

        funcs.export_csv(data=data,
                         export_path=config.output_path,
                         lat=config.lat,
                         long=config.lon,
                         file_name=f"{simulation_date}.csv",
                         index=False)
