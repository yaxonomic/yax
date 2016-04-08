import sys


def preprocessing(nodes_fp, names_fp, gi_taxid_nucl_fp, output_location,
                  project_name):
    ##########################################################################
    # This module, accessed with the tag -build, is responsible for compiling
    # all pertinent information into a single file that can be quickly read by
    # later Tax Tree Clipping actions.
    #
    # Input
    #       nodes_fp    STRING  location of nodes.dmp file
    #       names_fp    STRING  location of names.dmp file
    #       gi_taxid_nucl_fp    STRING  location of gi_taxid_nucl.dmp file
    #       output_location     STRING  desired output location of taxid_data
    #                                   file
    #
    # Output
    #       taxid_data  FILE    file containing a line for each taxid and it's
    #                           associated information
    ###########################################################################
    with open(nodes_fp, 'r') as nodes_fh:
        nodes_lines = nodes_fh.readlines()

    taxid_data = {}
    print("Handling nodes file")
    for line in nodes_lines:
        this_line = line.replace("\t", "").split("|")
        taxid = str(this_line[0].replace(" ", ""))
        if taxid not in taxid_data:
            parent_taxid = [this_line[1].replace(" ", "")]
            print(taxid)
            print(parent_taxid[0])
            if parent_taxid[0] == taxid:
                parent_taxid = []
            rank = this_line[2].lstrip(" ").rstrip(" ")
            taxid_data[taxid] = ["sci_name", [], [], parent_taxid, rank]
            print(str(taxid_data[taxid]))
    print("nodes file complete")

    for taxid in taxid_data:
        print(taxid_data[taxid])

    with open(names_fp, 'r') as names_fh:
        names_lines = names_fh.readlines()

    print("Handling names file")
    for line in names_lines:
        this_line = line.replace("\t", "").split("|")
        taxid = this_line[0].replace(" ", "")
        if taxid in taxid_data and len(this_line) > 3 and this_line[3].rstrip(
                " ").lstrip(" ") == "scientific name":
            taxid_data[taxid][0] = this_line[1].rstrip(" ").lstrip(" ")
    print("names file complete")

    print("Handling gi file")
    with open(gi_taxid_nucl_fp, 'r') as gi_taxid_fh:
        gi_taxid_lines = gi_taxid_fh.readlines()

    for line in gi_taxid_lines:
        this_line = line.split("\t")
        gi = this_line[0]
        taxid = this_line[1].replace(" ", "").rstrip()
        if taxid in taxid_data:
            # print("Adding " + gi + " to " + taxid)
            taxid_data[taxid][1].append(gi)
        else:
            pass
    print("gi file complete")

    for taxid in taxid_data:
        print(taxid_data[taxid])

    print("Adding parent taxids to entries")

    for taxid in taxid_data:
        if len(taxid_data[taxid][3]) > 0:
            parent = taxid_data[taxid][3][-1]
            taxid_data[parent][2].append(taxid)
            id = taxid_data[taxid][3][-1]
            while id != "1":
                id = taxid_data[id][3][-1]
                taxid_data[taxid][3].insert(0, id)

    print("parent taxid processing complete")

    for taxid in taxid_data:
        print(taxid_data[taxid])

    print("Beginning taxid_data output")
    output_fh = open(output_location + "taxid_data_" + project_name + ".txt",
                     'w')

    for taxid in taxid_data:
        output_fh.write(str(taxid) + "\t")
        for item in taxid_data[taxid]:
            output_fh.write(str(item) + "\t")
        output_fh.write("\n")
    print("Output complete")


def tree_builder(input_taxid_data_fp, sequences_input_fp, taxids_to_include,
                 taxids_to_exclude, truncation_level,
                 project_name, output_location):
    ##########################################################################
    # Input
    #   input_taxid_data_fp
    #   sequences_input_fp
    #   taxids_to_include
    #   taxids_to_exclude
    #   truncation_level
    #   project_name
    #   output_location
    #
    # Description
    #   Driver for the -build functionality. Responsible for running checks and
    #   overlaps on created trees then finally calling for the output into
    #   .tree and .fasta formats
    ###########################################################################
    print("input_taxid_data_fp : " + str(input_taxid_data_fp))
    print("sequences_input_fp : " + str(sequences_input_fp))
    print("taxids_to_include : " + str(taxids_to_include))
    print("taxids_to_exclude : " + str(taxids_to_exclude))
    print("truncations_level : " + str(truncation_level))
    print("project_name : " + str(project_name))

    taxid_data = get_input_taxid_data(input_taxid_data_fp)

    exclusion_roots = []
    exclusion_tree = {}
    if taxids_to_exclude:
        print("Handling exclusions")
        with open(taxids_to_exclude, 'r') as exclusive_fh:
            for line in exclusive_fh:
                exclusion_roots.append(line.rstrip())
            exclusion_tree = build_branch(taxid_data, exclusion_roots,
                                          truncation_level)
        print("exclusions complete")

    print("Handling inclusions")
    inclusion_roots = []
    with open(taxids_to_include, 'r') as inclusive_fh:
        for line in inclusive_fh:
            this_line = line.strip()
            if taxids_to_exclude:
                if this_line not in exclusion_tree:
                    inclusion_roots.append(this_line)
                else:
                    print(
                        "Root taxid {0} found inside existing exclusion "
                        "branch".format(line.rstrip()))
            else:
                inclusion_roots.append(this_line)
        print("Calling build_branch on inclusion roots")
        print("inclusion_roots = " + str(inclusion_roots))
        inclusion_tree = build_branch(taxid_data, inclusion_roots,
                                      truncation_level)
    print("inclusions complete")

    print("Length of inclusion_tree = " + str(len(inclusion_tree)))

    # Removes taxids in exclusion tree from inclusion tree if one exists
    if taxids_to_exclude:
        print("Removing exclusive taxids from inclusion tree")
        for taxid in exclusion_tree:
            inclusion_tree.pop(taxid, None)
        print("Exclusion removal complete")

    print("SIZE OF INCLUSION TREE : " + str(len(inclusion_tree)))
    gis_to_taxids = build_gis_to_taxids(inclusion_tree)

    output_sequences(taxid_data, inclusion_tree, gis_to_taxids,
                     sequences_input_fp, output_location, project_name,
                     truncation_level)
    output_tree(taxid_data, inclusion_tree, output_location, project_name)


def get_input_taxid_data(input_taxid_data_fp):
    ##########################################################################
    # Input
    #   input_taxid_data_fp STRING  location of taxid_data as previously
    #                               computed
    #
    # Output
    #   taxid_data  DICT    Recreation of precomputed taxid_data structure
    #
    # Description
    #   Reads in the preprocessed taxid_data file to a dictionary which the
    #   -clip process uses.
    ###########################################################################
    print("Entering get_input_taxid_data")

    taxid_data = {}
    with open(input_taxid_data_fp, 'r') as taxid_data_fh:
        counter = 0
        for line in taxid_data_fh:
            if counter % 10000 == 0:
                print(counter)
            counter += 1
            this_line = line.rstrip().split("\t")
            taxid = this_line[0]
            sci_name = this_line[1]
            assoc_gis = this_line[2].rstrip("]").lstrip("[").replace("'", "")\
                .replace(" ", "").split(",")
            children = list((this_line[3].rstrip("]").lstrip("[").
                             replace("'", "").replace(" ", "").split(",")))
            parents = list((this_line[4].rstrip("]").lstrip("[").
                            replace("'", "").replace(" ", "").split(",")))
            rank = this_line[5]

            taxid_data[taxid] = [sci_name, assoc_gis, children, parents, rank,
                                 0]

    print("Exiting get_input_taxid_data")
    return taxid_data


def build_branch(taxid_data, inclusion_roots, truncation_level):
    ##########################################################################
    # Input
    #   taxid_data  DICT    representation of taxid tree from NCBI
    #   root_taxids LIST    taxids to be used as roots of tree branches
    #
    # Output
    #   this_branch DICT    representation of branches built from roots
    #
    # Description
    #   Responsible for building the branches from the provided roots in both
    #   exclusion_roots and inclusion_roots. It does so by simply copying
    #   dictionary entries from taxid_data to this_branch.
    ###########################################################################
    print("Entering build_branch")

    this_branch = {}
    taxids_to_add = set()
    # inclusion_roots_check = set(inclusion_roots)
    for taxid in inclusion_roots:
        taxids_to_add.add(taxid)
    while len(taxids_to_add) > 0:
        taxids_found = set()
        for taxid in taxids_to_add:
            for id in taxid_data[taxid][2]:
                if id != "":
                    taxids_found.add(id)
            this_branch[taxid] = taxid_data[taxid]
        taxids_to_add = set()
        for taxid in taxids_found:
            taxids_to_add.add(taxid)

    print("Exiting build_branch")
    return this_branch


def build_gis_to_taxids(tree):
    ##########################################################################
    # Builds a dictionary where each gi key is associeated with a taxid value
    # Input:
    #       tree    DICT    a constructed tree in the form of a dictionary
    #
    # Output:
    #       gis_to_taxids   DICT    gi key with taxid value
    ###########################################################################
    print("Entering build_gis_to_taxids")

    gis_to_taxids = {}
    for taxid in tree:
        for gi in tree[taxid][1]:
            gis_to_taxids[gi] = taxid

    print("Exiting build_gis_to_taxids")
    return gis_to_taxids


def output_sequences(taxid_data, inclusion_tree, gis_to_taxids,
                     sequences_input_fp, output_location, project_name,
                     truncation_level):
    ##########################################################################
    # Input
    #   taxid_data          DICT    read in from taxid_data; representation of
    #                               the entire tree
    #   inclusion_tree      DICT    built using provided taxid roots; the
    #                               specific tree of interest
    #   gis_to_taxids       DICT    a lookup table of gi key to taxid value for
    #                               reverse lookup and association
    #   sequences_input_fp  STRING  absolute file path to the fasta file
    #                               containing sequences to search
    #   output_location     STRING  directory destination of desired output
    #   project_name        STRING  name used for identifying this run
    #   truncation_level    STRING  level at which leaf nodes will be rolled up
    #                               in sequence association only
    #
    # Output
    #   <project_name>.fasta   FILE fasta formatted output of sequences found
    #                               to be associated with the trees built on
    #                               provided roots. The header is in the format
    #                               ><gi>-<taxid>
    #
    # Description
    #   Writes a .fasta output of the sequences found to be associated with the
    #   trees built upon branch roots provided
    ###########################################################################
    print("Entering output_sequences")

    print_line = False
    taxid_counts = {}
    with open(sequences_input_fp, 'r') as sequences_fh:
        with open(output_location + project_name + "_seqs.fasta",
                  'w') as output_fh:
            for counter, line in enumerate(sequences_fh):
                if counter % 100000 == 0:
                    print(counter)
                if (line[0] != ">" and print_line):
                    output_fh.write(line)
                elif line[0] == ">":
                    gi = line.split(" ")[1].split(":")[1]
                    # name = " ".join(line.rstrip().split(" ")[2:])
                    if gi in gis_to_taxids:
                        taxid = str(gis_to_taxids[gi])
                        taxid_to_increment = str(gis_to_taxids[gi])
                        if truncation_level and\
                                taxid_data[taxid][4] != truncation_level:
                            for id in taxid_data[taxid][3]:
                                if taxid_data[id][4] == truncation_level:
                                    taxid = id
                        if taxid_to_increment in taxid_counts:
                            taxid_counts[taxid_to_increment] += 1
                        else:
                            taxid_counts[taxid_to_increment] = 1
                        print_line = True
                        output_fh.write(">" + gi + "-" + taxid + "\n")
                    else:
                        print_line = False
                else:
                    continue

    # Updating gi counts in tree
    print("Updating gi counts in tree")
    for taxid in taxid_counts:
        count = taxid_counts[taxid]
        # print("Count : " + str(count))
        taxid_data[taxid][5] += count
        # print("Taxid : " + str(taxid))
        for id in inclusion_tree[taxid][3]:
            try:
                taxid_data[id][5] += count
                # print(str(id))
            except IndexError:
                print("id not in taxid_data : " + str(id))

    print("Exiting output_sequences")


def output_tree(taxid_data, inclusion_tree, output_location, project_name):
    ##########################################################################
    ###########################################################################
    print("Entering output_tree")

    print(len(inclusion_tree))

    with open(output_location + project_name + ".tree", 'w') as output_fh:
        for taxid in inclusion_tree:
            print(taxid)
            print(inclusion_tree[taxid][2])
            print(inclusion_tree[taxid][5])
            if inclusion_tree[taxid][2] == [''] and\
                    inclusion_tree[taxid][5] != 0:
                print("inside if")
                output_string = ""
                for id in taxid_data[taxid][3]:
                    output_string += id + "\t" + taxid_data[id][
                        0] + "\t" + str(taxid_data[id][5]) + "\t"
                output_string += taxid + "\t" + taxid_data[taxid][
                    0] + "\t" + str(taxid_data[taxid][5])
                output_fh.write(output_string + "\n")

    print("Exiting output_tree")


if __name__ == "__main__":
    ##########################################################################
    # Input
    #  -build
    #       nodes_fp            STRING  absolute path to the nodes.dmp file
    #       names_fp            STRING  absolute path to the names.dmp file
    #       gi_taxid_nucl_fp    STRING  absolute path to the gi_taxid_nucl.dmp
    #                                   file
    #       output_location     STRING  absolute path to the desired
    #                                   destination of output
    #       project_name        STRING  name that will be used for .tree and
    #                                   .fasta output for identification
    #                                   purposes
    #  -clip
    #       input_taxid_data_fp STRING  absolute path to taxid_data file
    #       sequences_input_fp  STRING  absolute path to fasta file of
    #                                   sequences to investigate
    #       taxids_to_include   STRING  absolute path to .txt file containing
    #                                   intended branch roots; one taxid per
    #                                   line
    #       taxids_to_exclude   STRING  absolute path to .txt file of intended
    #                                   exclusion roots; one taxid per line
    #       output_location     STRING  absolute path to directory of intended
    #                                   output
    #       truncation_level    STRING  level of taxonomic tree to roll
    #                                   branches up to
    #       project_name        STRING  name that will be used for .tree and
    #                                   .fasta output for identification
    #                                   purposes
    #
    # Description
    #   When called from the command line this function takes in command line
    #   arguments to populate the applicaable variables. The first argument
    #   -build/-clip is what will determine how arguments are assigned to
    #   variables as well as which component is run, the preprocessing or
    #   clipping sections, -build and -clip respectively
    ###########################################################################
    if sys.argv[1] == "-build":
        nodes_fp = sys.argv[2]
        names_fp = sys.argv[3]
        gi_taxid_nucl_fp = sys.argv[4]
        output_location = sys.argv[5]
        project_name = sys.argv[6]

        print("Calling preprocessing functionality")
        preprocessing(nodes_fp, names_fp, gi_taxid_nucl_fp, output_location,
                      project_name)

    elif sys.argv[1] == "-clip":
        input_taxid_data_fp = sys.argv[2]
        sequences_input_fp = sys.argv[3]
        taxids_to_include = sys.argv[4]
        if sys.argv[5] != "none":
            taxids_to_exclude = sys.argv[5]
        else:
            taxids_to_exclude = False
        output_location = sys.argv[6]
        if sys.argv[7] != "none":
            truncation_level = sys.argv[7]
        else:
            truncation_level = False
        project_name = sys.argv[8]

        print("Calling processing functionality")
        tree_builder(input_taxid_data_fp, sequences_input_fp,
                     taxids_to_include, taxids_to_exclude, truncation_level,
                     project_name, output_location)
