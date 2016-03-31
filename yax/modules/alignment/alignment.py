"""Alignment Module
This module is responsible for aligning the trimmed reads to the
reduced set of gi references output by the aggregation module and
generating a .sam file with the alignment data
"""

import subprocess
from yax.artifacts.alignments import Alignments
from yax.artifacts.reads import Reads
from yax.artifacts.gi_references import GiReferences
from yax.state.type import Str


def main(working_dir, output, reads: Reads, gi_references: GiReferences,
         bowtie_options: Str) -> Alignments:
    return run_alignment(gi_references, reads, output, bowtie_options,
                         working_dir)


def run_alignment(gi_references, sample_reads, output,
                  bowtie_options, working_dir):
    """
    :param gi_references: Location of gi references
    :param sample_reads: Location of reads trimmed by ReadPrep
    :param output: Artifact to fill out with sam file alignments
    :param bowtie_options: Optional bowtie parameters
    """

    command = ["bowtie2-build", gi_references, working_dir + "/index"]
    try:
        # Build bowtie indexes
        subprocess.call(command)
    except Exception as e:
        print("ALIGNMENT: Failed to build bowtie indexes.")
        print(e)

    for i, sample in enumerate(sample_reads):
        command = ["bowtie2-align"] + bowtie_options + \
                  ["-x", working_dir + "/index", "-U", sample, "-S",
                   str(output) + "sample_" + str(i) + "coverage.sam"]
        try:
            # Align sequences to references
            subprocess.call(command)
        except Exception as e:
            print("ALIGNMENT: Failed to perform bowtie alignment.")
            print(e)
