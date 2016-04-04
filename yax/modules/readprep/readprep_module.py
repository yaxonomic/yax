from yax.state.tests.test_pipeline.artifacts.prepared_reads import\
    PreparedReads
from yax.state.type.parameter import Int, Str, File
import subprocess
import configparser


def main(working_dir,
         output,
         path_to_readprep_main: File,
         infile_list: File,
         num_workers: Int,
         max_mem_target_gb: Int,
         trimming_type: Str,
         trimming_segment_length: Int,
         adapter_list: File="optional",
         adapter_tolerance: Int="optional",
         minimum_quality: Int="optional",
         max_below_threshold: Int="optional")\
         -> PreparedReads:

    prepared_reads, = output

    prepared_reads.infile_list = infile_list
    prepared_reads.work_dir = working_dir
    prepared_reads.out_dir = None
    prepared_reads.num_workers = num_workers
    prepared_reads.max_mem_target_gb = max_mem_target_gb
    prepared_reads.trimming_type = trimming_type
    prepared_reads.trimming_segment_length = trimming_segment_length
    prepared_reads.adapter_list = adapter_list
    prepared_reads.adapter_tolerance = adapter_tolerance
    prepared_reads.minimum_quality = minimum_quality
    prepared_reads.max_below_threshold = max_below_threshold

    path_to_config_file = "/".join([working_dir, "/", "runid",
                                    "readprep_config.ini"])
    write_readprep_config(path_to_config_file)
    run_readprep(path_to_config_file, path_to_readprep_main)

    return output


def write_readprep_config(path_to_config_file, prepared_reads):
    config = configparser.ConfigParser()
    config['paths'] = {'infile_list': prepared_reads.infile_list,
                       'work_dir': prepared_reads.working_dir,
                       'out_dir': "output_directory"}
    config['performance'] = {'num_workers': prepared_reads.num_workers,
                             'max_mem_target_gb':
                             prepared_reads.max_mem_target_gb}
    config['trimming'] = {'type': prepared_reads.trimming_type,
                          'segment_length':
                          prepared_reads.trimming_segment_length}
    config['adapters'] = {'adapter_list': prepared_reads.adapter_list,
                          'adapter_tolerance':
                          prepared_reads.adapter_tolerance}
    config['quality_filter'] = {'minimum_quality':
                                prepared_reads.minimum_quality,
                                'max_below_threshold':
                                prepared_reads.max_below_threshold}

    with open(path_to_config_file) as readprep_configfile:
        config.write(readprep_configfile)


def run_readprep(path_to_config_file, path_to_readprep_main):
    command = ["python", path_to_readprep_main, path_to_config_file]
    subprocess.call(" ".join(command), shell=True)
