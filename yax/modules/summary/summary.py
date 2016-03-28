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
from yax.state.type.parameter import Directory, Str, Int


def main(working_directory: Directory, output: Summary,
         summary_stats: SummaryStats, summary_table: SummaryTable,
         coverage_data: CoverageData, order_method: Str, total_results: Int,
         bin_size: Int, output_path: Directory):
    print('Running summary.')
    return _run_summary(summary_stats, summary_table, coverage_data,
                        order_method, total_results, bin_size,
                        str(output_path), output, str(working_directory))


def _run_summary(summary_stats, summary_table, coverage_data, order_method,
                 total_results, bin_size, output_path, output_artifact_path,
                 working_directory):
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
    css = file_path + "/style.css"
    tax_id_snippet = ''.join(open(file_path + "/tax_id_snippet.html", 'r')
                             .readlines())
    coverage_snippet = ''.join(open(file_path + "/coverage_snippet.html", 'r')
                               .readlines())

    coverage_data = _get_files(coverage_data)
    # For each sample, fill out templates with appropriate data
    for n, sample in enumerate(coverage_data):
        print('Calculating coverage data: sample ' + str(n + 1) + '/' +
              str(len(coverage_data)))
        # Get ordered list of tax ids and gis
        coverage, max_coverage = _parse_summary_data(sample)

        template_data = ""
        for i, key in enumerate(list(coverage.keys())):

            print('Calculating coverage data: tax id ' + str(i + 1) + '/' +
                  str(len(list(coverage.keys()))))

            tax_id = coverage[key]
            _set_hit_data(tax_id, summary_stats, summary_table)
            calculate_coverage_stats(tax_id, bin_size)
            references = _order_results(tax_id, order_method, total_results)

            table = _generate_table(references, tax_id)

            gi_data = ""
            for j, reference in enumerate(references):
                coverage_plot = _generate_coverage_plot(reference,
                                                        tax_id[reference],
                                                        working_directory,
                                                        bin_size, max_coverage)

                gi_data += coverage_snippet.format(coverage_plot)

            template_data += tax_id_snippet.format(key, table, gi_data)

        print('Writing output file.')
        writer = StringIO()
        writer.write(template.format(css, n, template_data))

        # Write pdf to configurable output path
        pdfkit.from_string(writer.getvalue(), str(output_path) + "sample_" +
                           str(n + 1) + ".pdf")

        # Write pdf to output artifact location
        pdfkit.from_string(writer.getvalue(), str(output_artifact_path) +
                           "sample_" + str(n + 1) + ".pdf")
        writer.close()


def _parse_summary_data(coverage_data):
    """
    Parse sam files and build a dictionary of taxids that, for each taxid,
    stores a list of gis and coverage values for those gis.
    """
    with open(coverage_data, 'r') as sam_file:
        sam_lines = sam_file.readlines()

    coverage = {}
    max_coverage = 0
    for line in sam_lines:
        try:
            if line[:3] == '@SQ':
                _append_reference_array(coverage, line)
                continue
            elif line[0] == '@':
                continue
            current_line = line.split('\t')

            reference = current_line[2].split('|')
            tax_id = reference[3]
            gi = reference[1]

            position = int(current_line[3])
            length = int(len(current_line[9]))

            for i in range(position, position + length):
                coverage[tax_id][gi][i + 5] += 1
                if coverage[tax_id][gi][i + 5] > max_coverage:
                    max_coverage = coverage[tax_id][gi][i + 5]

        except Exception:
            continue
    return coverage, max_coverage


def _get_files(coverage_data):
    """
    Get a list of files in the coverage_data directory.
    """
    try:
        return [str(coverage_data) + name for name in os.listdir(coverage_data)
                if os.path.isfile(str(coverage_data) + name)]
    except Exception:
        return None


def _append_reference_array(coverage, line):
    """
    :param line: line in the sam file
    :param coverage: 2d array with subarrays representing coverage for each
    sequence
    :return: Sets entry for certain gi to an array of zeros the same length
    as the reference
    """
    line = line.split('\t')
    reference = line[1].split(':')[1].split('|')
    tax_id = reference[3]
    gi = reference[1]
    length = int(line[2].split(':')[1])

    if tax_id not in coverage.keys():
        coverage[tax_id] = {}
    coverage[tax_id][gi] = [0] * (length + 6)
    coverage[tax_id][gi][5] = length


def _set_hit_data(stats, table, coverage):
    """
    NOT FINISHED
    Uses summary stats and table to set the number of unique and informative
    hits for each reference.
    """
    try:
        with open(stats, 'r') as stats_file:
            stats_file.readlines()
    except Exception:
        return coverage

    try:
        with open(table, 'r') as table_file:
            table_file.readlines()
    except Exception:
        return coverage


def _order_results(tax_id, order_method, total_results):
    """
    Sorts the list of gis by a given key and returns a certain number of gis
    """
    references = list(tax_id.keys())

    if order_method == "ABSOLUTE_COVERAGE":
        references.sort(key=lambda ref: tax_id[ref][0], reverse=True)
    elif order_method == "RELATIVE_COVERAGE":
        references.sort(key=lambda ref: tax_id[ref][1], reverse=True)
    elif order_method == "TOTAL_HITS":
        references.sort(key=lambda ref: tax_id[ref][2], reverse=True)
    elif order_method == "INFORMATIVE_HITS":
        references.sort(key=lambda ref: tax_id[ref][3], reverse=True)
    elif order_method == "UNIQUE_HITS":
        references.sort(key=lambda ref: tax_id[ref][4], reverse=True)

    return references[:total_results]


def calculate_coverage_stats(coverage, bin_size):
    """
    For each gi, counts of number of bases in the sequence that are covered by
     at least one read to calculate the absolute coverage. Divides this amount
     by the length of the sequence to get relative coverage.
    """
    for key in coverage.keys():
        gi = coverage[key]
        sequence = gi[6:]
        # Calculate absolute coverage
        absolute_coverage = 0
        averaged_coverage = [0]
        for n, base in enumerate(sequence):
            if int(base) > 0:
                absolute_coverage += 1
            averaged_coverage[-1] += int(base)
            if n != 0 and n % bin_size == 0:
                averaged_coverage[-1] /= bin_size
                averaged_coverage.append(0)
            if n % bin_size != 0 and n == len(sequence) - 1:
                averaged_coverage[-1] /= n % bin_size
        # Set absolute coverage
        gi[0] = absolute_coverage
        # Calculate relative coverage
        gi[1] = gi[0] / (len(gi) - 6)
        coverage[key] = gi[:6] + averaged_coverage


def _generate_table(references, coverage):
    """
    Generates a table where each row is a gi with coverage information.
    """
    table = "<table><tr><th>GI</th><th>Length</th><th>Absolute coverage</th>" \
            "<th>Relative coverage</th><th>Average Coverage</th></tr>"
    for reference in references:
        sequence = coverage[reference]
        table += "<tr>"
        length = sequence[5]
        abs_coverage = sequence[0]
        rel_coverage = "%.4f" % sequence[1]
        average_coverage = 0
        for base in sequence[6:]:
            average_coverage += base
        average_coverage /= len(sequence[6:])
        average_coverage = "%.4f" % average_coverage

        table += "<td>" + "</td><td>".join([reference, str(length),
                                            str(abs_coverage),
                                            str(rel_coverage),
                                            str(average_coverage)]) \
                 + "</td></tr>"
    table += "</table>"
    return table


def _generate_coverage_plot(gi, reference, file_path, bin_size, max_y):
    """
    Generates a matplotlib coverage plot and returns the HTML <img> tag with
    the plot as an image.
    """
    try:
        sequence = reference[6:]
        length = reference[5]

        y_data = []
        for base in sequence:
            y_data += [base] * bin_size
        y_data = y_data[:length]

        mpl.rcParams['patch.antialiased'] = True
        mpl.rcParams['xtick.labelsize'] = 'small'
        mpl.rcParams['ytick.labelsize'] = 'small'

        pyplot.figure(figsize=(8, 2.057), dpi=72, tight_layout=True)
        # the histogram of the data
        pyplot.fill_between(range(length), y_data, interpolate=True,
                            color='#409AB8')
        pyplot.xlim(0, length)
        pyplot.ylim(0, max_y)

        # Axis and labels
        pyplot.title(gi)
        pyplot.grid(False)

        # Save plot
        pyplot.savefig(file_path + '/coverage_' + gi + '.png')

        return str(file_path) + '/coverage_' + gi + '.png'
    except Exception as e:
        return e
