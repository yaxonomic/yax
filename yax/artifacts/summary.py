from yax.state.type.artifact import Artifact
from io import StringIO
import pdfkit


class Summary(Artifact):

    def write_summary(self, text, file_name):
        """
        Write a summary pdf to the data_dir.
        """
        writer = StringIO()
        writer.write(text)

        pdfkit.from_string(writer.getvalue(), str(self.data_dir) + "/" +
                           str(file_name) + ".pdf")
        writer.close()
