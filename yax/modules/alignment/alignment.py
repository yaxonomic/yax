"""Alignment Module
This module is responsible for aligning the trimmed reads to the
reduced set of gi references output by the aggregation module and
generating a .sam file with the alignment data
"""

import subprocess
import os
from yax.state.module import Module
from yax.state.type import Artifact, Parameter


class Alignment(Module):

    def __init__(self):
        super.__init__()

    def __call__(self):

        gi_references = ""
        sample_reads = []
        output_directory = ""

        bowtie_options = BowtieArguments([])
        bowtie_location = BowTieLocation("/usr/bin/bowtie2/")

        return self.run_alignment(gi_references, sample_reads,
                                  output_directory, bowtie_options,
                                  bowtie_location)

    def run_alignment(self, gi_references, sample_reads, output_directory,
                      bowtie_options, bowtie_location):
        """Calls bowtie2 and executes the alignment. Outputs a .sam file"""

        command = [bowtie_location + "/bowtie2-build", gi_references, "index"]
        try:
            # Build bowtie indexes
            subprocess.call(command)
        except Exception as e:
            print("ALIGNMENT: Failed to build bowtie indexes.")
            print(e)

        for i, sample in enumerate(sample_reads):
            command = [bowtie_location + "/bowtie2-align"] + bowtie_options + \
                      ["-x", "index", "-U", sample, "-S",
                       output_directory + "sample_" + str(i) + "coverage.sam"]
            try:
                # Align sequences to references
                subprocess.call(command)
            except Exception as e:
                print("ALIGNMENT: Failed to perform bowtie alignment.")
                print(e)

        return

# Parameters


class BowtieArguments(Parameter):

    def __init__(self, value):
        super().__init__(key="bowtie-arguments", value=value)

    def _validate_(self):
        try:
            for arg in self.value:
                pass
            return True
        except Exception:
            return False


class BowTieLocation(Parameter):

    def __init__(self, value):
        super().__init__(key="bowtie-location", value=value)

    def _validate_(self):
        try:
            if not os.path.isdir(self.value):
                return False
            if self.value.split('/').rstrip('/')[-1] == "bowtie2":
                return True
            return False
        except Exception:
            return False
