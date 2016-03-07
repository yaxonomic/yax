import subprocess


def run_alignment(reference_inlist, index_dir, read_inlist, output_dir):
    ###############################################################
    # Running Alignme                                             #
    ###############################################################
    print("run_alignment : Enter")
    reference_files = []
    reference_names = []
    read_files = []
    read_names = []

    print("run_alignment : working through references")
    with open(reference_inlist, 'r') as reference_list:
        for path in reference_list:
            this_path = path.rstrip()
            reference_files.append(this_path)
            reference_names.append(this_path.split("/")[-1].split(".")[0])

    print("run_alignment : working through reads")
    with open(read_inlist, 'r') as read_list:
        for path in read_list:
            this_path = path.rstrip()
            read_files.append(this_path)
            read_names.append(this_path.split("__")[1])

    sam_outputs = []
    for ref_num, reference_file in enumerate(reference_files):
        for read_num, read_file in enumerate(read_files):
            print("run_alignment : running taxa_identification of " +
                  read_names[read_num] + " to " + reference_names[ref_num])
            output = output_dir + reference_names[ref_num] + "__" + \
                read_names[read_num] + ".sam"
            sam_outputs.append(output)
            command = "bowtie2 -a -f -x " + index_dir + \
                      reference_names[ref_num] + "_index -U " + \
                      read_file + " -S " + output

            try:
                subprocess.call([command], shell=True)
            except subprocess.CalledProcessError:
                print("RUN_ALIGNEMENT_FOR_REFERENCE: Unable to run bowtie2: " +
                      reference_names[ref_num] + "_" +

                      read_names[read_num] + ".sam")

    print("run_alignment : Exit")
