import pdfkit
from io import StringIO


class Summary:

    def __init__(self):
        super.__init__()

    def __call__(self):
        summary_stats = ""
        summary_table = ""
        coverage_data = []
        order_method = ""
        total_results = 10
        num_samples = 5
        output_path = ""
        final_output_path = ""

        return self.run_summary(summary_stats, summary_table,
                                coverage_data, order_method,
                                total_results, num_samples,
                                output_path, final_output_path)

    def run_summary(self, summary_stats, summary_table, coverage_data,
                    order_method, total_results, num_samples,
                    output_path, final_output_path):

        # Get HTML templates
        template = ''.join(open("template.html", 'r').readlines())
        tax_id_snippet = ''.join(open("tax_id_snippet.html", 'r').readlines())

        # For each sample, fill out templates with appropriate data
        for i, sample in enumerate(num_samples):
            # Get ordered list of tax ids and gis
            tax_ids, gis = self.parse_summary_data(summary_stats,
                                                   summary_table,
                                                   coverage_data[i],
                                                   order_method,
                                                   total_results)
            template_data = ""
            for j, tax_id in enumerate(tax_ids):
                coverage_plot = self.generate_coverage_plot(coverage_data[i])
                # Fill out template with tax id, gis, and a coverage plot
                template_data += tax_id_snippet.format(tax_id,
                                                       gis[j],
                                                       coverage_plot)

            writer = StringIO()
            writer.write(template.format(template_data))

            # Write pdf to output artifact location
            pdfkit.from_string(writer.getvalue(),
                               output_path + "sample_" + str(i) + ".pdf")

            # Write pdf to location specified in config
            pdfkit.from_string(writer.getvalue(),
                               final_output_path + "sample_" + str(i) + ".pdf")

            writer.close()

    def parse_summary_data(self, summary_stats, summary_table,
                           coverage_data, order_method, total_results):
        stats = open(summary_stats, 'r')
        table = open(summary_table, 'r')
        coverage = open(coverage_data, 'r')
        return [], []

    def generate_coverage_plot(self, coverage_data):
        coverage = open(coverage_data, 'r')
        return ""
