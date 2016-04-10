from yax.state.type import Artifact
from os import listdir
from os.path import isfile, join, splitext


class CoverageData(Artifact):

    def build_coverage_data(self):
        """
        Sets the object representation of coverage data from the collection of
        sam files.
        """
        self.samples = []
        # Get sam files
        files = [f for f in listdir(self.data_dir)
                 if isfile(join(self.data_dir, f)) and
                 splitext(f)[1].lower() == '.sam']

        # For each file, create a sample object that holds sequences and
        # alignments
        for file in files:
            sample = self.Sample(splitext(file)[0].split('/')[-1])
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
                        sample.sequences.append(self.Sequence(gi, length))
                    # If the line is an alignment, add it to the sample's list
                    # of alignments
                    else:
                        tabs = line.split('\t')
                        gi = tabs[2].split('|')[1]
                        position = int(tabs[3])
                        length = len(tabs[9])
                        sample.alignments.append(self.Alignment(gi, length,
                                                                position))
                except Exception:
                    continue
            self.samples.append(sample)

    class Sample:
        # Holds the sequences listed in the sam file and the alignments to that
        # sequences
        def __init__(self, name):
            self.name = name
            self.sequences = []
            self.alignments = []

    class Sequence:
        # Holds the gi and length of a sequence
        def __init__(self, gi, length):
            self.gi = gi
            self.length = length

    class Alignment:
        # Holds the gi that was aligned to, length of the alignment, and the
        # starting position of the alignment on the sequences
        def __init__(self, gi, length, position):
            self.gi = gi
            self.length = length
            self.position = position
