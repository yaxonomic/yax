from yax.state.type.artifact import Artifact
from yax.shared.utilities import taxidtool


class TaxIDData(Artifact):
    def __init__(self, completed):
        self.tax_id_data = None

        if complete:
            self.tax_id_data = taxidtool.parse_taxid_data(tax_id_data_fp)

    def __complete__(self):
        taxidtool.write_taxid_data(self.tax_id_data, self.data_dir)
