import subprocess


def build_index(reference_inlist, output_dir):
    ###############################################################
    # Building Index                                              #
    ###############################################################
    print("build_index : Enter")

    reference_paths = []
    reference_names = []

    with open(reference_inlist, 'r') as references:
        for reference in references:
            reference_paths.append(reference.rstrip())
            reference_names.append(reference.split("/")[-1].split(".")[0])

    for ref_num, reference_path in enumerate(reference_paths):
        command = "bowtie2-build " + reference_path + " " + output_dir + \
                  reference_names[ref_num] + "_index"
        try:
            subprocess.call([command], shell=True)
        except subprocess.CalledProcessError:
            print("RUN_ALIGNEMENT_FOR_REFERENCE: Unable to build index")

    print("build_index : Exit")
