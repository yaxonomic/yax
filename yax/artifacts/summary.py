from yax.state.type.artifact import Artifact
from io import StringIO
import os
import os.path
import pdfkit


class Summary(Artifact):

    def __init__(self, data_dir):
        super().__init__(self)
        self.data_dir = data_dir

    def write_summary(self, text, file_name):
        """
        Write a summary pdf to the data_dir.
        """
        writer = StringIO()
        writer.write(text)

        pdfkit.from_string(writer.getvalue(), str(self.data_dir) + "/" +
                           str(file_name) + ".pdf")
        writer.close()

    def __complete__(self):
        """
        Clean up data_dir by deleting temporary coverage plot images
        """
        images = [self.data_dir + '/' + f for f in os.listdir(self.data_dir) if
                  os.path.isfile(os.path.join(self.data_dir, f)) and
                  len(f.split('.')) > 1 and
                  f.split('.')[1] == "png"]
        for image in images:
            os.remove(image)
