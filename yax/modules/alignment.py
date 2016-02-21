import subprocess
import configparser


class Alignment:

    def __init__(self, input_artifact, config):
        self.module_name = "alignment"
        self.input_artifact = input_artifact
        self.config = config
        self.gi_reference_set = None
        self.trimmed_reads = None
        self.bowtie_location = None
        self.bowtie_arguments = None
        self.bowtie_build_arguments = None
        self.output_file_path = None
        self.working_directory = None

        self.unpack_artifact()
        self.parse_config()

    def unpack_artifact(self):
        self.gi_reference_set = self.artifact.gi_reference_set
        self.trimmed_reads = self.artifact.trimmed_reads

    def parse_config(self):
        parser = configparser.ConfigParser()
        parser.read_file(open(self.config))
        self.bowtie_location = parser.get(self.module_name, "bowtie_location")
        self.bowtie_arguments = parser.get(self.module_name, "bowtie_arguments")
        self.bowtie_build_arguments = parser.get(self.module_name, "bowtie_build_arguments")
        self.working_directory = parser.get(self.module_name, "working_directory")

    def verify_params(self):
        pass

    def initialize_artifact(self, ):
        pass

    def run(self):
        index_directory = self.working_directory + "index/index"
        subprocess.call([self.bowtie_location + "bowtie2-build", self.gi_reference_set, index_directory])
        subprocess.call([self.bowtie_location + "bowtie2-align", "-x", index_directory, "-U", self.trimmed_reads, "-S",
                         self.output_directory])


class Artifact:

    def __init__(self):
        self.file_path = "/home/hayden/Desktop/bowtie/output.sam";
        self.gi_reference_set = ("/home/hayden/Desktop/bowtie/reference/lambda_virus.fa,"
                                 "/home/hayden/Desktop/bowtie/reference/genome.fa")
        self.trimmed_reads = ("/home/hayden/Desktop/bowtie/reads/reads_1.fq,"
                              "/home/hayden/Desktop/bowtie/reads/reads_2.fq")


alignment = Alignment(Artifact(), "/home/hayden/Desktop/bowtie/config")
alignment.run()
