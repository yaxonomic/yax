import collections
import json
import os


def parse_names_dmp(names_fp):
    results = {}
    with open(names_fp, mode='r') as fh:
        lines = fh.readlines()

    for line in lines:
        line = line.rstrip('\t|\n')
        taxid, scientific_name, _, name_type = line.split("\t|\t", 4)
        if name_type == "scientific name":
            results[taxid] = scientific_name

    return results


def parse_gi_taxid_dmp(gi_taxid_nucl_fp):
    results = {}
    with open(gi_taxid_nucl_fp, mode='r') as fh:
        lines = fh.readlines()

    for line in lines:
        gi, taxid = line.strip().split("\t")
        if taxid in results:
            results[taxid].append(gi)
        else:
            results[taxid] = [gi]

    return results


NodeRecord = collections.namedtuple(
    "NodeRecord", (
        "taxid",
        "parent_taxid",
        "rank"))


def parse_nodes_dmp(nodes_fp):
    results = {}
    with open(nodes_fp, mode='r') as fh:
        lines = fh.readlines()

    for line in lines:
        taxid, parent_taxid, rank, _ = \
            line.split("\t|\t", 3)
        results[taxid] = NodeRecord(taxid, parent_taxid, rank)

    return results


TaxIDDataRecord = collections.namedtuple(
    "TaxIDDataRecord", (
        "taxid",
        "sci_name",
        "assoc_gis",
        "children",
        "parents",
        "rank",
        "num_gis_assoc"))


def parse_taxid_data(input_taxid_data_fp):
    """Reads in provided taxid_data file to python dictionary.

    Reads precomputed taxid_data file back into a python dictionary. This new
    dictionary will represent whatever tree was used to build the taxid_data
    file.

    Parameters
    ----------
    input_taxid_data_fp : str
        location of precomputed taxid_data file

    Returns
    -------
    taxid_data : dict
        contains all taxids found in provided taxid_data

    See Also
    --------
    write_taxid_data

    """
    num_gis_assoc = 0
    results = {}
    with open(input_taxid_data_fp, mode='r') as fh:
        lines = fh.readlines()

    for line in lines:
        taxid, sci_name, assoc_gis, children, ancestors, rank = \
            line.rstrip().split("\t")

        assoc_gis = json.loads(assoc_gis)
        children = json.loads(children)
        ancestors = json.loads(ancestors)

        results[taxid] = TaxIDDataRecord(taxid, sci_name, assoc_gis,
                                         children, ancestors, rank,
                                         num_gis_assoc)

    return results


def build_taxid_data(nodes_fp, names_fp, gi_taxid_nucl_fp):
    """Builds taxid_data.

    Based on NCBI taxa.dmp files the taxid_data

    Parameters
    ----------
    nodes_fp : str
        location of nodes.dmp file
    names_fp : str
        location of names.dmp file
    gi_taxid_nucl_fp : str
        location of gi_taxid_nucl.dmp file

    Returns
    -------
    dict
        Big Dictionary

    See Also
    --------
    parse_nodes_dmp
    parse_names_dmp
    parse_gi_taxid_dmp

    """
    nodes = parse_nodes_dmp(nodes_fp)
    names = parse_names_dmp(names_fp)
    taxid_gi = parse_gi_taxid_dmp(gi_taxid_nucl_fp)

    if not (len(nodes) == len(names) >= len(taxid_gi)):
        raise ValueError("NCBI dump files do not make sense")

    taxid_data = {}
    for taxid in nodes:
        children = []
        parents = []
        taxid_data[taxid] = TaxIDDataRecord(taxid,
                                            names[taxid],
                                            taxid_gi.get(taxid, []),
                                            children,
                                            parents,
                                            nodes[taxid].rank,
                                            0)

        current_taxid = taxid

        while nodes[current_taxid].taxid != \
                nodes[current_taxid].parent_taxid:
            parents.insert(0, nodes[current_taxid].parent_taxid)
            current_taxid = nodes[current_taxid].parent_taxid

    for node_record in nodes.values():
        if node_record.taxid == '1':
            continue
        taxid_data[node_record.parent_taxid].children.\
            append(node_record.taxid)

    return taxid_data


def write_taxid_data(taxid_data, output_fp):
    """Write TaxID records to a file.

    Parameters
    ----------
    taxid_data : iterable of TaxIDDataRecord
        The data to serialize
    output_fp : str
        The filepath to write the data to.

    Returns
    -------
    None
        Writes `taxid_data` to `output_fp`

    See Also
    --------
    parse_taxid_data

    """
    output = []
    for record in taxid_data.values():
        output.append('\t'.join([
            record.taxid,
            record.sci_name,
            json.dumps(record.assoc_gis),
            json.dumps(record.children),
            json.dumps(record.parents),
            record.rank]))

    with open(output_fp, mode="w") as fh:
        fh.write("\n".join(output))


def build_tree(taxid_data, sequences_input_fp, taxids_to_include_fp,
               taxids_to_exclude_fp, truncation_level):
    """Builds indicated taxonomic subtree.

    Based on input taxids a subtree(s) is/are built containing all organisms
    above or at the indicated `truncation_level`. These trees are represented
    to the user in two output files .seqs and .tree.

    Parameters
    ----------
    input_taxid_data_fp : str
        location of preprocessed taxid_data file
    sequences_input_fp : str
        location of FASTA formatted file containing sequences to filter for
        inclusion in .seqs output
    taxids_to_include_fp : str
        location of file containing taxids to include in output trees
    taxids_to_exclude_fp : str
        location of file containing taxids to exclude from output treese ac

    Returns
    -------
    inclusion_tree : dict
        similar to taxid_data but only representing the taxids of interest

    """
    exclusion_roots = []
    if taxids_to_exclude_fp:
        with open(taxids_to_exclude_fp, mode='r') as fh:
            for line in fh:
                exclusion_roots.append(line.strip())

    exclusion_tree = build_branch(taxid_data, exclusion_roots,
                                  truncation_level)

    inclusion_roots = []
    with open(taxids_to_include_fp, mode='r') as fh:
        for line in fh:
            this_line = line.strip()
            if exclusion_roots:
                if this_line in exclusion_tree:
                    raise ValueError("TaxID %s found inside exclusion tree"
                                     % this_line)
                else:
                    inclusion_roots.append(this_line)

    inclusion_tree = build_branch(taxid_data,
                                  inclusion_roots,
                                  truncation_level)

    # Removes taxids in exclusion tree from inclusion tree if one exists
    if exclusion_roots:
        for taxid in exclusion_tree:
            inclusion_tree.pop(taxid, None)

    return inclusion_tree


def build_branch(taxid_data, inclusion_roots):
    """Builds branch of taxonomy tree based on `inclusion_roots`.

    Responsible for building the branches from the provided roots in both
    exclusion_roots and inclusion_roots. It does so by simply copying
    dictionary entries from taxid_data to this_branch.

    Parameters
    ----------
    taxid_data : dict
        representation of tree to be considered
    root_taxids : list
        taxids to be used as roots of tree branches

    Returns
    -------
    this_branch : dict
        representation of branches built from roots

    """
    this_branch = {}
    taxids_to_add = set(inclusion_roots)

    while taxids_to_add:
        taxids_found = set()
        for taxid in taxids_to_add:
            for child_taxid in taxid_data[taxid].children:
                taxids_found.add(child_taxid)
            this_branch[taxid] = taxid_data[taxid]
        taxids_to_add = set(taxids_found)

    return this_branch


def build_gis_to_taxids(tree):
    """Builds reverse lookup table of gis to taxids

    Builds a dictionary where each gi key is associeated with a taxid value.

    Parameters
    ----------
    tree : dict
        the tree to build a reverse lookup for

    Returns
    -------
    gis_to_taxids : dict
        gi keys with taxids values

    """
    results = {}
    for taxid, record in tree.items():
        for gi in record.assoc_gis:
            results[gi] = taxid

    return results


def output_sequences(taxid_data, inclusion_tree, gis_to_taxids,
                     sequences_input_fp, output_fp, truncation_level):
    """Outputs branch sequences

    Filters through provided NCBI FASTA formatted file and outputs the
    sequences included in the built branches to file.

    Parameters
    ----------
    taxid_data : dict
        read in from taxid_data; representation of the entire tree
    inclusion_tree : dict
        built using provided taxid roots; the specific tree of interest
    gis_to_taxids : dict
        a lookup table of gi key to taxid value for reverse lookup and
        association
    sequences_input_fp : str
        absolute file path to the fasta file containing sequences to search
    output_location : str
        directory destination of desired output
    project_name : str
        name used for identifying this run
    truncation_level : str
        level at which leaf nodes will be rolled up in sequence association
        only

    Returns
    -------
    None
        Writes sequence data to indicated FASTA formatted file.
    """
    print_line = False
    taxid_counts = {}
    with open(sequences_input_fp, 'r') as seqs_fh:
        with open(os.path.join(output_fp, "_seqs.fasta"), mode='w')\
                as output_fh:
            for line in seqs_fh:
                if (line[0] != ">" and print_line):
                    output_fh.write(line)
                elif line[0] == ">":
                    gi = line.split(" ")[1].split(":")[1]
                    if gi in gis_to_taxids:
                        taxid = str(gis_to_taxids[gi])
                        taxid_to_increment = taxid
                        if truncation_level and\
                                taxid_data[taxid].rank != truncation_level:
                            for this_taxid in taxid_data[taxid].parents:
                                if taxid_data[this_taxid].rank ==\
                                        truncation_level:
                                    taxid = this_taxid
                        if taxid_to_increment in taxid_counts:
                            taxid_counts[taxid_to_increment] += 1
                        else:
                            taxid_counts[taxid_to_increment] = 1
                        print_line = True
                        output_fh.write("".join([">", gi, "-", taxid, "\n"]))
                    else:
                        print_line = False
                else:
                    continue

    # Updating gi counts in tree
    for taxid in taxid_counts:
        count = taxid_counts[taxid]
        taxid_data[taxid].num_gis_assoc += count
        for this_taxid in inclusion_tree[taxid].parents:
            try:
                taxid_data[this_taxid].num_gis_assoc += count
            except IndexError:
                raise ValueError("this_taxid not in taxid_data : %s" %
                                 this_taxid)


def output_tree(taxid_data, inclusion_tree, output_fp):
    """Writes dsv(|) file of taxonomy trees

    Description

    Parameters
    ----------
    taxid_data : dict
        read in from taxid_data; representation of the entire tree
    inclusion_tree : dict
        built using provided taxid roots; the specific tree of interest
    output_location : str
        directory destination of desired output
    project_name : str
        name used for identifying this run

    Returns
    -------
    None
        Writes dsv(|) file of taxonomy trees


    """
    with open(os.path.join(output_fp, ".tree"), mode='w') as output_fh:
        for taxid in inclusion_tree:
            if inclusion_tree[taxid].children == [] and\
                    inclusion_tree[taxid].num_gis_assoc != 0:
                output_string = ""
                for this_taxid in taxid_data[taxid][3]:
                    output_string = "".join([output_string, this_taxid, "\t",
                                             taxid_data[this_taxid].sci_name,
                                             "\t", str(taxid_data[this_taxid].
                                                       num_gis_assoc), "\t"])
                output_string = "".join([output_string, taxid, "\t",
                                         taxid_data[taxid].sci_name, "\t",
                                         str(taxid_data[taxid].num_gis_assoc)])
                output_fh.write("".join([output_string, "\n"]))
