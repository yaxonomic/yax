"""Summary module
This module is responsible for outputting a pdf file for each sample.
This file has a list of TaxIds identified  in the sample and a
list of Gis associated with these TaxIds. The user is able to
order this list of Gis.
"""

import pdfkit
import matplotlib as mpl
import matplotlib.pyplot as pyplot
import os
import os.path
from io import StringIO
from yax.artifacts.summary import Summary
from yax.artifacts.summary_stats import SummaryStats
from yax.artifacts.summary_table import SummaryTable
from yax.artifacts.coverage_data import CoverageData
from yax.state.type import Directory, Str, Int


def main(output: Summary, summary_stats: SummaryStats,
         summary_table: SummaryTable, coverage_data: CoverageData,
         order_method: Str, total_results: Int, output_path: Directory):
    return _run_summary(summary_stats, summary_table, coverage_data,
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

    coverage_data = _get_files(coverage_data)
    # For each sample, fill out templates with appropriate data
    for n, sample in enumerate(coverage_data):
        # Get ordered list of tax ids and gis
        print('Calculating coverage data:' + str(n + 1) + '/' +
              str(len(coverage_data)))
        coverage = _parse_summary_data(sample, 1)
        _set_hit_data(coverage, summary_stats, summary_table)
        calculate_coverage_stats(coverage)
        references = _order_results(coverage, order_method, total_results)
        tax_ids = _get_tax_ids(references)

        template_data = ""
        for i, reference in enumerate(references):
            print('Generating coverage plot: ' + str(i + 1) + '/' +
                  str(len(references)))
            coverage_plot = _generate_coverage_plot(coverage[reference],
                                                    coverage_snippet, i,
                                                    output_path)
            gi = reference.split('|')[1]
            tax_id = reference.split('|')[3]
            gi_string = tax_id_snippet.format(gi, tax_id, coverage_plot)
            template_data += gi_string

        print('Writing output file.')
        writer = StringIO()
        writer.write(template.format(tax_ids, template_data))

        # Write pdf to output artifact location
        pdfkit.from_string(writer.getvalue(), output_path + "sample_" +
                           str(n + 1) + ".pdf")
        writer.close()


def _parse_summary_data(coverage_data, nm_max):

    with open(coverage_data, 'r') as sam_file:
        sam_lines = sam_file.readlines()

    coverage = {}
    for line in sam_lines:
        try:
            if line[:3] == '@SQ':
                _append_reference_array(coverage, line)
                continue
            elif line[0] == '@':
                continue
            current_line = line.split('\t')

            '''
            nm = False
            for tag in current_line[11:]:
                if "NM" in tag:
                    nm = int(tag.split(':')[2]) < nm_max
                    break
            if not nm:
                continue
            '''

            reference = current_line[2]
            position = int(current_line[3])
            length = int(len(current_line[9]))

            for i in range(position, position + length):
                coverage[reference][i + 4] += 1

        except Exception:
            continue
    return coverage


def _get_files(coverage_data):
    return [coverage_data + name for name in os.listdir(coverage_data)
            if os.path.isfile(coverage_data + name)]


def _get_tax_ids(references):
    tax_ids = []
    for reference in references:
        tax_id = reference.split('|')[3]
        if tax_id not in tax_ids:
            tax_ids.append(tax_id)
    return '<li>' + '</li><li>'.join(tax_ids) + '</li>'


def _append_reference_array(coverage, line):
    """
    :param line: line in the sam file
    :param coverage: 2d array with subarrays representing coverage for each
    sequence
    :return: Sets entry for certain gi to an array of zeros the same length
    as the reference
    """
    line = line.split('\t')
    reference = line[1].split(':')[1]
    length = int(line[2].split(':')[1])
    coverage[reference] = [0] * (length + 5)


def _set_hit_data(stats, table, coverage):
    pass


def _order_results(coverage, order_method, total_results):
    references = list(coverage.keys())

    if order_method == "ABSOLUTE_COVERAGE":
        references.sort(key=lambda ref: coverage[ref][0], reverse=True)
    elif order_method == "RELATIVE_COVERAGE":
        references.sort(key=lambda ref: coverage[ref][1], reverse=True)
    elif order_method == "TOTAL_HITS":
        references.sort(key=lambda ref: coverage[ref][2], reverse=True)
    elif order_method == "INFORMATIVE_HITS":
        references.sort(key=lambda ref: coverage[ref][3], reverse=True)
    elif order_method == "UNIQUE_HITS":
        references.sort(key=lambda ref: coverage[ref][4], reverse=True)

    return references[:total_results]


def calculate_coverage_stats(coverage):
    for gi in coverage.values():
        # Calculate absolute coverage
        absolute_coverage = 0
        for base in gi[5:]:
            if int(base) > 0:
                absolute_coverage += 1
        gi[0] = absolute_coverage
        # Calculate relative coverage
        gi[1] = gi[0] / (len(gi) - 5)


def _generate_coverage_plot(reference, coverage_snippet, n, file_path):
    try:
        mpl.rcParams['patch.antialiased'] = True
        mpl.rcParams['xtick.labelsize'] = 'small'
        mpl.rcParams['ytick.labelsize'] = 'small'

        pyplot.figure(figsize=(7, 2.0), dpi=72, tight_layout=True)
        # the histogram of the data
        pyplot.fill_between(range(len(reference) - 5), reference[5:],
                            interpolate=True, color='blue')
        pyplot.xlim(0, len(reference) - 5)
        pyplot.ylim(ymin=0)

        # Axis and labels
        pyplot.xlabel('Sequence')
        pyplot.ylabel('Depth')
        pyplot.title('Coverage')
        pyplot.grid(False)

        # Save plot
        pyplot.savefig(file_path + '/coverage_' + str(n) + '.png')

        return coverage_snippet.format(file_path + 'coverage_' + str(n) +
                                       '.png')
    except Exception:
        return None


_run_summary(None, None, '/home/hayden/Desktop/bowtie/coverage/',
             "ABSOLUTE_COVERAGE", 5, '/home/hayden/Desktop/')
