'''
Created on Feb 24, 2016

@author: Andrew Hodel
'''
#must import NCBI taxid functions and tree
import numpy as np
import ete2.ncbi_taxonomy as tax
class Filter():
    
    filter_results=None
    maximum_lca_threshold=None
    taxid_tree=None
    #creates a 'matrix' 10 rows BY 3 columns
    read_check = np.zeros(10,3)
    read_taxid = []
    read_taxid.append([])
    read_taxid_ancestor = []
    read_taxid_ancestor.append([])
    read_taxid_ancestor.append([])
    
    informed_read_taxid = np.zeros(10,2)
    minumum_informed_threshold = None
    #the number of reads/lines from survey
    n = 0;
    m = 0;
    def identify_informative_reads(self, survey_results, maximum_lca_threshold):
        '''
        for nth element in the survey_results list of read fragments
           locate in the taxid tree where that read frag hits
           traverse up the taxid tree LCA times
               storing each taxid that exists at that location
                   if that taxid already has been hit then incrment a counter for the node
                   
       
        '''
        # the first line of the file because that is the first taxid
        
        #3d array of reads, the taxid they map to, and the list of ancestors
        #puts the results of survey into a 
        survey_decipher_list();
        survey_decipher_numpy();
        #add a third dimension to this for the use of storing ancestors
        
        #get the ancestors of the taxid associated with the read fragement
        #add the list of ancestors to the third element in the row
        for i in m:
            read_taxid[i][1][0] = tree_traverse_up(read_taxid[i][1])
            
        return self.informed_reads 
    #will not return the taxid used to enter the tree                
    
    def add_informed(self, taxid):
        i=0
        #taxid is already in the dictionary so we need to find out how many times its been hit
        if 
        #taxid not found, insert it into the dictionary      
        else:

            
        return self.informed_read_taxid
    
     def rank_informed_reads(self, informed_reads, minimum_informed_threshold):                                                                
        #2 thresholds are allowed

        #minimum overall frequency supplied by user
               
            
        # OR
        
        #minimum relative frequency with respect to all informed reads
        #contains hits by informed(taxid is hit by at least 1 informed read)
        #exclusive hits by informed(taxid is hit by only informed reads)
        #total number of hits on a taxid
        #TODO
        
        
        return self.filter_results                                                                

    #TEST
    #kind of done just need concrete inputs to complete parsing
    #returns a list of ancestors for a given taxid and number of ancestors
    def tree_traverse_up(self, taxid):
        i=0
        taxid_ancestors [] = None
        temp [] = None
        #will work when NCBI stuff is imported
        lineage_str = tax.get_lineage(taxid)
        #parse lineage_str
        while i < maximum_lca_threshold:
            for c in lineage_str:
                #if the current character is the end of the parent taxid
                temp.append(c)
                if c == #whatever the end of the taxid delimination is
                    #add the contents of temp[] to informed_temp[]
                    taxid_ancestors.append(temp)
                    #delete contents of temp for the next taxid
                    del temp[:len(temp)]
                
            i+=1     
        return self.taxid_ancestors
    
    #TEST
    def survey_decipher_numpy(self):
        temp_buf [] = None
        #to get one line of read:taxid
        for i in survey_results:
            #contains either read or taxid
            temp_buf.append(i);
            if ord(i) == ord(' '):
                #here can be changed to accomidate for however the readfrag
                #and taxid are seperated
                temp_buf.remove(' ');
                #add the read frag to the first element in the row
                read_check[n][0][0] = copy(temp_buf);
                #delete contents of the array
                for h in len(temp_buf):
                    temp_buf.pop();
            if ord(i) == ord('\n'):
                temp_buf.remove('\n');
                #add taxid to the second element in the row
                read_check[n][1][0] = copy(temp_buf);
                for h in len(temp_buf):
                    temp_buf.pop();
            n++
                
   
    #NEEDS TEST
    #survey_results is a 2 dimension list where each element is a read fragment 
    #then an associated TAXID
    def survey_decipher_list(self):
        temp_buf [] = None
        temp_read_taxid [] = None
        #to get one line of read:taxid
        for i in survey_results:
            #contains either read or taxid
            temp_buf.append(i);
            if ord(i) == ord(' '):
                #here can be changed to accomidate for however the readfrag
                #and taxid are seperated
                temp_buf.remove(' ');
                #add the read frag to temp array
                temp_read_taxid_ancestor.insert([m,0,0],copy(temp_buf));
                #delete contents of the array
                for h in len(temp_buf):
                    temp_buf.pop();
            if ord(i) == ord('\n'):
                temp_buf.remove('\n');
                temp_read_taxid_ancestor.insert([m,1,0],copy(temp_buf));
                for h in len(temp_buf):
                    temp_buf.pop();
            m++
                
    
    def __init__(self, params):
        #must set the variables to their values 
        super().__init__()

        