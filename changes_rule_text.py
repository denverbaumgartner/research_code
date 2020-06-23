import requests
from bs4 import BeautifulSoup
import re

'''
def get_rule_text_nodes(main_text):
    begin = main_text.find('h2', text = re.compile('Statutory Authority'))
    end = main_text.find('div', class_= 'signature')
    list_of_nodes = []
    nextnode = begin.nextSibling
    while nextnode != end:
        if nextnode == '\n':
            nextnode = nextnode.nextSibling
        if nextnode == end:
            break
        if nextnode.name == 'span' or nextnode.name == 'div':
            if nextnode.text is not None:
                list_of_nodes.append(nextnode.text)
                nextnode = nextnode.nextSibling
            
        else:
            list_of_nodes.append(nextnode)
            nextnode = nextnode.nextSibling
    return list_of_nodes
'''

# Function that returns parts and its authority citations
def get_part_authorities(main_text):
    dictionary = {}
    parts = main_text.findAll('h1', text = re.compile('PART'))
    for node in parts:
        part_title = node.text
        dictionary[part_title] = []
        authority_node = node.findNextSibling('p', class_='authority').find('span',class_='auth-content').text
        dictionary[part_title].append(authority_node)
    
    
    return dictionary
        
def compare_rule_text(proposed_link, final_link):
    page_final = requests.get(final_link)
    soup_final = BeautifulSoup(page_final.content,'lxml')
    main_text_final = soup_final.find('div', class_= 'doc-content-area')
    rule_text_final = get_part_authorities(main_text_final)

    page_proposed = requests.get(proposed_link)
    soup_proposed = BeautifulSoup(page_proposed.content,'lxml')
    main_text_proposed = soup_proposed.find('div', class_= 'doc-content-area')
    rule_text_proposed = get_part_authorities(main_text_proposed)
    return [rule_text_final, rule_text_proposed]
    
    

def main():
    final = 'https://www.federalregister.gov/documents/2020/03/26/2020-05546/accelerated-filer-and-large-accelerated-filer-definitions'
    proposed = 'https://www.federalregister.gov/documents/2019/05/29/2019-09932/amendments-to-the-accelerated-filer-and-large-accelerated-filer-definitions'
    print(compare_rule_text(proposed,final))
    sample = compare_rule_text(proposed, final)
    return sample

output = main()