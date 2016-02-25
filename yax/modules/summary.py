import pdfkit
import configparser
from io import StringIO

class Summary:

    def __init__(self, input_artifact, output_artifact, config):
        self.module_name = "summary"

        #self.summary_stats = input_artifact.summary_stats
        #self.summary_table = input_artifact.summary_table
        #self.coverage_data = input_artifact.coverage_data

        self.output_file_path = output_artifact.file_path

        parser = configparser.ConfigParser()
        parser.read_file(open(config))
        self.order_method = parser.get(self.module_name, "order_method")
        self.total_results = parser.get(self.module_name, "total_results")
        self.final_output_file_path = parser.get(self.module_name, "output_file_path")
        self.num_samples = int(parser.get(self.module_name, "number_of_samples"))
        self.num_samples = int(parser.get(self.module_name, "number_of_samples"))

    def verify_params(self):
        """To do: verifies the validity of the config parameters
        Returns:
            Boolean representing whether the params are valid or not
        """
        pass

    def run(self):

        for sample in range(self.num_samples):
            # For every sample, create a summary file
            writer = StringIO()
            writer.write("<html><body>TEST</body></html>")

            pdfkit.from_string(writer.getvalue(), self.output_file_path + "output" + str(sample) + ".pdf")
            pdfkit.from_string(writer.getvalue(), self.final_output_file_path + "output" + str(sample) + ".pdf")

            writer.close()

# The following code is just for testing purposes
# Simulates an artifact and config being passed to the pipeline
class Artifact:

    def __init__(self):
        self.file_path = None
        self.complete = False


# Create output artifact
output_artifact = Artifact()
output_artifact.file_path = "/home/hayden/Desktop/"

# Run alignment with new input_artifact, output_artifact, and the config file
summary = Summary(Artifact(), output_artifact, "/home/hayden/Desktop/config")
summary.run()
