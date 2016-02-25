def preprocessing(nodes_fp, names_fp, gi_taxid_nucl_fp, output_location,
                  project_name):
    ###########################################################################
    # This module, accessed with the tag -build, is responsible for compiling
    # all pertinent information into a single
    # file that can be quickly read by later Tax Tree Clipping actions.
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
    #       associated information
    #
    ###########################################################################
    with open(nodes_fp, 'r') as nodes_fh:
        nodes_lines = nodes_fh.readlines()

    taxid_data = {}
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

    for line in names_lines:
        this_line = line.replace("\t", "").split("|")
        taxid = this_line[0].replace(" ", "")
        if taxid in taxid_data and len(this_line) > 3 and this_line[3]. \
                rstrip(" ").lstrip(" ") == "scientific name":
            taxid_data[taxid][0] = this_line[1].rstrip(" ").lstrip(" ")

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

    for taxid in taxid_data:
        print(taxid_data[taxid])

    for taxid in taxid_data:
        if len(taxid_data[taxid][3]) > 0:
            parent = taxid_data[taxid][3][-1]
            taxid_data[parent][2].append(taxid)
            id_ = taxid_data[taxid][3][-1]
            while id_ != "1":
                id_ = taxid_data[id_][3][-1]
                taxid_data[taxid][3].insert(0, id_)

    for taxid in taxid_data:
        print(taxid_data[taxid])

    output_fh = open(output_location + "taxid_data_" + project_name + ".txt",
                     'w')

    for taxid in taxid_data:
        output_fh.write(str(taxid) + "\t")
        for item in taxid_data[taxid]:
            output_fh.write(str(item) + "\t")
        output_fh.write("\n")


def tree_builder(input_taxid_data_fp, sequences_input_fp, taxids_to_include,
                 taxids_to_exclude, truncation_level, project_name,
                 output_location):
    ###########################################################################
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
    #   overlaps on created trees then finally
    #   calling for the output into .tree and .fasta formats
    ###########################################################################
    taxid_data = get_input_taxid_data(input_taxid_data_fp)

    exclusion_roots = []
    exclusion_tree = {}
    if taxids_to_exclude:
        with open(taxids_to_exclude, 'r') as exclusive_fh:
            for line in exclusive_fh:
                exclusion_roots.append(line.rstrip())
            exclusion_tree = build_branch(taxid_data, exclusion_roots)

    inclusion_roots = []
    with open(taxids_to_include, 'r') as inclusive_fh:
        for line in inclusive_fh:
            this_line = line.strip()
            if taxids_to_exclude:
                if this_line not in exclusion_tree:
                    inclusion_roots.append(this_line)
                else:
                    print("Root taxid {0} found inside existing exclusion "
                          "branch".format(line.rstrip()))
            else:
                inclusion_roots.append(this_line)
        print("Calling build_branch on inclusion roots")
        print("inclusion_roots = " + str(inclusion_roots))
        inclusion_tree = build_branch(taxid_data, inclusion_roots)

    print("Length of inclusion_tree = " + str(len(inclusion_tree)))

    # Removes taxids in exclusion tree from inclusion tree if one exists
    if taxids_to_exclude:
        for taxid in exclusion_tree:
            inclusion_tree.pop(taxid, None)
    print("SIZE OF INCLUSION TREE : " + str(len(inclusion_tree)))
    gis_to_taxids = build_gis_to_taxids(inclusion_tree)

    output_sequences(taxid_data, inclusion_tree, gis_to_taxids,
                     sequences_input_fp, output_location, project_name,
                     truncation_level)
    output_tree(taxid_data, inclusion_tree, output_location, project_name)


def get_input_taxid_data(input_taxid_data_fp):
    ###########################################################################
    # Input
    #   input_taxid_data_fp STRING  location of taxid_data as previously
    #   computed
    #
    # Output
    #   taxid_data  DICT    Recreation of precomputed taxid_data structure
    #
    # Description
    #   Reads in the preprocessed taxid_data file to a dictionary which the
    #   -clip process uses.
    ###########################################################################
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
            assoc_gis = this_line[2].rstrip("]").lstrip("[").replace("'", "").\
                replace(" ", "").split(",")
            children = list((this_line[3].rstrip("]").lstrip("[").
                             replace("'", "").replace(" ", "").split(",")))
            parents = list((this_line[4].rstrip("]").lstrip("[").
                            replace("'", "").replace(" ", "").split(",")))
            rank = this_line[5]

            taxid_data[taxid] = [sci_name, assoc_gis, children, parents, rank,
                                 0]

    return taxid_data


def build_branch(taxid_data, inclusion_roots):
    ###########################################################################
    # Input
    #   taxid_data  DICT    representation of taxid tree from NCBI
    #   root_taxids LIST    taxids to be used as roots of tree branches
    #
    # Output
    #   this_branch DICT    representation of branches built from roots
    #
    # Description
    #   Responsible for building the branches from the provided roots in both
    #   exclusion_roots and inclusion_roots. It
    #   does so by simply copying dictionary entries from taxid_data to
    #   this_branch.
    ###########################################################################
    this_branch = {}
    taxids_to_add = set()
    for taxid in inclusion_roots:
        taxids_to_add.add(taxid)
    while len(taxids_to_add) > 0:
        taxids_found = set()
        for taxid in taxids_to_add:
            for id_ in taxid_data[taxid][2]:
                if id_ != "":
                    taxids_found.add(id_)
            this_branch[taxid] = taxid_data[taxid]
        taxids_to_add = set()
        for taxid in taxids_found:
            taxids_to_add.add(taxid)

    return this_branch


def build_gis_to_taxids(tree):
    ###########################################################################
    # Builds a dictionary where each gi key is associeated with a taxid value
    # Input:
    #       tree    DICT    a constructed tree in the form of a dictionary
    #
    # Output:
    #       gis_to_taxids   DICT    gi key with taxid value
    ###########################################################################
    gis_to_taxids = {}
    for taxid in tree:
        for gi in tree[taxid][1]:
            gis_to_taxids[gi] = taxid

    return gis_to_taxids


def output_sequences(taxid_data, inclusion_tree, gis_to_taxids,
                     sequences_input_fp, output_location, project_name,
                     truncation_level):
    ###########################################################################
    # Input
    #   taxid_data          DICT    read in from taxid_data; representation of
    #                               the entire tree
    #   inclusion_tree      DICT    built using provided taxid roots; the
    #                               specific tree of interest
    #   gis_to_taxids       DICT    a lookup table of gi key to taxid value for
    #                               reverse lookup and association
    #   sequences_input_fp  STRING  absolute file path to the fasta file
    #                               containg sequences to search
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
    print_line = False
    taxid_counts = {}
    with open(sequences_input_fp, 'r') as sequences_fh:
        with open(output_location + project_name + "_seqs.fasta", 'w') as \
                output_fh:
            for counter, line in enumerate(sequences_fh):
                if counter % 100000 == 0:
                    print(counter)
                if line[0] != ">" and print_line:
                    output_fh.write(line)
                elif line[0] == ">":
                    gi = line.split(" ")[1].split(":")[1]
                    if gi in gis_to_taxids:
                        taxid = str(gis_to_taxids[gi])
                        taxid_to_increment = str(gis_to_taxids[gi])
                        if truncation_level and taxid_data[taxid][4] != \
                                truncation_level:
                            for id_ in taxid_data[taxid][3]:
                                if taxid_data[id_][4] == truncation_level:
                                    taxid = id_
                        if taxid_to_increment in taxid_counts:
                            taxid_counts[taxid_to_increment] += 1
                        else:
                            taxid_counts[taxid_to_increment] = 1
                        print_line = True
                        output_fh.write(">" + taxid + "\n")
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
        for id_ in inclusion_tree[taxid][3]:
            try:
                taxid_data[id_][5] += count
                # print(str(id_))
            except IndexError:
                print("id_ not in taxid_data : {0}".format(str(id_)))


def output_tree(taxid_data, inclusion_tree, output_location, project_name):
    ###########################################################################
    ###########################################################################
    print(len(inclusion_tree))

    with open(output_location + project_name + ".tree", 'w') as output_fh:
        for taxid in inclusion_tree:
            print(taxid)
            print(inclusion_tree[taxid][2])
            print(inclusion_tree[taxid][5])
            if inclusion_tree[taxid][2] == [''] and inclusion_tree[taxid][5] \
                    != 0:
                print("inside if")
                output_string = ""
                for id_ in taxid_data[taxid][3]:
                    output_string += id_ + "\t" + taxid_data[id_][0] + "\t" + \
                        str(taxid_data[id_][5]) + "\t"
                output_string += taxid + "\t" + taxid_data[taxid][0] + "\t" + \
                    str(taxid_data[taxid][5])
                output_fh.write(output_string + "\n")
