from yax.state.type import Artifact
import supporting_functions


class PreparedReads(Artifact):
    def __init__(self, completed):
        self.infile_list = None
        self.work_dir = None
        self.out_dir = None
        self.num_workers = None
        self.max_mem_target_gb = None
        self.trimming_type = None
        self.trimming_segment_length = None
        self.adapter_list = None
        self.adapter_tolerance = None
        self.minimum_quality = None
        self.max_below_threshold = None
        self.read_headers = None
        self.read_sequences = None

        if completed:
            reads_files = []
            # get files from self.out_dir
            self.read_headers, self.read_sequences = \
                self.get_reads(reads_files)

    def get_reads(self, reads_files):
        read_headers = []
        read_sequences = []

        for reads_file in reads_files:
            headers, sequences =\
                supporting_functions.read_fasta_file(reads_file)
            read_headers.extend(headers)
            read_sequences.extend(sequences)

        return read_headers, read_sequences

    def __complete__(self):
        pass
