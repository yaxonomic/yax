"""Alignment Module
This module is responsible for aligning the trimmed reads to the
reduced set of gi references output by the aggregation module and
generating a .sam file with the alignment data
"""

import os
from yax.shared.utilities.bowtie2_utils import build_index, call_bt2_align
from yax.artifacts.coverage_data import CoverageData
from yax.artifacts.reads import Reads
from yax.artifacts.gi_references import GiReferences
from yax.state.type import Str


def main(working_dir, output, reads: Reads, gi_references: GiReferences,
         bowtie_options: Str) -> \
         CoverageData:
    print("Running alignment.")
    run_alignment(gi_references, reads, output, working_dir, bowtie_options)


def run_alignment(gi_references, reads_fp, output, working_dir,
                  bowtie_args):
    """
    :param gi_references: Location of gi references
    :param reads_fp: Location of reads trimmed by ReadPrep
    :param output: Artifact to fill out with sam file alignments
    :param working_dir: working directory
    :param bowtie_args: Optional bowtie parameters
    """

    # Get the list of already completed coverage files
    completed_files = output.get_completed_coverage_files().sort()

    num_samples = get_num_samples(reads_fp)
    for sample_num in range(num_samples):

        # Check if file has already been completed
        file = "sample_" + str(sample_num) + "_coverage.sam"
        if file in completed_files:
            continue

        # Get the list of reads that appear in the current sample
        reads = get_reads_in_sample(sample_num, reads_fp)

        # Build the index for the current sample
        index = build_current_index(sample_num, gi_references, working_dir)

        # Call bowtie2 and create a coverage file for the current sample
        call_bt2_align(reads, os.path.join(working_dir, index),
                       os.path.join(output.data_dir, "sample_" +
                                    str(sample_num) + "_coverage.sam"),
                       bowtie_args)

        # Add the coverage file to list of compelted files
        output.append_completed_file("sample_" + str(sample_num) +
                                     "_coverage.sam")
    # Build the object representation of the coverage data
    output.build_coverage_data()
    output.complete()


def get_num_samples(reads_fp):
    """
    Returns the number of samples represented in the reads file
    """
    with open(reads_fp) as reads_file:
        line = reads_file.readline()
        return len(line.split('_')) - 1


def get_reads_in_sample(sample_num, reads_fp):
    """
    Returns a list of all reads in the specified sample
    """
    reads = []
    grab_read = False
    with open(reads_fp) as reads_file:
        lines = reads_file.readlines()
    for line in lines:
        if line.startswith('>'):
            line_data = line.split('_')
            if int(line_data[sample_num + 1]) > 0:
                grab_read = True
        else:
            if grab_read:
                reads.append(line)
    return ','.join(reads)


def build_current_index(sample_num, gi_references, working_dir):
    """
    Still has to be finished
    """
    file = ""
    build_index(file, os.path.join(working_dir, "index_" + str(sample_num)))
    return "index_" + str(sample_num)
