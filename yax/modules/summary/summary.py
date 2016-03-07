"""Summary module
This module is responsible for outputting a pdf file for each sample.
This file has a list of TaxIds identified  in the sample and a
list of Gis associated with these TaxIds. The user is able to
order this list of Gis.
"""

import pdfkit
import os
from io import StringIO
from yax.artifacts.pdf import Pdf
from yax.artifacts.summary_stats import SummaryStats
from yax.artifacts.summary_table import SummaryTable
from yax.artifacts.coverage_data import CoverageData
from yax.state.type import Directory, Str, Int


def main(output: Pdf, summary_stats: SummaryStats, summary_table: SummaryTable,
         coverage_data: CoverageData, order_method: Str, total_results: Int,
         output_path: Directory):
    return _run_summary(summary_stats, summary_table, coverage_data, output,
                        order_method,  total_results, output_path)


def _run_summary(summary_stats, summary_table, coverage_data, order_method,
                 total_results, output_path):
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
    :param output_path: Location to write the final output pdf
    """

    # Get HTML templates
    file_path = os.path.dirname(os.path.realpath(__file__))
    template = ''.join(open(file_path + "/template.html", 'r').readlines())
    tax_id_snippet = ''.join(open(file_path + "/tax_id_snippet.html", 'r')
                             .readlines())
    coverage_snippet = ''.join(open(file_path + "/coverage_snippet.html", 'r')
                               .readlines())

    num_samples = len(coverage_data.files)
    # For each sample, fill out templates with appropriate data
    for sample in range(num_samples):
        # Get ordered list of tax ids and gis
        alignments = _parse_summary_data(summary_stats, summary_table,
                                         coverage_data[sample], 1)

        alignments, tax_ids = _order_results(alignments, order_method,
                                             total_results)

        template_data = ""
        for i, alignment in enumerate(alignments):
            coverage_plot = _generate_coverage_plot(alignment,
                                                    coverage_snippet)
            align_string = tax_id_snippet.format(alignment["gi"],
                                                 alignment["tax_id"],
                                                 coverage_plot)
            template_data += align_string

        writer = StringIO()
        writer.write(template.format(template_data))

        # Write pdf to output artifact location
        pdfkit.from_string(writer.getvalue(),
                           output_path + "sample_" + str(sample + 1) +
                           ".pdf")

        writer.close()


def _parse_summary_data(summary_stats, summary_table, coverage_data, nm_max):
    # stats = open(summary_stats, 'r')
    # table = open(summary_table, 'r')

    with open(coverage_data, 'r') as sam_file:
        sam_lines = sam_file.readlines()

    alignments = []
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
            gi = current_line[2].split('|')[1]
            number = current_line[0]
            position = current_line[3]
            length = len(current_line[9])

            alignment = {"number": number, "tax_id": tax_id, "gi": gi,
                         "start_pos": position, "length": length,
                         "abs_coverage": 0, "rel_coverage": 0,
                         "total_hits": 0, "inform_hits": 0,
                         "unique_hits": 0}

            alignments.append(alignment)

        except Exception:
            continue

    return alignments


def _order_results(alignments, order_method, total_results):
    if order_method == "ABSOLUTE_COVERAGE":
        alignments.sort(key=lambda align: align["abs_coverage"])
    elif order_method == "RELATIVE_COVERAGE":
        alignments.sort(key=lambda align: align["rel_coverage"])
    elif order_method == "TOTAL_HITS":
        alignments.sort(key=lambda align: align["total_hits"])
    elif order_method == "INFORMATIVE_HITS":
        alignments.sort(key=lambda align: align["inform_hits"])
    elif order_method == "UNIQUE_HITS":
        alignments.sort(key=lambda align: align["unique_hits"])

    tax_ids = []
    for alignment in alignments:
        tax_id = alignment["tax_id"]
        if tax_id not in tax_ids:
            tax_ids.append(tax_id)

    return alignments[:total_results], tax_ids


def _generate_coverage_plot(alignment, coverage_snippet):
    try:
        start_pos = alignment["start_position"]
        align_length = alignment["length"]
        end_pos = int(start_pos) + int(align_length)
        return coverage_snippet.format(start_pos, align_length, end_pos)
    except Exception:
        return None
