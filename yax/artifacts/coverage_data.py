from yax.state.type import Artifact
import os
from collections import namedtuple


class CoverageData(Artifact):

    def get_completed_coverage_files(self):
        """
        Gets a list of already completed coverage files
        """
        completed_files = []
        with open(os.path.join(self.data_dir, "/.files"), 'r') as files:
            for file in files.readlines():
                completed_files.append(file)
            files.close()
        return completed_files

    def append_completed_file(self, file):
        with open(os.path.join(self.data_dir, "/.files", 'a')) as files:
            files.write(file + '\n')
            files.close()

    def build_coverage_data(self):
        """
        Sets the object representation of coverage data from the collection of
        sam files.
        """
        self.samples = []

        # Create namedtuple types
        Sample = namedtuple("Sample", ["name", "sequences", "alignments"])
        Sequence = namedtuple("Sequence", ["gi", "length"])
        Alignment = namedtuple("Alignment", ["gi", "length", "position"])

        # Get sam files
        files = [f for f in os.listdir(self.data_dir)
                 if os.path.isfile(os.path.join(self.data_dir, f)) and
                 os.path.splitext(f)[1].lower() == '.sam']

        # For each file, create a sample object that holds sequences and
        # alignments
        for file in files:
            sample_name = os.path.splitext(file)[0].split('/')[-1]
            sample = Sample(sample_name, [], [])
            with open(self.data_dir + '/' + file, 'r') as coverage_file:
                lines = coverage_file.readlines()

            for line in lines:
                try:
                    # If the line is a sequence, add it to the sample's list of
                    #  sequences
                    if line.startswith('@SQ'):
                        tabs = line.split('\t')
                        gi = tabs[1].split('|')[1]
                        length = int(tabs[2].split(':')[1])
                        sample.sequences.append(Sequence(gi, length))
                    # If the line is an alignment, add it to the sample's list
                    # of alignments
                    else:
                        tabs = line.split('\t')
                        gi = tabs[2].split('|')[1]
                        position = int(tabs[3])
                        length = len(tabs[9])
                        sample.alignments.append(Alignment(gi, length,
                                                           position))
                except Exception:
                    continue
            self.samples.append(sample)
