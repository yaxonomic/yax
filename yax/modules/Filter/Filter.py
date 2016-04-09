'''
Created on Feb 24, 2016

@author: Andrew Hodel
'''
import yax/TaxIDBranch as branch


class Filter():
    filter_results = None
    maximum_lca_threshold = None
    taxid_tree = None
    read_taxids = {}
    taxid_ancestor = {}
    taxid_mismatch = []
    minumum_informed_threshold = None
    informed_read_taxids = {}
    read = None

    def main(working_dir, output):
        # puts the taxtree in output_location
        branch.preprocessing(nodes_fp, names_fp, gi_taxid_nucl_fp,
                             output_location, project_name)
        branch.get_input_taxid_data(output_location)
        pass

    def identify_informative_reads(self, survey_results,
                                   maximum_lca_threshold):

        '''
        for nth element in the survey_results list of read fragments
           locate in the taxid tree where that read frag hits
           traverse up the taxid tree LCA times
               storing each taxid that exists at that location
                   if that taxid already has been hit then incrment a counter
                   for the node
        '''
        pass

    def add_informed(self, taxid):

        pass

    def rank_informed_reads(self,
                            informed_reads,
                            minimum_informed_threshold):
        # 2 thresholds are allowed
        # minimum overall frequency supplied by user
        #  OR
        # minimum relative frequency with respect to all informed reads
        # contains hits by informed
            # (taxid is hit by at least 1 informed read)
        # exclusive hits by informed(taxid is hit by only informed reads)
        # total number of hits on a taxid
        # TODO

        return self.filter_results

    # TEST
    # kind of done just need concrete inputs to complete parsing
    # returns a list of ancestors for a given taxid and number of ancestors

    def get_ancestors(self, taxids):
        # use taxid clipper to get the tree file
        taxid_ancestors = [[]]
        number = 0
        for tax in taxids:
            # look up the ancestors for the given taxid
            taxid_ancestors[number] = branch.get_ancestors()
            number += 1
        return taxid_ancestors

    def is_informed(self, read_taxids, informed_read_taxids):
        keys = read_taxids.keys()
        ancestors = []
        for read in keys:
            # list of lists each element containing taxids for element number
            # of mismatches
            tax_by_mismatch_list = dict.get(read)
            # grab the list of the taxids from element/mismatch N
            for tax in tax_by_mismatch_list:
                for temp_tax in tax:
                    # list with each element being a list of the ancestors
                    # from
                    ancestors.append(get_ancestors(temp_tax))
                    if temp_tax == tax[len(tax)-1]:
                        if does_it_share_one(ancestors) == 1:
                            informed_read_taxids[read] = tax_by_mismatch_list
        return informed_read_taxids

    # go through the list of lists of taxid to its ancestors
    # if it fails early then it will fail later as well
    def does_it_share_one(self, ancestor_list):
        true1_false0 = 0
        for temp in ancestor_list:
            for ancestor in temp:
                try:
                    ancestor.index()
                except Exception as e:
                    raise
        pass

    # NEEDS TEST
    # survey_results is a 2 dimension
    # list where each element is a read fragment
    # then an associated TAXID

    def survey_decipher(self, survey_results, read_taxids):
        # a list with each line as an element
        lines = survey_results.split('\n')
        # a list for the taxids, each element being a different mismatch
        temp_taxids = []
        # this will be the list of taxids according to the number of mismatchs
        # this will get put into temp_taxids which is then put into read_taxids
        mismatch_taxids = []
        words_from_line = []
        for i in len(lines):
            # fills a list with each word as a seperate element in the list
            words_from_line = lines[i].split(' ')

            for q in len(words_from_line):

                # inserts the read frag as a key into the dictionary
                # and then the list of all taxids associated to it
                read_taxids[words_from_line[0]] = words_froms_line[1:]
