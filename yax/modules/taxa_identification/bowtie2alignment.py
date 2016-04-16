import subprocess


def call_bt2_wrapper(allowed_edits,
                     reads_fp,
                     index_fp,
                     output_fp,
                     allowed_threads):
    """Uses the metagenomic wrapper to run bowtie2 alignment.

    The metagenomic wrapper is used to catch the output of bowtie2 and present
    a format that matches each read to the taxids it aligned to in order of
    edit distance.

    Please note that this code is designed specifcally to operate with a SLURM
    task management tool.

    Parameters
    ----------
    allowed_edits : int
        Number of mismatches to allow reporting on
    reads_fp : str
        absolute path to the fasta file containing reads to align
    index_fp : str
        absolute path to the index file set previously computed
    output_fp : str
        absolute path to location and file name where output will be written
    allowed_threads : int
        number of threads to allows bowtie2 to spawn

    Returns
    -------
    None
        Produces an output file containing that results of bowtie2 alignment

    """
    subprocess.call([" ".join(["srun /common/contrib/bin/"
                               "bowtie2_mg_aligner "
                               "-e", allowed_edits,
                               "-q", reads_fp,
                               "-i", index_fp,
                               "-o", output_fp,
                               "-p", allowed_threads])],
                               shell=True)
