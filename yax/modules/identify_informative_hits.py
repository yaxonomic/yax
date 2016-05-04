from yax.shared.utilities import taxidtool
from yax.artifacts import TaxIDData, InformativeAlignmentData, IdentifiedTaxa
from yax.state.type.parameters import Int, File


def main(working_dir, output, details, identified_taxa_art: IdentifiedTaxa,
         tax_id_data_art: TaxIDData, lca_dist: Int, min_hits: Int,
         min_relative_hits: Int, sequences_input_fp: File) \
            -> InformativeAlignmentData:
    """Produces InformativeAlignmentData artifact type

    The InformativeAlignmentData artifact contains a FASTA formatted file and a
    file representing the tree observed when built from alignments. The hits in
    these alignments are first determined to be informative or not based on
    least common ancestor and minimum hits on tax id to be informative.

    Parameters
    ----------
        identified_taxa_art : IdentifiedTaxa
            artifact from an alignment step that describes reads that hit to
            tax ids
        tax_id_data_art : TaxIDData
            tax id data file artifact
        lca_dist: Int
            edges to traverse between multiple tax ids when determining if a
            read that hit multiple taxids is informative
        min_hits: Int
            absolute number of hits a taxid must exhibit to be determined
            informative
        min_relative_hits: Int
            number of hits relative to total number of hits reported that a
            taxid must exhibit to be determined informative
        sequences_input_fp: File
            FASTA formatted file containing sequence data based on gi

    Returns
    -------
        output
            generates InformativeAlignmentData artifact

    """
    hit_data, = output

    hit_data.sequences_input_fp = sequences_input_fp
    hit_data.truncation_level = "species"
    hit_data.tax_id_data = taxidtool.parse_taxid_data(tax_id_data_art)

    with open(identified_taxa_art, mode='r') as fh:
        hit_taxa_lines = fh.readlines()

    hit_taxa = get_hit_taxa(hit_taxa_lines)

    hit_tax_ids, total_informative_hits = get_hit_taxids(hit_data,
                                                         hit_taxa,
                                                         lca_dist)

    informative_tax_ids = get_informative_tax_ids(min_hits,
                                                  min_relative_hits,
                                                  hit_tax_ids,
                                                  total_informative_hits)

    hit_data.inclusion_tree = taxidtool.build_tree(hit_data.tax_id_data,
                                                   None,
                                                   informative_tax_ids,
                                                   [])

    hit_data.gis_to_taxids = taxidtool.build_gis_to_taxids(hit_data.
                                                           inclusion_tree)

    return hit_data


def get_informative_tax_ids(min_hits, min_relative_hits, hit_tax_ids,
                            total_informative_hits):
    """Based on min_hit thresholds taxids are determined to be informative

    The most stringent (highest) of min_hits and min_relative_hits is used as
    a threshold that each tax id must meet or beat in order to determined
    informative.

    Parameters
    ----------
    min_hits : Int
        absolute number of hits a taxid must exhibit to be determined
        informative
    min_relative_hits : Int
        number of hits relative to total number of hits reported that a
        taxid must exhibit to be determined informative
    hit_tax_ids : dict
        tax_id key to number_of_hits value representing the number of hits each
        tax_id was observed to have in the alignmnet file

    Returns
    -------
        list
            tax_ids that have meet or beat minimum hit thresholds

    """
    hit_threshold = max(min_hits,
                        (total_informative_hits/100*min_relative_hits))

    informative_tax_ids = []
    for tax_id, num_hits in hit_tax_ids.items():
        if num_hits >= hit_threshold:
            informative_tax_ids.append(tax_id)

    return informative_tax_ids


def get_hit_taxa(hit_taxa_lines):
    """Builds dictionary from read_ids and the tax_ids it hit

    A set of all tax_ids it hit is constructed for each read_id.

    parameters
    ----------
        hit_taxa_lines : list
            all lines from mg_wrapper output generated in an alignment module

    Returns
    -------
        dict
            read_id key to list of tax_ids value where the read was observed
            to hit the tax_id in an alignment step

    """
    hit_taxa = {}

    for line in hit_taxa_lines:
        this_line = line.rstrip().split(":")
        this_read_id = this_line[1]
        these_hits = set()
        for mm_distance in this_line[1:]:
            for tax_id_hit in mm_distance:
                these_hits.add(tax_id_hit)

        hit_taxa[this_read_id] = list(these_hits)

    return hit_taxa


def get_hit_taxids(hit_data, hit_taxa, lca_dist):
    """Counts the numer of times each tax_id was hit in alignment

    For each tax_id the number of reads that informatively aligned to it are
    counted.

    Parameters
    ----------
        hit_data : object
            containg tree and data recording final informative output
        hit_taxa : dict
            read_id key to list of hit tax_ids value
        lca_dist : Int
            number of edges to be traversed when determining lowest common
            ancestor

    Returns
    -------
        dict
            tax_id key to number of hits to it value

    """
    hit_tax_ids = {}
    total_informative_hits = 0
    for read_id in hit_taxa:
        these_tax_ids_hit = hit_taxa[read_id]
        if len(these_tax_ids_hit) == 1:
            total_informative_hits += 1
            hit_tax_ids = increment_tax_id_hits(
                hit_tax_ids, these_tax_ids_hit[0])

        else:
            informative = True
            ancestor_pool = set(hit_data.tax_id_data[these_tax_ids_hit[0]].
                                parents[-lca_dist:])
            for tax_id_hit in these_tax_ids_hit[1:]:
                this_ancestor_pool = set(hit_data.tax_id_data[tax_id_hit].
                                         parents[-lca_dist:])
                if this_ancestor_pool & ancestor_pool:
                    ancestor_pool |= this_ancestor_pool
                else:
                    break
                    informative = False
            if informative:
                total_informative_hits += 1
                hit_tax_ids = increment_tax_id_hits(
                    hit_tax_ids, these_tax_ids_hit[0])

    return hit_tax_ids, total_informative_hits


def increment_tax_id_hits(ids, id_to_increment):
    """Increments a counter in a dictionary of ids

    Checks that the id_to_increment is present in the dictionary and Increments
    it, if it is not present it adds the id to the dictionary and sets its
    counter to 1.

    parameters
    ----------
        ids : dict
            dictionary of id keys to counter values
        id_to_increment : string
            key in dictionary to increment

    Returns
    -------
        dict
            id keys to counter values

    """
    if id_to_increment in ids:
        ids[id_to_increment] += 1
    else:
        ids[id_to_increment] = 1
    return ids
