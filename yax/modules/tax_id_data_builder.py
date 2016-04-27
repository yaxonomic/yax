from yax.artifacts.tax_id_data import TaxIDData
from yax.state.type.parameter import file
from yax.shared.utilities import taxidtool


def main(working_dir, output, details, nodes_dmp: File, names_dmp: File,
         gi_taxid_nucl_fp: File) -> TaxIDData:
    """Description

    Detailed Description

    Parameters
    ----------


    Returns
    -------


    """
    tax_id_data = output

    tax_id_data.tax_id_data = taxidtool.build_taxid_data(nodes_dmp,
                                             names_dmp,
                                             gi_taxid_nucl_fp)

    output.complete

    return output
