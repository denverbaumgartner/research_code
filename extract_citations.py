'''
Script to extract citations given the FR link
General rules that a citation must satisfies:
    Has at least 1 <em> tag
    Includes a year
    Has at least one person's name (use NLTK library to detect this)
'''
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import spacy
import nltk
import csv
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from nltk.tag import StanfordNERTagger

# Boolean function (Journal articles and Author Names should not have these words)
def forbidden(test_string):
    forbid = ['etter ', 'Release', 'xchange ', 'GAO', 'Table', 'Part ', 'section',
    'Staff', 'LLC', 'Inc.', 'Office of', 'Notice ', 'omment', 'supra'
    'Prospectus', 'footnote', 'FR', 'Edition', 'Statement', 'Division of', 'Speech ']
    for word in forbid:
        if word in test_string:
            return True


# Boolean Fuction to check if a string has a person's name
def has_person(string_test):
    entities = ne_chunk(pos_tag(word_tokenize(string_test))) # Use NLTK library to parse and tag the string
    for entity in entities:
        # Check if there is a person name
        if not isinstance(entity, tuple) and 'PERSON' in entity.label():    
            return True
    else:
        return False

def sub_leaves(tree, node):
    return [t.leaves()  for t in tree.subtrees(lambda s: s.label() == node)]


# Boolean Function to check if a string has a year
def has_year(stringg):
    list_of_4digits = re.findall(('\d\d\d\d'), stringg)
    for digit in list_of_4digits:
        digit = int(digit)
        # Years should be indexed between 1800 and 2020
        if digit > 1800 and digit < 2020:
            return True
    else:
        return False 


# Extract all the emphasized tags and text between them
def get_emp(italics):
    content = []
    before_first_em = re.sub(r'[^a-zA-Z .,&-]+', '', italics[0].previousSibling.split('(')[-1]) #Get the node before first <em>
    if has_person(before_first_em): 
        content.append(before_first_em)
    for italic in italics: # Loop through the <em> tags
        content.append(italic)
        nextnode = italic.nextSibling
        # Get text betweem <em>
        if nextnode.name != 'em' and nextnode is not None:
            if len(nextnode) > 5:
                content.append(nextnode)
    if len(content) >= 2:
        return content


def restructure(strings_and_tags):
    para = ''
    for cite in strings_and_tags:
        if isinstance(cite, Tag) and (not forbidden(cite.text)):
            para += ';' + cite.text 
        if (isinstance(cite, NavigableString) or isinstance(cite, str)) and (not forbidden(cite)):
            para += ';' + cite
    split_list = para.split(';')[1:]
    citations = []
    citation = ''
    for entry in split_list:
        if re.search('\d\d\d\d', entry) is None:
            citation += entry + '+'
        if re.search('\d\d\d\d', entry) is not None:
            citation += entry + '+'
            citations.append(citation)
            citation = ''
    return citations




# Return a dictionary of qualified footnotes given FR link (key is footnote number)
def get_qualified_footnotes(link):
    # Extract the footnote section of the page
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'lxml')
    content = soup.find('div', class_= 'doc-content-area')
    footnotes = content.findAll('div', class_='footnote')

    # List to store footnotes that have <em> tag, 'See', and has a year
    footnotes_with_em = [] 
    for footnote in footnotes:
        if footnote.find('em') is not None: # Add footnote with <em> tags
            if has_year(footnote.text): # If the footnote has a year, append
                footnotes_with_em.append(footnote)
                print(footnotes_with_em)
                print('_________________________________________________')

    dict_break_down = {}
    for note in footnotes_with_em:
        id_str = note.get('id')
        id_num = int(re.search(r'(\d+)',id_str).group(0)) #Footnote number as keys
        list_of_em_tags = note.findAll('em') # Find all <em> in footnote
        qualified = []
        for tags in list_of_em_tags:
            qualified.append(tags)
        broke_up = get_emp(qualified) # Extract all text between <em> by function above
        if broke_up is not None:
            dict_break_down[id_num] = broke_up
    #return dict_break_down
    print(dict_break_down)
    print('_________________________________________________')
    diction_cand = {}
    for key in dict_break_down:
        list_of_tags = dict_break_down[key]
        for i in range(len(list_of_tags)): #Go though the list of tags for one footnote
            if i == len(list_of_tags) - 1:
                if isinstance(list_of_tags[i],NavigableString) and has_person(list_of_tags[i]) and has_year(list_of_tags[i]):
                    if not forbidden(list_of_tags[i]):
                        diction_cand[key] = restructure(dict_break_down[key])
                break
            # Identify the <em> tag first and parse through 
            if isinstance(list_of_tags[i], Tag) and ('ee' in list_of_tags[i].text or 'e.g' in list_of_tags[i].text 
            or 'or exam' in list_of_tags[i].text):
                string_tags = str(list_of_tags[i+1].encode('utf-8')) # Convert to a workable string
                if has_person(string_tags) and not forbidden(string_tags): 
                    if (i < len(list_of_tags) - 2) and (not forbidden(list_of_tags[i+2])):
                        diction_cand[key] = restructure(dict_break_down[key])
                        break

            # Identity string first and parse through
            if isinstance(list_of_tags[i], str) and isinstance(list_of_tags[i+1], Tag):
                sentence = str(list_of_tags[i].encode('utf-8'))
                if has_person(sentence) and (not forbidden(list_of_tags[i+1].text)) and (not forbidden(sentence)):
                    diction_cand[key] = restructure(dict_break_down[key])
                    break
    
    print(diction_cand)
    print('_________________________________________________')
    return diction_cand



def main():


    url = 'https://www.federalregister.gov/documents/2006/12/13/E6-21141/short-selling-in-connection-with-a-public-offering'
    test = get_qualified_footnotes(url)




    with open('citations_proposed.csv', 'w', newline='', encoding='utf8') as csvFile:
        writer = csv.writer(csvFile)
        for key in test:
            writer.writerow([key, test[key]])
    csvFile.close()



    
main()

