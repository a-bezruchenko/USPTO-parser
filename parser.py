import re
import os
from bs4 import BeautifulSoup as BS
import time

def get_input_names():
    os.chdir('input')
    input_list = list(filter(lambda x: re.match('.*.xml', x), os.listdir()))
    os.chdir('..')
    return input_list

def get_patents(path: str):
    input_file = open(path, 'r')
    input_string = input_file.read()
    input_file.close()
    return input_string

def parse(text: str):
    splitter = '<?xml version="1.0" encoding="UTF-8"?>'
    splitted = text.split(splitter)
    splitted = list(filter(lambda x: x != '', splitted))
    return splitted

names = get_input_names()

names = ["ipg100105.xml"]
overall_res = []
time_start = time.clock()
for filename in names:
    print("processing " + filename)
    with open(filename, "r") as f:
        text = f.read()
    res = parse(text)
    for text_num, text in enumerate(res):
        print(f"text #{text_num}")
        soup = BS(text)
        try:
            # Identification of a patent application.
            temp = soup.find("application-reference")
            if temp:
                application_reference = {'doc_number': temp.find("doc-number").text,
                                         'country': temp.find("country").text,
                                         'date': temp.find("date").text}
            else:
                application_reference = None
            # Identification of a published patent document.
            temp = soup.find("publication-reference")
            if temp:
                publication_reference = {'doc_number': temp.find("doc-number").text,
                                         'country': temp.find("country").text,
                                         'date': temp.find("date").text}
            else:
                publication_reference = None
            description = soup.find("description").text
            claims = [x.text for x in soup.findAll("claim-text")]
            overall_res.append({
                "application_reference": application_reference,
                "publication_reference": publication_reference,
                "description" : description,
                "claims": claims})
        except AttributeError:
            pass




        # parties
        # applicant
        # agent
        # assignees
        # examiners





    # input_path = 'input/' + filename
    # patents = get_patents(input_path)
    # parsed = parse(patents)
    # save_parsed(parsed, 'output/' + filename)
    # print(filename +" processed")
