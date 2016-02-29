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
        coverage_data = []
        order_method = ""
        total_results = 10
        num_samples = 5
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
        :return:
        """

        # Get HTML templates
        file_path = os.path.dirname(os.path.realpath(__file__))
        template = ''.join(open(file_path + "/template.html", 'r').readlines())
        tax_id_snippet = ''.join(open(file_path + "/tax_id_snippet.html", 'r')
                                 .readlines())

        # For each sample, fill out templates with appropriate data
        for i, sample in enumerate(range(num_samples)):
            # Get ordered list of tax ids and gis
            tax_ids, gis = self.parse_summary_data(summary_stats,
                                                   summary_table,
                                                   coverage_data,
                                                   order_method,
                                                   total_results)
            template_data = ""
            for j, tax_id in enumerate(tax_ids):
                coverage_plot = self.generate_coverage_plot(coverage_data)
                # Fill out template with tax id, gis, and a coverage plot
                gis_string = '<li>' + '</li><li>'.join(gis[j]) + '</li>'
                template_data += tax_id_snippet.format(tax_id,
                                                       gis_string,
                                                       coverage_plot)

            writer = StringIO()
            writer.write(template.format(template_data))

            # Write pdf to output artifact location
            pdfkit.from_string(writer.getvalue(),
                               output_path + "sample_" + str(i) + ".pdf")

            # Write pdf to location specified in config
            pdfkit.from_string(writer.getvalue(),
                               final_output_path + "final_sample_" + str(i) +
                               ".pdf")

            writer.close()

            return output_path

    def parse_summary_data(self, summary_stats, summary_table,
                           coverage_data, order_method, total_results):
        # stats = open(summary_stats, 'r')
        # table = open(summary_table, 'r')
        # coverage = open(coverage_data, 'r')
        return ["5", "3", "8"], [["2", "7", "4"], ["1", "8", "5"], ["9", "11", "3"]]

    def generate_coverage_plot(self, coverage_data):
        # coverage = open(coverage_data, 'r')
        return "COVERAGE PLOT GOES HERE"
