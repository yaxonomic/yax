import configparser
import state.type.artifact as artifact
import state.type.parameter as paramtype
import subprocess
from state.errors import ModuleError





# [paths]
# infile_list = /path/to/in.list
# work_dir = /path/to/work/dir
# out_dir = /path/to/output/dir
#
# [performance]
# num_workers = 4
# max_mem_target_gb = 8
#
# [trimming]
# # valid values are:
# # LCD
# # LCDQ
# # SEG
# type = LCD
# segment_length = 50
#
# optional
#
# [adapters]
# adapter_list = /path/to/adapter.list
# adapter_tolerance = 10
#
# [quality_filter]
# minimum_quality = 25
# max_below_threshold = 6

def main(module_working_dir,
         output,
         infile_list: paramtype.File,
         work_dir: paramtype.Directory,
         out_dir: paramtype.Directory,
         num_workers: paramtype.Int,
         max_mem_target_db: paramtype.Int,
         type_: paramtype.Str,
         segment_length: paramtype.Int,
         adapter_list: paramtype.File,
         adapter_tolerance: paramtype.Int,
         minimum_quality: paramtype.Int,
         max_below_threshold: paramtype.Int,
         path_to_readprep_main: paramtype.File)\
         -> (someoutput):

    config = configparser.ConfigParser()
    config["paths"] = {"infile_list": infile_list,
                       "work_dir": work_dir,
                       "out_dir": out_dir}

    config["performance"] = {"num_workers": num_workers,
                             "max_mem_target_gb": max_mem_target_db}

    config["trimming"] = {"type": type_,
                          "segment_length": segment_length}

    config["adapters"] = {"adapter_list": adapter_list,
                          "adapter_tolerance": adapter_tolerance}

    config["quality_filter"] = {"minimum_quality": minimum_quality,
                                "max_below_threshold": max_below_threshold}

    with open(module_working_dir + "readprep_config.ini", 'w') as configfile:
        config.write(configfile)

    #python /path/to/main.pyx /path/to/config.ini

    command = " ".join(["python",
                        path_to_readprep_main,
                        module_working_dir + "readprep_config.ini"])

    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        raise ModuleError("read_prep failed")

    return