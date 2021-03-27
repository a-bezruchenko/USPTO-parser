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
    not_found_description = []
    not_found_claims = []
    for filename in names:
        print("processing " + filename)
        with open(filename, "r") as f:
            text = f.read()
        res = parse(text)
        for text_num, text in enumerate(res):
            print(f"text #{text_num}")
            soup = BS(text)
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

            description_tag = soup.find("description")
            if description_tag:
                description = description_tag.text
            else:
                not_found_description.append(text_num)
                continue

            claims = [x.text for x in soup.findAll("claim-text")]

            # applicants = []
            # for applicant in soup.findAll("applicant"):
            #     applicants.append({
            #         "first-name":applicant.find("first-name").text,
            #         "last-name":applicant.find("last-name").text})

            # agents = []
            # for agent in soup.find("parties").findAll("agent"):
            #     agents.append({"orgname":agent.find("orgname").text})

            # assignees = []
            # for assignee in soup.findAll("assignee"):
            #     assignees.append({"orgname": assignee.find("orgname").text})

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
                if problem_tag is not None and solution_tag is not None:
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

            overall_res.append({
                "application_reference": application_reference,
                "publication_reference": publication_reference,
                "abstract": abstract,
                "main_classification_type": str(classification_type),
                "main_classification": str(main_classification),
                "description" : description,
                "claims": claims
                # "applicants": applicants,
                # "agents":agents,
                # "assignees":assignees
            }
            )

    time_end = time.clock()

    #pprint(overall_res)
    main_classification_count = dict()
    none_abstract_count = 0

    for el in overall_res:
        if el["main_classification_type"]+el["main_classification"] in main_classification_count.keys():
            main_classification_count[el["main_classification_type"]+el["main_classification"]] += 1
        else:
            main_classification_count[el["main_classification_type"]+el["main_classification"]] = 1

        if el["abstract"] == str(None):
            none_abstract_count += 1


    pprint(main_classification_count)

    print(none_abstract_count)

    print(time_end-time_start)

    input()

if __name__=="__main__":
    main()