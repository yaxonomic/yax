import inspect
import os


def get_data_path(rel_fp, subfolder='data'):
    callers_filename = inspect.getouterframes(inspect.currentframe())[1][1]
    path = os.path.dirname(os.path.abspath(callers_filename))
    return os.path.join(path, subfolder, rel_fp)
