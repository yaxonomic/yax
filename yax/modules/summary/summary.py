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


def main(working_directory, output, summary_stats: SummaryStats,
         summary_table: SummaryTable, coverage_data: CoverageData,
         order_method: Str, total_results: Int, bin_size: Int,
         output_path: Directory) -> Summary:
    print('Running summary.')
    return _run_summary(summary_stats, summary_table, coverage_data,
                        order_method, total_results, bin_size,
                        str(output_path), output, str(working_directory))


def _run_summary(summary_stats, summary_table, coverage_data, order_method,
                 total_results, bin_size, output_path, output,
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

    coverage_data = coverage_data.samples
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

            taxid_coverage = coverage[key]

            tax_id = key.split('|')[0]
            name = key.split('|')[1]
            _set_hit_data(tax_id, summary_stats, summary_table)
            _calculate_coverage_stats(taxid_coverage)
            references = _order_results(taxid_coverage, order_method,
                                        total_results)
            table = _generate_table(references, taxid_coverage)

            gi_data = ""
            for j, reference in enumerate(references):
                coverage_plot = _generate_coverage_plot(reference, sample.name,
                                                        taxid_coverage
                                                        [reference],
                                                        working_directory,
                                                        bin_size, max_coverage)

                gi_data += coverage_snippet.format(coverage_plot)

            template_data += tax_id_snippet.format(tax_id, name, table,
                                                   gi_data)

        print('Writing output file.')

        writer = StringIO()
        writer.write(template.format(css, n, template_data))

        # Write pdf to configurable output path
        pdfkit.from_string(writer.getvalue(), str(output_path) + "sample_" +
                           str(n + 1) + ".pdf")
        writer.close()

        # Complete output artifact
        output.write_summary(template.format(css, n, template_data),
                             "sample_" + str(n))
    #output.complete()


def _parse_summary_data(coverage_data):
    """
    Parse sam files and build a dictionary of taxids that, for each taxid,
    stores a dictionary with gis as keys and a list of coverage values as
    values.
    """

    coverage = {}
    for sequence in coverage_data.sequences:
        tax_id = '|'.join(_get_taxid_and_name(sequence.gi))
        if tax_id not in coverage:
            coverage[tax_id] = {}
        coverage[tax_id][sequence.gi] = [0] * (sequence.length + 6)
        coverage[tax_id][sequence.gi][5] = sequence.length

    max_coverage = 0
    for alignment in coverage_data.alignments:
        gi = alignment.gi
        tax_id = '|'.join(_get_taxid_and_name(gi))

        if tax_id not in coverage:
            continue

        position = alignment.position
        length = alignment.length

        if gi in coverage[tax_id]:
            for i in range(position, position + length):
                coverage[tax_id][gi][i + 5] += 1
                if coverage[tax_id][gi][i + 5] > max_coverage:
                    max_coverage = coverage[tax_id][gi][i + 5]
    print(max_coverage)
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
    gi = line[1].split('|')[1]
    tax_id = '|'.join(_get_taxid_and_name(gi))
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
    else:
        references.sort(key=lambda ref: tax_id[ref][0], reverse=True)

    return references[:total_results]


def _calculate_coverage_stats(coverage):
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
        for n, base in enumerate(sequence):
            if int(base) > 0:
                absolute_coverage += 1
        # Set absolute coverage
        gi[0] = absolute_coverage
        # Calculate relative coverage
        gi[1] = gi[0] / (len(gi) - 6)


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
        average_coverage /= length
        average_coverage = "%.4f" % average_coverage

        table += "<td>" + "</td><td>".join([str(reference), str(length),
                                            str(abs_coverage),
                                            str(rel_coverage),
                                            str(average_coverage)]) \
                 + "</td></tr>"
    table += "</table>"
    return table


def _generate_coverage_plot(gi, sample_id, reference, file_path, bin_size,
                            max_y):
    """
    Generates a matplotlib coverage plot and returns the HTML <img> tag with
    the plot as an image.
    """
    try:
        sequence = reference[6:]
        length = reference[5]

        # Average data across bins
        binned_data = _bin_sequence(sequence, bin_size)

        # Visual parameters
        mpl.rcParams['patch.antialiased'] = True
        mpl.rcParams['xtick.labelsize'] = 'small'
        mpl.rcParams['ytick.labelsize'] = 'small'

        # Figure size
        pyplot.figure(figsize=(8, 2.057), dpi=72, tight_layout=True)

        # plot of the data
        pyplot.plot(range(length), binned_data, '-', color="#000000")
        pyplot.grid(True)

        # Axis ranges
        pyplot.xlim(0, length)
        pyplot.ylim(0, max_y)

        # Axis and labels
        pyplot.title(gi)

        # Save plot
        pyplot.savefig(file_path + '/coverage_' + str(gi) + '_' +
                       str(sample_id) + '.png')

        return str(file_path) + '/coverage_' + str(gi) + '_' + str(sample_id) \
            + '.png'
    except Exception as e:
        return e


def _bin_sequence(sequence, bin_size):
    binned_data = [0] * len(sequence)
    average = 0
    bin_start = 0
    mid_bin = False
    for n, base in enumerate(sequence):
        mid_bin = True
        if n > 0 and n % bin_size == 0:
            mid_bin = False
            average /= n - bin_start
            binned_data[bin_start: n] = [average] * (n - bin_start)
            average = 0
            bin_start = n
        average += base
    if mid_bin:
        average /= len(sequence) - bin_start
        binned_data[bin_start:] = [average] * (len(sequence) - bin_start)
    return binned_data


def _get_taxid_and_name(gi):
    """
    Returns the tax id and scientific organism name as a tuple of the given gi.
    Uses the TaxID Branch clipper tool.
    """

    # Test Code
    tax_id = random.randint(1, 3)
    if tax_id == 1:
        return "Organism One", str(tax_id)
    elif tax_id == 2:
        return "Organism Two", str(tax_id)
    elif tax_id == 3:
        return "Organism Three", str(tax_id)



import random

test_coverage = CoverageData()
sample = CoverageData.Sample("Sample One")
for n in range(random.randint(3, 9)):
    gi = random.randint(1000, 9999)
    gi_length = random.randint(5000, 80000)
    sample.sequences.append(CoverageData.Sequence(gi, gi_length))
    for i in range(random.randint(100, 5000)):
        alignment_length = random.randint(20, 900)
        position = random.randint(0, gi_length - alignment_length - 1)
        sample.alignments.append(CoverageData.Alignment(gi, alignment_length,
                                                        position))

test_coverage.samples.append(sample)

output = Summary("/home/hayden/Desktop/")

_run_summary("", "", test_coverage,
             "ABSOLUTE_COVERAGE", 5, 50, "/home/hayden/Desktop/",
             output, "/home/hayden/Desktop/")
