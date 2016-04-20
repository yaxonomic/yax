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
from io import StringIO
from yax.artifacts.summary import Summary
from yax.artifacts.summary_stats import SummaryStats
from yax.artifacts.summary_table import SummaryTable
from yax.artifacts.coverage_data import CoverageData
from yax.state.type.parameter import Directory, Str, Int, File
from yax.shared.utilities import taxidtool


def main(working_directory, output, summary_stats: SummaryStats,
         summary_table: SummaryTable, coverage_data: CoverageData,
         order_method: Str, total_results: Int, bin_size: Int,
         output_path: Directory, nodes_fp: File, names_fp: File,
         gi_taxid_nucl_fp: File) -> Summary:

    tax_id_data = taxidtool.build_taxid_data(nodes_fp, names_fp,
                                             gi_taxid_nucl_fp)
    gis_to_taxids = taxidtool.build_gis_to_taxids(tax_id_data)

    print('Running summary.')
    _run_summary(summary_stats, summary_table, coverage_data,
                 str(order_method), total_results, bin_size, str(output_path),
                 output, str(working_directory), gis_to_taxids)


def _run_summary(summary_stats, summary_table, coverage_data, order_method,
                 total_results, bin_size, output_path, output,
                 working_directory, gis_to_taxids):
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

    samples = coverage_data.samples
    # For each sample, fill out templates with appropriate data
    for n, sample in enumerate(samples):
        print('Calculating coverage data: sample ' + str(n + 1) + '/' +
              str(len(samples)))

        template_data = ""

        # Get dictionary containing coverage data for each gi, separated into
        # their respective tax ids
        coverage, max_coverage = _parse_summary_data(sample, gis_to_taxids)
        keys = list(coverage.keys())
        keys.sort()
        for i, key in enumerate(keys):

            print('Calculating coverage data: tax id ' + str(i + 1) + '/' +
                  str(len(keys)))

            # get coverage data for all gis belonging to a certain tax id
            taxid_coverage = coverage[key]

            # get tax id and organism name
            tax_id = key.split('|')[1]
            name = key.split('|')[0]

            # calculate coverage statistics
            _calculate_coverage_stats(taxid_coverage)

            # Get a sorted list of gis
            references = _order_results(taxid_coverage, order_method,
                                        total_results)

            # generate table of gis
            table = _generate_table(references, taxid_coverage)

            # for each gi, calculate a coverage plot
            gi_data = ""

            for j, reference in enumerate(references):
                coverage_plot = _generate_coverage_plot(reference, sample.name,
                                                        taxid_coverage
                                                        [reference],
                                                        working_directory,
                                                        bin_size, max_coverage)

                gi_data += coverage_snippet.format(coverage_plot)

            template_data += tax_id_snippet.format(name, tax_id, table,
                                                   gi_data)

        print('Writing output file.')

        writer = StringIO()
        writer.write(template.format(css, n, template_data))

        # Write pdf to configurable output path
        pdfkit.from_string(writer.getvalue(), str(output_path) + sample.name +
                           ".pdf")
        writer.close()

        # Complete output artifact
        output.write_summary(template.format(css, sample.name, template_data),
                             sample.name)
    # output.complete()


def _parse_summary_data(coverage_data, gis_to_taxids):
    """
    Builds a dictionary representing coverage data. Keys in the dictionary are
    tax ids and value are sub-dictionaries. Sub-dictionaries have gis as keys
    and sub-sub-dictionaries as values. These sub-sub-dictionaries contain all
    coverage data for a particular gi.

    output:

    { 'organism-name|tax-id':
        {
            'gi': {
                'length': value
                'abs_coverage': value
                'rel_coverage': value
                'total_hits': value
                'unique_hits': value
                'inform_hits': value
                'sequence':[a list where each value is the number of times that
                base is covered by an alignment]
            }
        }
    }
    """

    coverage = {}
    # For each sequence in the coverage data, add a record in the dictionary
    # representing the sequence and all it's initially empty coverage
    # statistics
    for sequence in coverage_data.sequences:
        tax_id = '|'.join(_get_taxid_and_name(sequence.gi, gis_to_taxids))
        # if the tax id is not in the dictionary, add it
        if tax_id not in coverage:
            coverage[tax_id] = {}
        # add empty coverage stats to the dictionary record for current tax id
        coverage[tax_id][sequence.gi] = {"length": sequence.length,
                                         "abs_coverage": 0,
                                         "rel_coverage": 0,
                                         "total_hits": 0,
                                         "unique_hits": 0,
                                         "inform_hits": 0,
                                         "sequence": [0] * sequence.length
                                         }

    # For each alignment in the coverage data, update the coverage stats in the
    # coverage dict to reflect the alignment
    max_coverage = 0
    for alignment in coverage_data.alignments:
        gi = alignment.gi
        tax_id = '|'.join(_get_taxid_and_name(gi, gis_to_taxids))

        if tax_id not in coverage:
            continue

        position = alignment.position
        length = alignment.length

        # for each gi, update its coverage sequence
        if gi in coverage[tax_id]:
            # for each position in the alignment, add 1 to the same position on
            # the coverage sequence
            for i in range(position, position + length):
                if i == len(coverage[tax_id][gi]["sequence"]):
                    break
                coverage[tax_id][gi]["sequence"][i] += 1
                # update max_coverage
                if coverage[tax_id][gi]["sequence"][i] > max_coverage:
                    max_coverage = coverage[tax_id][gi]["sequence"][i]
    return coverage, max_coverage


def _order_results(tax_id, order_method, total_results):
    """
    Sorts the list of gis by a given key and returns a sublist containing the
    first n gis
    """
    references = list(tax_id.keys())

    if order_method.upper() == "ABSOLUTE_COVERAGE":
        references.sort(key=lambda ref: tax_id[ref]["abs_coverage"],
                        reverse=True)
    elif order_method.upper() == "RELATIVE_COVERAGE":
        references.sort(key=lambda ref: tax_id[ref]["rel_coverage"],
                        reverse=True)
    elif order_method.upper() == "TOTAL_HITS":
        references.sort(key=lambda ref: tax_id[ref]["total_hits"],
                        reverse=True)
    elif order_method.upper() == "INFORMATIVE_HITS":
        references.sort(key=lambda ref: tax_id[ref]["inform_hits"],
                        reverse=True)
    elif order_method.upper() == "UNIQUE_HITS":
        references.sort(key=lambda ref: tax_id[ref]["unique_hits"],
                        reverse=True)
    else:
        references.sort(key=lambda ref: tax_id[ref]["abs_coverage"],
                        reverse=True)

    return references[:total_results]


def _calculate_coverage_stats(coverage):
    """
    For each gi, counts of number of bases in the sequence that are covered by
     at least one read to calculate the absolute coverage. Divides this amount
     by the length of the sequence to get relative coverage.
    """
    keys = list(coverage.keys())
    keys.sort()

    for key in keys:
        gi = coverage[key]
        sequence = gi["sequence"]
        # Calculate absolute coverage
        absolute_coverage = 0
        for base in sequence:
            if int(base) > 0:
                absolute_coverage += 1
        # Set absolute coverage
        gi["abs_coverage"] = absolute_coverage
        # Calculate relative coverage
        gi["rel_coverage"] = absolute_coverage / len(sequence)


def _generate_table(references, coverage):
    """
    Generates a table where each row is a gi with coverage information.
    """
    # Set table heading
    table = "<table><tr><th>GI</th><th>Length</th><th>Absolute coverage</th>" \
            "<th>Relative coverage</th><th>Average Coverage</th>" \
            "<th>Total Hits</th><th>Unique Hits</th><th>Informative Hits" \
            "</th></tr>"
    for reference in references:
        gi = coverage[reference]
        table += "<tr>"

        # get data for row in the table
        length = gi["length"]
        abs_coverage = gi["abs_coverage"]
        rel_coverage = "%.4f" % gi["rel_coverage"]
        total_hits = gi["total_hits"]
        unique_hits = gi["unique_hits"]
        inform_hits = gi["inform_hits"]

        # calculate average coverage
        average_coverage = 0
        for base in gi["sequence"]:
            average_coverage += base
        average_coverage /= length
        average_coverage = "%.4f" % average_coverage

        # Build table as HTML string
        table += "<td>" + "</td><td>".join([str(reference), str(length),
                                            str(abs_coverage),
                                            str(rel_coverage),
                                            str(average_coverage),
                                            str(total_hits),
                                            str(unique_hits),
                                            str(inform_hits)]) \
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
        sequence = reference["sequence"]
        length = reference["length"]

        # Average data across bins
        binned_data = _bin_sequence(sequence, bin_size)

        # Visual parameters
        mpl.rcParams['patch.antialiased'] = True
        mpl.rcParams['xtick.labelsize'] = 'small'
        mpl.rcParams['ytick.labelsize'] = 'small'

        # Figure size
        fig = pyplot.figure(figsize=(8, 1.8), dpi=180, tight_layout=True)

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

        pyplot.close(fig)

        return str(file_path) + '/coverage_' + str(gi) + '_' + str(sample_id) \
            + '.png'
    except Exception as e:
        return e


def _bin_sequence(sequence, bin_size):
    """
    Divides the sequence into bins of the specified size and averages coverage
    across the entire bin.
    """
    binned_data = [0] * len(sequence)
    average = 0
    bin_start = 0
    # mid_bin flag is true if the iteration is currently in the middle of a bin
    # as opposed to an edge between bins
    mid_bin = False
    for n, base in enumerate(sequence):
        mid_bin = True
        # if n % bin_size == 0, start a new bin
        if n > 0 and n % bin_size == 0:
            mid_bin = False
            # calculate average
            average /= n - bin_start
            # set all values in the bin to the average value
            binned_data[bin_start: n] = [average] * (n - bin_start)
            # reset average
            average = 0
            # set current position to start of next bin
            bin_start = n
        average += base
    # if iteration ended in the middle of a bin, the remainder of the bases
    # must be averaged over the remainder of the sequence.
    if mid_bin:
        average /= len(sequence) - bin_start
        binned_data[bin_start:] = [average] * (len(sequence) - bin_start)
    return binned_data


def _get_taxid_and_name(gi, gis_to_taxids):
    """
    Returns the tax id and scientific organism name as a tuple of the given gi.
    Uses the TaxID Branch clipper tool.
    """
    return gis_to_taxids[gi], "Scientific Name"

coverage = CoverageData(completed=True)
coverage.data_dir = "/home/hayden/Desktop/bowtie/coverage/"
coverage.build_coverage_data()

stats = SummaryStats(completed=True)

table = SummaryTable(completed=True)

summary = Summary(completed=False)
summary.data_dir = "/home/hayden/Desktop/"

tax_id_data = {}

_run_summary(stats, table, coverage, "ABSOLUTE_COVERAGE", 2, 1,
             "/home/hayden/Desktop/yax_out/", summary,
             "/home/hayden/Desktop/yax_working/", tax_id_data)
