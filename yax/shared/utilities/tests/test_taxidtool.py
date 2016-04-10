import unittest
import tempfile

from yax.util import get_data_path
import yax.shared.utilities.taxidtool as taxidtool


class TestTaxIDTool(unittest.TestCase):
    def test_parse_names_dmp(self):
        fp = get_data_path('names.dmp')
        results = taxidtool.parse_names_dmp(fp)
        for key, value in results.items():
            self.assertEqual(value, "Node%s" % key)

    def test_parse_gi_taxid_dmp(self):
        fp = get_data_path('gi_taxid_nucl.dmp')
        results = taxidtool.parse_gi_taxid_dmp(fp)
        for taxid, gis in results.items():
            for gi in gis:
                self.assertTrue(gi.startswith(taxid))

    def test_parse_nodes_dmp(self):
        fp = get_data_path('nodes.dmp')
        results = taxidtool.parse_nodes_dmp(fp)
        for taxid, record in results.items():
            self.assertEqual(record.taxid, taxid)
        self.assertEqual(results['12'].parent_taxid, '4')
        self.assertEqual(results['2'].rank, 'kingdom')
        self.assertEqual(results['5'].parent_taxid, '3')
        self.assertEqual(results['8'].rank, 'species')

    def test_build_taxid_data(self):
        nodes_fp = get_data_path('nodes.dmp')
        names_fp = get_data_path('names.dmp')
        gi_taxid_nucl_fp = get_data_path("gi_taxid_nucl.dmp")
        results = taxidtool.build_taxid_data(nodes_fp,
                                             names_fp,
                                             gi_taxid_nucl_fp)
        for taxid, record in results.items():
            self.assertEqual(record.taxid, taxid)
            self.assertEqual(record.sci_name, "Node%s" % taxid)
            for gi in record.assoc_gis:
                self.assertTrue(gi.startswith(taxid))

        self.assertEqual(results['23'].parents, ['1', '3', '7'])
        self.assertEqual(results['19'].children, [])
        self.assertEqual(results['23'].rank, 'species')
        self.assertEqual(set(results['1'].children), set(['3', '2']))

    def test_write_taxid_data(self):
        nodes_fp = get_data_path('nodes.dmp')
        names_fp = get_data_path('names.dmp')
        gi_taxid_nucl_fp = get_data_path("gi_taxid_nucl.dmp")
        results = taxidtool.build_taxid_data(nodes_fp,
                                             names_fp,
                                             gi_taxid_nucl_fp)

        with tempfile.NamedTemporaryFile() as fh:
            taxidtool.write_taxid_data(results, fh.name)
            data = taxidtool.parse_taxid_data(fh.name)
            with tempfile.NamedTemporaryFile() as fh2:
                taxidtool.write_taxid_data(data, fh2.name)
                data2 = taxidtool.parse_taxid_data(fh2.name)
                self.assertEqual(set(data.keys()), set(data2.keys()))

    def test_parse_taxid_data(self):
        taxid_data_fp = get_data_path('taxid_data.txt')
        results = taxidtool.parse_taxid_data(taxid_data_fp)

        for taxid, record in results.items():
            self.assertEqual(record.taxid, taxid)
            self.assertEqual(record.sci_name, "Node%s" % taxid)
            for gi in record.assoc_gis:
                self.assertTrue(gi.startswith(taxid))

        self.assertEqual(results['23'].parents, ['1', '3', '7'])
        self.assertEqual(results['19'].children, [])
        self.assertEqual(results['23'].rank, 'species')
        self.assertEqual(set(results['1'].children), set(['3', '2']))

    def test_build_gis_to_taxids(self):
        taxid_data_fp = get_data_path('taxid_data.txt')
        taxid_data = taxidtool.parse_taxid_data(taxid_data_fp)

        reverse_lookup = taxidtool.build_gis_to_taxids(taxid_data)

        for taxid, record in taxid_data.items():
            for gi in record.assoc_gis:
                self.assertEqual(taxid, reverse_lookup[gi])

    def test_build_branch(self):
        taxid_data_fp = get_data_path('taxid_data.txt')
        taxid_data = taxidtool.parse_taxid_data(taxid_data_fp)
        inclusion_roots = ["6"]

        results = taxidtool.build_branch(taxid_data, inclusion_roots)

        self.assertEqual(set(results.keys()), {'6', '16', '18', '20', '22'})

    def test_build_tree(self):
        pass


if __name__ == '__main__':
    unittest.main()
