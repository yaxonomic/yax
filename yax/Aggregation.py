'''
Created on Feb 24, 2016

@author: user
'''
class Agregation():
    
    refinement_results=None
    agregation_results=None
    maximum_lca_threshold=None
    taxid_tree=None
    
    
    def identify_informative_reads(self, survey_results, maximum_lca_threshold):
        '''
        for nth element in the survey_results list of read fragments
           locate in the taxid tree where that read frag hits
           traverse up the taxid tree LCA times
               storing each taxid that exists at that location
                   if that taxid already has been hit then incrment a counter for the node
                   
       
        '''
        
        return self.informed_reads
    def rank_informed_reads(self, informed_reads):                                                                
        
        
        #contains hits by informed(taxid is hit by at least 1 informed read)
        #exclusive hits by informed(taxid is hit by only informed reads)
        #total number of hits on a taxid
        return self.summary_stats
    
    
    def create_summary_table(self, summary_stats):
       
        #some kind of a table format for created from the summary_file
        return self.summary_table
    
    def __init__(self, params):
        super().__init__()
