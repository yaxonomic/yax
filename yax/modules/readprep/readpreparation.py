from yax.state.tests.test_pipeline.artifacts.prepared_reads import\
    PreparedReads
from yax.state.type.parameter import Int, Str, File
import subprocess
import configparser


def main(working_dir,
         output,
         details,
         readprep_main_fp: File,
         infile_list: File,
         trimming_type: Str,
         trimming_segment_length: Int,
         adapter_list: File=None,
         adapter_tolerance: Int=None,
         minimum_quality: Int=None,
         max_below_threshold: Int=None)\
         -> PreparedReads:
    """Generates readprep config file and calls readprep.

    For successful use of readprep a config.ini file is required. That file is
    created and then passed to readprep along with an output location for files
    containing prepared reads.

    Parameters
    ----------
    working_dir : str
        location where config file will be temporarily written for readprep run
    output : object
        containing the artifacts which will be created as part of this module
    details : object
        containing parameters from global settings of YAX run
    readprep_main_fp: File
        location of read_prep.py
    infile_list: File
        containing the list of fasta files to prepare
    trimming_type: Str
        indicates what type of fasta preparation is required of readprep
    trimming_segment_length: Int
        indicates desired output length of reads
    adapter_list: File
        optional readprep parameter containing a list of adapters to remove
        reads being prepared
    adapter_tolerance: Int
        optional readprep parameter indicates the length to check for
        adapters that exist in each read
    minimum_quality: Int
        optional readprep parameter for quality filtering indicates the minimum
        quality to allow in prepared reads
    max_below_threshold: Int
        optional readprep paramter indicates the number of bases in a read that
        are allowed to miss the minimum quality score before that read is
        discarded

    Returns
    -------
    None
        A temporary config.ini file is generated for the run of readprep but
        this file is removed after successful completion. The file containging
        prepared reads is generated which contains all reads in a collapsed
        format without duplicates.
    """
    prepared_reads, = output

    config_file_fp = os.path.join(working_dir,
                                       details.runid + "readprep_config.ini")

    prepared_reads.config_file_fp = config_file_fp

    generate_readprep_config(config_file_fp,
                             infile_list,
                             working_dir,
                             details.num_workers,
                             details.max_mem_target_gb,
                             trimming_type,
                             trimming_segment_length,
                             adapter_list,
                             adapter_tolerance,
                             minimum_quality,
                             max_below_threshold)

    call_readprep(readprep_main_fp, config_file_fp)

    return output

def generate_readprep_config(config_file_fp,
                             infile_list,
                             working_dir,
                             num_workers,
                             max_mem_target_gb,
                             trimming_type,
                             trimming_segment_length,
                             adapter_list,
                             adapter_tolerance,
                             minimum_quality,
                             max_below_threshold):
    """Generates config.ini for this run of readprep.

    Each run of readprep requires a config file to take input from the user
    which describes its functionality. This file is placed in the working
    directory and upon successful completion of the artifact is removed.

    Parameters
    ----------
    config_file_fp : str
        location where config file will be temporarily written for readprep run
    infile_list: File
        containing the list of fasta files to prepare
    working_dir : str
        Used by readprep as a temporary directory for working files
    num_workders : int
        number of concurrent threads readprep will be allowed to operate with
    max_mem_target_gb : int
        maximum memory that readprep will be allowed for operation
    trimming_type: Str
        indicates what type of fasta preparation is required of readprep
    trimming_segment_length: Int
        indicates desired output length of reads
    adapter_list: File
        optional readprep parameter containing a list of adapters to remove
        reads being prepared
    adapter_tolerance: Int
        optional readprep parameter indicates the length to check for
        adapters that exist in each read
    minimum_quality: Int
        optional readprep parameter for quality filtering indicates the minimum
        quality to allow in prepared reads
    max_below_threshold: Int
        optional readprep paramter indicates the number of bases in a read that
        are allowed to miss the minimum quality score before that read is
        discarded

    Returns
    -------
    None
        Generates temporary file which is used by readprep as a means of
        communicating user input.
    """
    config = configparser.ConfigParser()
    config['paths'] = {'infile_list': infile_list,
                       'work_dir': working_dir,
                       'out_dir': prepared_reads_fp}
    config['performance'] = {'num_workers': num_workers,
                             'max_mem_target_gb': max_mem_target_gb}
    config['trimming'] = {'type': trimming_type,
                          'segment_length': trimming_segment_length}

    # optional fields of readprep
    if adapter_list not None:
        config['adapters'] = {'adapter_list': adapter_list,
                              'adapter_tolerance': adapter_tolerance}
    if minimum_quality not None:
        config['quality_filter'] = {'minimum_quality': minimum_quality,
                                    'max_below_threshold': max_below_threshold}

    # writing configparser to config.ini for readprep consumption
    with open(config_file_fp) as readprep_configfile:
        config.write(readprep_configfile)


def call_readprep(readprep_main_fp, config_file_fp):
    """Calls the readprep utility.

    Readprep takes in multiple FASTA formatted files and collapses their
    contents so that only unique reads are represented while recording the
    multiple origins of each collapsed read.

    Parameters
    ----------
    readprep_main_fp : str
        indicates where the readprep utility main.py is located
    config_file_fp : str
        indicates the location of the temporary config.ini file for this run
        of Readprep

    Returns
    -------
    None
        Generates prepared reads output file at out_dir indicated in config
        file.
    """
    subprocess.call([" ".join(["python",
                               readprep_main_fp,
                               config_file_fp])],
                               shell=True)
