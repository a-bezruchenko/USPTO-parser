import re
import os
import sys
from pprint import pprint
from bs4 import BeautifulSoup as BS
import time

def split_xml(text: str):
    splitter = '<?xml version="1.0" encoding="UTF-8"?>'
    splitted = text.split(splitter)
    splitted = list(filter(lambda x: x != '', splitted))
    return splitted


def get_text_field(tag, field_name: str):
    field = tag.find(field_name)
    try:
        if field:
            text_field = field.text.strip()
            return text_field
        else:
            return None
    except AttributeError:
        print("Ошибка при обращении к полю" + field_name)
        return None

def parse_patent(patent_text):
    soup = BS(patent_text)
    # Identification of a patent application.
    temp = soup.find("application-reference")
    if temp:
        application_reference = {'doc_number': get_text_field(temp, "doc-number"),
                                 'country': get_text_field(temp, "country"),
                                 'date': get_text_field(temp, "date")}
    else:
        application_reference = None
    # Identification of a published patent document.
    temp = soup.find("publication-reference")
    if temp:
        publication_reference = {'doc_number': get_text_field(temp, "doc-number"),
                                 'country': get_text_field(temp, "country"),
                                 'date': get_text_field(temp, "date")}
    else:
        publication_reference = None
    description_tag = soup.find("description")
    if description_tag:
        description = description_tag.text
    else:
        return None
    claims = [x.text for x in soup.findAll("claim-text")]
    inventors = []
    applicants = soup.find("applicants")
    if applicants:
        for content in applicants.contents:
            if content != '\n':
                inventor = {'first-name': get_text_field(content, "first-name"),
                            'last-name': get_text_field(content, "last-name")}
                inventors.append(inventor)
    # agents = []
    # for agent in soup.find("parties").findAll("agent"):
    #     agents.append({"orgname":agent.find("orgname").text})
    assignees = []
    for assignee in soup.findAll("assignee"):
        if get_text_field(assignee, "orgname"):
            assignees.append(get_text_field(assignee, "orgname"))
    classification_type = None
    main_classification = None
    for type in ("classification-ipc", "classification-ipcr", "classification-locarno"):
        tag = soup.find(type)
        if tag:
            classification_type = type
            if type == "classification-ipcr":
                section_tag = tag.find("section")
                class_tag = tag.find("class")
                subclass_tag = tag.find("subclass")
                if section_tag and class_tag and subclass_tag:
                    patent_section = section_tag.text.strip()
                    patent_class = class_tag.text.strip()
                    patent_subclass = subclass_tag.text.strip()
                    main_classification = f"{patent_section}"
                    break
                else:
                    continue
            else:
                main_classification_tag = tag.find("main-classification")
                if main_classification_tag:
                    main_classification = main_classification_tag.text.strip()
                    break
                else:
                    continue
    abstract = str(None)
    tag = soup.find("abstract")
    if tag:
        problem_tag = tag.find("abst-problem")
        solution_tag = tag.find("abst-solution")
        if problem_tag and solution_tag:
            abstract = problem_tag.text + " " + solution_tag.text
        else:
            abstract = tag.text
    # tag = soup.find("classification-national")
    # if tag:
    #     country = tag.find("country").text.strip()
    #     national_classification = tag.find("main-classification").text.strip()
    # else:
    #     country = None
    #     national_classification = None
    return {
                "id": int(application_reference["doc_number"]),
                "application_reference": application_reference,
                "publication_reference": publication_reference,
                "abstract": abstract,
                "main_classification_type": str(classification_type),
                "main_classification": str(main_classification),
                "description" : description,
                "claims": claims,
                "applicants": inventors,
                "assignees":assignees
            }

def main():
    names = sys.argv[1:]
    overall_res = []
    time_start = time.clock()
    not_found_description = []
    not_found_claims = []
    for filename in names:
        print("processing " + filename)
        with open(filename, "r") as f:
            text = f.read()
        res = split_xml(text)
        for text_num, text in enumerate(res):
            print(f"text #{text_num}")
            parsed_patent = parse_patent(text)
            if parsed_patent:
                overall_res.append(parsed_patent)

    time_end = time.clock()

    print(time_end-time_start)
    input()

if __name__=="__main__":
    main()