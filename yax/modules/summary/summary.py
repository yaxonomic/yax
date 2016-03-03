"""Summary module
This module is responsible for outputting a pdf file for each sample.
This file has a list of TaxIds identified  in the sample and a
list of Gis associated with these TaxIds. The user is able to
order this list of Gis.
"""

import pdfkit
import os
from io import StringIO
from yax.state.module import Module


class Summary(Module):

    def __init__(self):
        super().__init__()

    def __call__(self):
        summary_stats = ""
        summary_table = ""
        coverage_data = ["/home/hayden/Desktop/bowtie/output.sam"]
        order_method = ""
        total_results = 10
        num_samples = 1
        output_path = "/home/hayden/Desktop/"
        final_output_path = "/home/hayden/Desktop/"

        return self.run_summary(summary_stats, summary_table,
                                coverage_data, order_method,
                                total_results, num_samples,
                                output_path, final_output_path)

    def run_summary(self, summary_stats, summary_table, coverage_data,
                    order_method, total_results, num_samples,
                    output_path, final_output_path):
        """
        :param summary_stats:
        :param summary_table:
        :param coverage_data: List of Sam files documenting coverage
        :param order_method: Method of ordering the list, possible values are:
                'ABSOLUTE_COVERAGE'
                'RELATIVE_COVERAGE'
                'TOTAL_HITS'
                'INFORMATIVE_HITS'
                'UNIQUE_HITS'
        :param total_results: Number of top tax id candidates to return
        :param num_samples: Number of samples
        :param output_path: Location to right the pdf for the final artifact
        :param final_output_path: Location to right the pdf, specified by the
        user
        :return: file path to the directory containing the output pdfs
        """

        # Get HTML templates
        file_path = os.path.dirname(os.path.realpath(__file__))
        template = ''.join(open(file_path + "/template.html", 'r').readlines())
        tax_id_snippet = ''.join(open(file_path + "/tax_id_snippet.html", 'r')
                                 .readlines())

        # For each sample, fill out templates with appropriate data
        for sample in range(num_samples):
            # Get ordered list of tax ids and gis
            alignments = self.parse_summary_data(summary_stats,
                                                 summary_table,
                                                 coverage_data[sample], 1)

            template_data = ""
            for i, tax_id in enumerate(alignments.keys()):
                gi_string = ""
                for j, gi in enumerate(alignments[tax_id].keys()):
                    coverage_plot = \
                        self.generate_coverage_plot(alignments[tax_id][gi])
                    gi_string = tax_id_snippet.format(gi, tax_id,
                                                      coverage_plot)
                template_data += gi_string

            writer = StringIO()
            writer.write(template.format(template_data))

            # Write pdf to output artifact location
            pdfkit.from_string(writer.getvalue(),
                               output_path + "sample_" + str(sample + 1) +
                               ".pdf")

            # Write pdf to location specified in config
            pdfkit.from_string(writer.getvalue(),
                               final_output_path + "final_sample_" +
                               str(sample + 1) + ".pdf")

            writer.close()

            return output_path

    def parse_summary_data(self, summary_stats, summary_table, coverage_data,
                           nm_max):
        # stats = open(summary_stats, 'r')
        # table = open(summary_table, 'r')

        with open(coverage_data, 'r') as sam_file:
            sam_lines = sam_file.readlines()

        alignments = {}

        for line in sam_lines:
            try:
                if line[0] == '@':
                    continue
                current_line = line.split('\t')

                nm = False
                for tag in current_line[11:]:
                    if "NM" in tag:
                        nm = int(tag.split(':')[2]) < nm_max
                        break
                if not nm:
                    continue

                tax_id = current_line[2].split('|')[3]

                if tax_id not in alignments:
                    alignments[tax_id] = {}
                tax_id = alignments[tax_id]

                gi = current_line[2].split('|')[1]
                if gi not in tax_id:
                    tax_id[gi] = []
                gi = tax_id[gi]

                alignment = {}
                read_number = current_line[0]
                position = current_line[3]
                length = len(current_line[9])
                alignment["read_number"] = read_number
                alignment["start_position"] = position
                alignment["length"] = length

                gi.append(alignment)

            except Exception:
                continue

        return alignments

    def order_results(self, alignments, order_method, total_results):
        return alignments

    def generate_coverage_plot(self, gi):
        try:
            template_str = ""
            for alignment in gi:
                read_number = alignment["read_number"]
                start_pos = alignment["start_position"]
                align_length = alignment["length"]
                end_pos = int(start_pos) + int(align_length)
                template_str += \
                    ("<li>Read Number: {3} - Start: {0} - End: {1} - "
                     "Length: {2}</li>"
                     .format(start_pos, end_pos, align_length, read_number))
            return template_str
        except Exception:
            return None

