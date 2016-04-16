from yax.artifacts.identified_taxa import IdentifiedTaxa
from yax.artifacts.prepared_reads import PreparedReads
from yax.state.type.parameter import Str, Int

import bowtie2indexbuilder
import bowtie2alignment

def main(working_dir,
         output,
         details,
         allowed_edits: Int=0,
         reads_fp: PreparedReads,
         reference_fp: File,
         allowed_threads: Int=0) -> (BT2Index, IdentifiedTaxa):
    """Builds bowtie2 index and performs a bowtie2 alignment.

    The bowtie2 alignment is done using the metagenomic wrapping tool to handle
    the output. It is more likely that the bowtie2 index will have been created
    in a previous run since it is fairly unlikely to change from one run to
    another particularly in the survey step.

    Parameters
    ----------
    allowed_edits : int
        Number of mismatches to allow reporting on
    reads_fp : str
        absolute path to the fasta file containing reads to align
    reference_fp : File
        absolute path to the fasta file containing the references to build an
        index from
    index_fp : str
        absolute path to the index file set previously computed
    output_fp : str
        absolute path to location and file name where output will be written
    allowed_threads : int
        number of threads to allows bowtie2 to spawn

    Returns
    -------
    None
        Generates a bowtie2 index and bowtie2 wrapper output file

    """
    BT2Index, IdentifiedTaxa = output

    if not BT2Index.is_complete:
        bowtie2indexbuilder()
        BT2Index.complete()

    bowtie2alignment()

    return BT2Index, IdentifiedTaxa
