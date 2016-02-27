"""Alignment Module
This module is responsible for aligning the trimmed reads to the
reduced set of gi references output by the aggregation module and
generating a .sam file with the alignment data
"""

import subprocess
from yax.state.module import Module
from yax.state.type import Artifact, Parameter


class Alignment(Module):

    def __init__(self):
        super.__init__()

    def __call__(self):

        gi_references = ""
        sample_reads = []
        output_directory = ""

        bowtie_options = []
        bowtie_location = ""

        return self.run_alignment(gi_references, sample_reads,
                                  output_directory, bowtie_options,
                                  bowtie_location)

    def run_alignment(self, gi_references, sample_reads, output_directory,
                      bowtie_options, bowtie_location):
        """Calls bowtie2 and executes the alignment. Outputs a .sam file"""

        command = [bowtie_location + "bowtie2-build", gi_references, "index"]
        try:
            # Build bowtie indexes
            subprocess.call(command)
        except Exception as e:
            print("ALIGNMENT: Failed to build bowtie indexes.")
            print(e)

        for i, sample in enumerate(sample_reads):
            command = [bowtie_location + "bowtie2-align"] + bowtie_options + \
                      ["-x", "index", "-U", sample, "-S",
                       output_directory + "sample_" + str(i) + "coverage.sam"]
            try:
                # Align sequences to references
                subprocess.call(command)
            except Exception as e:
                print("ALIGNMENT: Failed to perform bowtie alignment.")
                print(e)

        return

# Artifacts


class GiReferenceSet(Artifact):
    pass


class TrimmedReads(Artifact):
    pass


class SamFiles(Artifact):

    def __init__(self, file_path):
        self.file_path = file_path

# Parameters


class BowtieOptions(Parameter):
    pass
