import re
import os
import sys
from pprint import pprint
from bs4 import BeautifulSoup as BS
import time
from multiprocessing import Process

parallel_processes_count = 10

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
    soup = BS(patent_text, features="lxml")
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
    claims = '\n'.join(claims)
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

def create_if_not_exist(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def get_name(filename):
    return filename[filename.rfind('/')+1:filename.rfind('.')]

def process_file(filename):
    print("Started processing " + filename)
    file_res = []
    with open(filename, "r") as f:
        text = f.read()
    res = split_xml(text)
    for text_num, text in enumerate(res):
        if text_num % 100 == 0:
            print(f"{filename} : {text_num}")
        parsed_patent = parse_patent(text)
        if parsed_patent:
            file_res.append(parsed_patent)
    create_if_not_exist("output")
    create_if_not_exist("output/data")
    create_if_not_exist("output/firms")
    create_if_not_exist(f"output/info")
    create_if_not_exist(f"output/data/{get_name(filename)}")
    create_if_not_exist(f"output/firms/{get_name(filename)}")
    create_if_not_exist(f"output/info/{get_name(filename)}")
    for patent in file_res:
        with open(f"output/data/{get_name(filename)}/{patent['id']}", "w", encoding="utf-8") as f:
            f.write(patent["claims"] + '\n')
            f.write(patent["description"] + '\n')
            f.write(patent["abstract"] + '\n')
        with open(f"output/firms/{get_name(filename)}/{patent['id']}", "w", encoding="utf-8") as f:
            for a in patent["assignees"]:
                f.write(a)
                f.write("\n")
        with open(f"output/info/{get_name(filename)}/{patent['id']}", "w", encoding="utf-8") as f:
            f.write(patent["main_classification_type"] + '\n')
            f.write(patent["main_classification"])
    print("Finished processing " + filename)

def process_files(filenames):
    for name in filenames:
        process_file(name)

def main():
    names = sys.argv[1:]
    not_found_description = []
    not_found_claims = []
    filenames = []
    i = 0
    while i < len(names):
        if os.path.isdir(names[i]):
            names += list(map(lambda x: f"{names[i]}/{x}", os.listdir(names[i])))
        i += 1

    filenames = [name for name in names if os.path.isfile(name)]

    print("Filenames:\n")
    #pprint(filenames)

    filenames_list = []

    for i in range(parallel_processes_count):
        start = i * len(filenames) / parallel_processes_count
        end = (i+1) * len(filenames) / parallel_processes_count
        if i == parallel_processes_count:
            end = len(filenames)
        start = int(start)
        end = int(end)
        filenames_list.append(filenames[start:end])

    filenames_list = filenames_list
    #pprint(filenames_list)

    # for filename in filenames:
    #     process_file(filename)

    processes = []

    for sublist in filenames_list:
        p = Process(target = process_files, args = [sublist])
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("\nDone.")

if __name__=="__main__":
    main()