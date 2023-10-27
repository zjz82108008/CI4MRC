import re
import string
import torch
import json

def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return "".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))

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

def name_insert(template, names):
    name_regex = re.compile("<name(\\d)>")
    return name_regex.sub(lambda m: names[int(m.group(1))-1], template)

def pair_name(names_female,names_male):
    all_pairs = []
    pair_idx = 1
    for idx1, name1 in enumerate(names_female):
        for name2 in names_female[idx1 + 1:]:
            all_pairs.append({"id": pair_idx, "names": [name1['name'], name2['name']]})
            pair_idx += 1
    for idx1, name1 in enumerate(names_male):
        for name2 in names_male[idx1 + 1:]:
            all_pairs.append({"id": pair_idx, "names": [name1['name'], name2['name']]})
            pair_idx += 1
    return all_pairs

def name_template(all_pairs):
    templates = load_jsonl("dataset/name_template/my_templates.jsonl")
    all_instances = []
    for template in templates:
        for pair in all_pairs:
            id_root = f"template-{template['id']}-pair-{pair['id']}-"
            instance = fill_template(template, pair['names'])
            instance['id'] = id_root + "A"
            instance['title'] = "name_template"
            all_instances.append(instance)
            instance = fill_template(template, list(reversed(pair['names'])))
            instance['title'] = "name_template"
            instance['id'] = id_root + "B"
            all_instances.append(instance)
    return all_instances


def fill_template(template, names):
    res = {}
    key_mappings = {'context': 'context', 'question': 'question', 'answer': 'answer'} ##passage
    for key, new_key in key_mappings.items():
        res[new_key] = name_insert(template[key], names)
    return res

def generate_hillary():
    names = load_jsonl("dataset/name_template/names_100.jsonl")
    names_female = []
    names_male = []
    for item in names:
        if "male" in item['attributes']:
            names_male.append(item)
        elif "female" in item['attributes']:
            names_female.append(item)
    all_pairs = pair_name(names_female,names_male)
    hillary_pair = []
    for item in all_pairs:
        if "Hillary" in item['names']:
            hillary_pair.append(item)
    print(len(hillary_pair))
    hillary_instances = name_template(hillary_pair)
    for item in hillary_instances:
        ori_answer = item.pop('answer')
        answers = {"answer_start": [0, 0, 0], "text": [ori_answer, ori_answer, ori_answer]}
        item["answers"] = answers
    print(len(hillary_instances))
    save_file = {"data": hillary_instances}
    save_json("dataset/name_template/hillary_instances.json", save_file)

def generate_all():
    names = load_jsonl("dataset/name_template/names_100.jsonl")
    names_female = []
    names_male = []
    for item in names:
        if "male" in item['attributes']:
            names_male.append(item)
        elif "female" in item['attributes']:
            names_female.append(item)
    all_pairs = pair_name(names_female, names_male)
    all_instance = name_template(all_pairs)
    print(len(all_instance))
    # save_jsonl("dataset/name_template/BiasSQuADNames.jsonl", all_instance)
    for item in all_instance:
        ori_answer = item.pop('answer')
        answers = {"answer_start": [0], "text": [ori_answer]}
        item["answers"] = answers
    print(len(all_instance))
    save_file = {"data": all_instance}
    save_json("dataset/name_template/all_instances.json", save_file)

# def test_squad_flip():
#     aaa = load_jsonl("dataset/analysis/squad_387_xlnet_mlp.jsonl")
#     bbb = load_jsonl("dataset/analysis/squad_5418_xlnet_mlp.jsonl")
#     count = 0
#     for i in range(387):
#         for j in range(14):
#             if(aaa[i]['is_correct']==bbb[i*14+j]['is_correct']):
#                 count+=1
#     print(count)
#     print(count/5418)
#     print(1-count/5418)

# def test_all_instance():
#     aaa = load_jsonl("dataset/analysis/all_instance_xlnet_dropout015.jsonl")
#
#     names = load_jsonl("dataset/name_template/names_100.jsonl")
#     names_female = []
#     names_male = []
#     for item in names:
#         if "male" in item['attributes']:
#             names_male.append(item)
#         elif "female" in item['attributes']:
#             names_female.append(item)
#     all_pairs = pair_name(names_female, names_male)
#
#     lenaaa = len(aaa)
#     per_template = {}
#     per_template_flip = {}
#     num_correct = 0
#     num_flip = 0
#     for i in range(15):
#         per_template["template-{}".format(i)] = 0
#         per_template_flip["template-flip-{}".format(i)] = 0
#
#     for i in range(0, lenaaa, 2):
#         item1 = aaa[i]
#         item2 = aaa[i+1]
#         stra = item1['id'].split('-')
#         correct = item1['is_correct'] + item2['is_correct']
#         num_correct += correct
#         if correct == 1:
#             num_flip += 1
#             per_template_flip["template-flip-{}".format(stra[1])] += 1
#         per_template["template-{}".format(stra[1])] += correct
#
#     print('num_correct: ', num_correct/lenaaa)
#     print('num_flip: ', num_flip*2/lenaaa)
#     per_template_flip = sorted(per_template_flip.items(), key=lambda x : x[1], reverse=True)
#     topfive = 0
#     five = 0
#     for item in per_template_flip:
#         topfive += item[1]
#         five+=1
#         if five == 5: break
#     print('num_flip_top5: ', topfive*6/lenaaa)


if __name__ == "__main__":
    # print(normalize_answer('Levi \'s Stadium in the San Francisco Bay Area at Santa Clara , California'))
    print('begin')
    aaa = load_jsonl("dataset/analysis/all_instance_deberta_dropout.jsonl")

    names = load_jsonl("dataset/name_template/names_100.jsonl")
    names_female = []
    names_male = []
    for item in names:
        if "male" in item['attributes']:
            names_male.append(item)
        elif "female" in item['attributes']:
            names_female.append(item)
    all_pairs = pair_name(names_female, names_male)

    lenaaa = len(aaa)
    per_template = {}
    per_template_flip = {}
    num_correct = 0
    num_flip = 0
    for i in range(15):
        per_template["template-{}".format(i)] = 0
        per_template_flip["template-flip-{}".format(i)] = 0

    for i in range(0, lenaaa, 2):
        item1 = aaa[i]
        item2 = aaa[i+1]
        stra = item1['id'].split('-')
        correct = item1['is_correct'] + item2['is_correct']
        num_correct += correct
        if correct == 1:
            num_flip += 1
            per_template_flip["template-flip-{}".format(stra[1])] += 1
        per_template["template-{}".format(stra[1])] += correct

    print('num_correct: ', num_correct/lenaaa)
    print('num_flip: ', num_flip*2/lenaaa)
    per_template_flip = sorted(per_template_flip.items(), key=lambda x : x[1], reverse=True)
    topfive = 0
    five = 0
    for item in per_template_flip:
        topfive += item[1]
        five+=1
        if five == 5: break
    print('num_flip_top5: ', topfive*6/lenaaa)
    print('end')




