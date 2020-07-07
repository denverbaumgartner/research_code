#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 15:34:35 2020

@author: denverbaumgartner
"""

import requests
from bs4 import BeautifulSoup as soup
import re

# packages to help with analysis of the text secions
from fuzzywuzzy import fuzz

# fuzzy wuzzy - would be a good library to see the impact of change 

'''
use this to create the key that is going to be associated with the dictionary self.textChange_data


newPart_### will refer to the amendment of parts that are new from proposed to final
samePart_### will refer to the parts that are the same, contains text from final indexed at 0 and from proposed at 1, and pull text for analysis

as of now whatever the last part of the ruling is is not being pulled, this is because the final part does not have a class = 'section'
'''

# class to track text changes across the statutory authority section 
class textChanges_Statutory_Authority():
    
    # initialize the class by scraping relevant data from the proposed and finalized ruling 
    def __init__(self, proposed_link, final_link):
        
        # create dictionaries to store the relevant data for the documents
        self.proposed_link_content = {}
        self.final_link_content = {}
        
        # set variables to store analysis data 
        self.textChange_analysis = {}
        
        # pull the main text group from the final link
        page_final = requests.get(final_link)
        soup_final = soup(page_final.content,'lxml')
        main_text_final = soup_final.find('div', class_= 'doc-content-area')
        
        # pull the main text group from the proposed link
        page_proposed = requests.get(proposed_link)
        soup_proposed = soup(page_proposed.content,'lxml')
        main_text_proposed = soup_proposed.find('div', class_= 'doc-content-area')
        
        # pull out all h1 tagged groups 
        final_parts = main_text_final.findAll('h1', text = re.compile('PART'))
        proposed_parts = main_text_proposed.findAll('h1', text = re.compile('PART'))

        # sort through pulled h1 tags and gather parts and authority citations  - proposed link
        for node in proposed_parts:
            part_title = node.text
            self.proposed_link_content[part_title] = []
            authority_node = node.findNextSibling('p', class_='authority').find('span',class_='auth-content').text
            self.proposed_link_content[part_title].append(authority_node)

        # sort through pulled h1 tags and gather parts and authority citations  - final link
        for node in final_parts:
            part_title = node.text
            self.final_link_content[part_title] = []
            authority_node = node.findNextSibling('p', class_='authority').find('span',class_='auth-content').text
            self.final_link_content[part_title].append(authority_node)
        
        # call the initial_comparison helper function to identify points of comparison 
        self.initial_comparison()
        
        self.test_set = main_text_final
        
        # pull out the data that is relevant to the parts in the proposed section 
        proposed_part_data = main_text_proposed.findAll('div', class_= 'section')
        
        # pull out the data that is relevant to the parts in the final section 
        final_part_data = main_text_final.findAll('div', class_= 'section')
        
        #print(final_part_data)
        
        ''' for testing - this section does not currently pull out whatever the last part of the amendment is 
        final_part_data = main_text_final.findAll('div', class_= "section-subject")
        print(final_part_data)
        '''
        
        # set a variable to hold collected data that is different between the proposal and the final 
        self.textChange_data = {}
        
        # check all the new parts and pull out relevant data, all data will be pulled from the final link
        for part in self.textChange_parts: 

            # pull out specifically which part it is refering to 
            part_number = self.part_number_helper(part, 'part')

            # iterate through the final part data to find the relating section 
            for i in range(len(final_part_data)):

                # test to see if the section is the related one 
                part_test = final_part_data[i].findAll('div', id = re.compile(part_number))

                # see if the array is empty or contains data 
                if len(part_test) > 0: 

                    # set the key for the new part 
                    newKey = 'newPart_' + part_number
                    
                    # create a key and append the related text data to the file 
                    self.textChange_data[newKey] = final_part_data[i].text
        
        # now compare the parts that were the same and see if the text changed at all
        same_parts_comparison_group = list(self.textChange_parts_changed_text.keys())
        
        # iterate through the parts that are same between the two links and get the text 
        for same_part in same_parts_comparison_group: 
            
            
            # pull out specifically which part it is refering to 
            part_number = self.part_number_helper(same_part, 'part')
            
            # set the key for the new part 
            newKey = 'samePart_' + part_number
            
            self.textChange_data[newKey] = []
            
            # iterate through the final part data to find the relating section 
            for a in range(len(final_part_data)):

                # test to see if the section is the related one 
                part_test = final_part_data[a].findAll('div', id = re.compile(part_number))

                # see if the array is empty or contains data 
                if len(part_test) > 0: 
                    
                    # create a key and append the related text data to the file 
                    self.textChange_data[newKey].append(final_part_data[a].text)
                    
            # iterate through the final part data to find the relating section 
            for b in range(len(proposed_part_data)):

                # test to see if the section is the related one 
                part_test = proposed_part_data[b].findAll('div', id = re.compile(part_number))

                # see if the array is empty or contains data 
                if len(part_test) > 0: 
                    
                    # create a key and append the related text data to the file 
                    self.textChange_data[newKey].append(proposed_part_data[b].text)
            
            # add a note just so future users know which data relates to what 
            self.textChange_data[newKey].append('index 0 contains the final link data and index 1 contains the proposed')
            
    # function to analyze the differences between the two sets of collected information 
    def initial_comparison(self):
        
        # return the keys (these will be the parts) of each link
        proposed_link_parts = list(self.proposed_link_content.keys())
        final_link_parts = list(self.final_link_content.keys())
        
        # create variable to hold the keys that are different between the two groups
        self.textChange_parts = []
        
        # create variable to hold the difference in authority citations 
        self.textChange_authority_citations = {}
        
        # create variable to store the same parts to then be checked for text changes
        self.textChange_parts_changed_text = {}
        
        # compare the keys and determine which are new between the two links
        for part in final_link_parts: 
            
            # check to see if the part was in the proposal, append to textChange if not 
            if part not in proposed_link_parts: 
                self.textChange_parts.append(part)
            
            # if the amended part is in both drafts, check to see if any authority citations changed
            else: 
                # make a key for the part so that the text can later be compared
                self.textChange_parts_changed_text[part] = []
                
                # create variables to hold authority citations 
                proposed_authority_citations = self.proposed_link_content[part]
                final_authority_citations = self.final_link_content[part]
                
                # check to see if autority citations are the same, if not add to dictionary 
                if proposed_authority_citations != final_authority_citations: 
                
                    # set the part name as the key to the dictionary and initialize an array 
                    self.textChange_authority_citations[part] = []
                
                    # iterate through citations and figure out which are new 
                    for citation in final_authority_citations: 
                    
                        # if the citation is not in the proposal, append to the changes
                        if citation not in proposed_authority_citations: 
                            
                            # append the citation to the appropriate key group 
                            self.textChange_authority_citations[part].append(citation)  
     
    # helper function to pull out the part number from a passed string 
    def part_number_helper(self, string, term):
         
        # create variable for length of characters to check
        amounts = [5, 4, 3, 2, 1]
         
        # lower the string to handle all cases 
        string = string.lower()
         
        # index the first instance of the term "part" and add len
        index = string.index(term) + len(term) 
         
        # pull out strings of the first reference to part and the possible number relating to it 
        for i in amounts: 
             
            # pull test string from portion 
            test_string = string[index: index + i]
            test_string = test_string.strip()
        
            # test to see if the test string is an int, if it is return to the caller 
            try:
                int(test_string)
                
                # if int then return the test_string
                return test_string
            
            except ValueError: 
                
                hold = 0 
  
    # function to run analysis of the text data     
    def textChange_analysis(self): 
        
        # get the keys from the textChange_data and then run related analysis
        textChange_data_keys = list(self.textChange_data)
        
        # iterate through the keys and determine what analysis must be run 
        for key in textChange_data_keys:
            
            # test to see what analysis should be run depending on the key 
            if key[:8] == 'samePart': 
                
                # if it is the same part then 


newPart_### will refer to the amendment of parts that are new from proposed to final
samePart_###
    
final = 'https://www.federalregister.gov/documents/2020/03/26/2020-05546/accelerated-filer-and-large-accelerated-filer-definitions'
proposed = 'https://www.federalregister.gov/documents/2019/05/29/2019-09932/amendments-to-the-accelerated-filer-and-large-accelerated-filer-definitions'
         
a = textChanges_Statutory_Authority(proposed, final)     