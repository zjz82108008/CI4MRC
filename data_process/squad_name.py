import json
import copy
import os
import re

def load_json(file_name):
    with open(file_name, "r", encoding='utf-8') as reader:
        input_data = json.load(reader)
    return input_data

def load_jsonl(file_name):
    return [json.loads(line) for line in open(file_name, 'r')]

def save_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as writer:
        json.dump(data, writer)

def save_jsonl(file_name, data):
    with open(file_name, 'w') as file:
        for d in data:
            file.write(json.dumps(d))
            file.write("\n")


def name_100():
    name_list = load_jsonl("namedata/names.jsonl")
    print(len(name_list))
    print(name_list[0])
    name_list_by_rank = sorted(name_list, key=lambda x: x.get('100_year_rank', 999))
    print(name_list_by_rank[:5])
    names_female = [name for name in name_list if 'news' in name['attributes'] and 'female' in name['attributes']]
    names_male = [name for name in name_list if 'news' in name['attributes'] and 'male' in name['attributes']]
    for name in name_list_by_rank:
        if 'female' in name['attributes'] and len(names_female) < 50 and name not in names_female:
            names_female.append(name)
        if 'male' in name['attributes'] and len(names_male) < 50 and name not in names_male:
            names_male.append(name)
    save_jsonl("namedata/names_100.jsonl", names_male + names_female)
    # for i, name in enumerate(names_male+names_female):

def example_all():
    squad_examples = load_json("squad1.1/dev-who_gai.json")["data"]
    onesquad_example = squad_examples[0]
    print(onesquad_example)
    name_list = load_jsonl("namedata/names_100.jsonl")
    # print(squad_example["context"][squad_example["answers"]["answer_start"][0]:(squad_example["answers"]["answer_start"][0]+len(squad_example["answers"]["text"][0]))])
    # squad_example_new = squad_example["context"][0:squad_example["answers"]["answer_start"][0]] + name_list[0]["name"] + squad_example["context"][(squad_example["answers"]["answer_start"][0]+len(squad_example["answers"]["text"][0])):]
    print(onesquad_example["context"])
    # print(squad_example_new)
    # squad_example["context"] = re.sub(squad_example["answers"]["text"][0], name_list[0]["name"], squad_example["context"])
    result = []
    k = 0
    for squad_example in squad_examples:
        for j in range(10):
            k+=1
            substitue = copy.deepcopy(squad_example)
            for i in range(len(substitue["answers"]["answer_start"])):
                oldname = substitue["answers"]["text"][i]
                print(oldname,k)
                substitue["context"] = re.sub(oldname, name_list[j]["name"], substitue["context"])
                substitue["answers"]["text"][i] = re.sub(oldname, name_list[j]["name"], substitue["answers"]["text"][i])
                substitue["question"] = re.sub(oldname, name_list[j]["name"],substitue["question"])
            substitue["id"] = substitue["id"] + str(j)
            result.append(copy.deepcopy(substitue))

    data_dict = {}
    with open('squad1.1/test_file_10name.json', "w", encoding='utf-8') as writer:
        data_dict['data'] = result
        json.dump(data_dict, writer)

def top_name():
    name_list = load_jsonl("namedata/prediction_name.jsonl")
    name_list_by_rank_em = sorted(name_list, key=lambda x: x.get('exact_match', 99))
    name_list_by_rank_f1 = sorted(name_list, key=lambda x: x.get('f1', 99))
    print(name_list_by_rank_f1[0:10])
    print(name_list_by_rank_em[0:10])
    lll = []
    for item in name_list_by_rank_f1[0:11]:
        lll.append(item['name'])
    for item in name_list_by_rank_em[0:11]:
        lll.append(item['name'])
    sss = set(lll)
    save_jsonl('namedata/name_top.jsonl', sss)

def select_question():
    question_list = load_jsonl("namedata/prediction_question.jsonl")
    question_list_by_rank_em = sorted(question_list, key=lambda x: x.get('exact_match', 101))
    question_list_by_rank_f1 = sorted(question_list, key=lambda x: x.get('f1', 101))
    print(question_list_by_rank_f1[0:10])
    print(question_list_by_rank_em[0:10])
    id_list = []
    for item in question_list:
        if item['exact_match'] == 100:
            assert item['exact_match'] == item['f1']
            id_list.append(item['id'][:-1])
    print(len(id_list))
    squad_examples = load_json("squad1.1/dev-who_gai.json")["data"]
    result = []
    for item in squad_examples:
        if item['id'] in id_list:
            continue
        result.append(item)

    data_dict = {}
    with open('squad1.1/dev-who_gai_387.json', "w", encoding='utf-8') as writer:
        data_dict['data'] = result
        json.dump(data_dict, writer)

def generate_final():
    squad_examples = load_json("squad1.1/dev-who_gai_387.json")["data"]
    onesquad_example = squad_examples[0]
    print(onesquad_example)
    name_list = load_jsonl("namedata/name_top.jsonl")
    result = []
    k = 0
    for squad_example in squad_examples:
        for j in range(len(name_list)):
            k+=1
            substitue = copy.deepcopy(squad_example)
            for i in range(len(substitue["answers"]["answer_start"])):
                oldname = substitue["answers"]["text"][i]
                print(oldname,k)
                substitue["context"] = re.sub(oldname, name_list[j], substitue["context"])
                substitue["answers"]["text"][i] = re.sub(oldname, name_list[j], substitue["answers"]["text"][i])
                substitue["question"] = re.sub(oldname, name_list[j], substitue["question"])
            substitue["id"] = substitue["id"] + str(j)
            result.append(copy.deepcopy(substitue))

    data_dict = {}
    with open('squad1.1/test_file_final.json', "w", encoding='utf-8') as writer:
        data_dict['data'] = result
        json.dump(data_dict, writer)


if __name__ == "__main__":
    squad_examples = load_json("test.json")["data"]
    name_list = load_jsonl("namedata/names_100.jsonl")
    result = []
    k = 0
    for squad_example in squad_examples:
        for j in range(10):
            k += 1
            substitue = copy.deepcopy(squad_example)
            for i in range(len(substitue["answers"]["answer_start"])):
                oldname = substitue["answers"]["text"][i]
                print(oldname, k)
                substitue["context"] = re.sub(oldname, name_list[j]["name"], substitue["context"])
                substitue["answers"]["text"][i] = re.sub(oldname, name_list[j]["name"],
                                                         substitue["answers"]["text"][i])
                substitue["question"] = re.sub(oldname, name_list[j]["name"], substitue["question"])
            substitue["id"] = substitue["id"] + str(j)
            result.append(copy.deepcopy(substitue))

    data_dict = {}
    with open('squad1.1/test_file_10name.json', "w", encoding='utf-8') as writer:
        data_dict['data'] = result
        json.dump(data_dict, writer)
