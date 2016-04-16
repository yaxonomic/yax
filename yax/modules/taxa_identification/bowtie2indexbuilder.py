import subprocess


def build_index(fasta_fp, index_fp):
    """Builds bowtie2 index file set

    Requiring a fasta file to build from and index_fp as a destination for the
    created index file set `build_index` creates a bowtie2 index file set

    Parameters
    ----------
    fasta_fp : str
        abosolute path to fasta file to generate a bowtie2 index file set

    index_fp : str
        absolute path to the location where the index file set should exist

    Returns
    -------
    None
        Only the bowtie2 index file set is genenerated


    """
    subprocess.call([" ".join(["bowtie2-build", fasta_fp, index_fp])],
                    shell=True)
