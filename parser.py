import re
import os
import sys
from pprint import pprint
from bs4 import BeautifulSoup as BS
import time

def parse(text: str):
    splitter = '<?xml version="1.0" encoding="UTF-8"?>'
    splitted = text.split(splitter)
    splitted = list(filter(lambda x: x != '', splitted))
    return splitted

def main():
    names = sys.argv[1:]
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
                    publication_reference = {'doc-number': temp.find("doc-number").text,
                                             'country': temp.find("country").text,
                                             'date': temp.find("date").text}
                else:
                    publication_reference = None
                description = soup.find("description").text
                claims = [x.text for x in soup.findAll("claim-text")]

                applicants = []
                for applicant in soup.findAll("applicant"):
                    applicants.append({
                        "first-name":applicant.find("first-name").text,
                        "last-name":applicant.find("last-name").text})

                agents = []
                for agent in soup.find("parties").findAll("agent"):
                    agents.append({"orgname":agent.find("orgname").text})

                assignees = []
                for assignee in soup.findAll("assignee"):
                    assignees.append({"orgname": assignee.find("orgname").text})

                overall_res.append({
                    "application_reference": application_reference,
                    "publication_reference": publication_reference,
                    "description" : description,
                    "claims": claims,
                    "applicants": applicants,
                    "agents":agents,
                    "assignees":assignees})
            except AttributeError:
                pass
    pprint(overall_res)
    input()

if __name__=="__main__":
    main()