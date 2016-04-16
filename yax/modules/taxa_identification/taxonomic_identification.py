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
         index_fp: Str,
         output_fp: Str,
         allowed_threads: Int=0) -> IdentifiedTaxa:
    """

    Stuff

    Parameters
    ----------


    Returns
    -------


    """
