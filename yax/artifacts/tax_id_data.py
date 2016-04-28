from yax.state.type.artifact import Artifact
from yax.shared.utilities import taxidtool
import os


class TaxIDData(Artifact):
    def __init__(self, completed):
        self.tax_id_data = None

        if completed:
            taxidtool.parse_taxid_data(os.path.join(self.data_dir,
                                                    "tax_id_data.yax"))

    def __complete__(self):
        taxidtool.write_taxid_data(self.tax_id_data,
                                   os.path.join(self.data_dir,
                                                "tax_id_data.yax"))
