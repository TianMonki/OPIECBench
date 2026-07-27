# find_most_frequent_entity2np2triple

# filtration 2 entity frequency >= 2
# in filtration_frequency_triple_id is ok
# filtration_frequency_triple_id, filtration_frequency_entity, filtration_frequency_np has pass the first filtration
from avro.datafile import DataFileReader
from avro.io import DatumReader
import numpy as np
import pathlib
import pickle
import pdb
import time


# open origin dataset system setting
all_file_num = 7789
# all_file_num = 1
all_triple_num = 0
AVRO_SCHEMA_FILE = "../OPIEC-master/avroschema/TripleLinked.avsc"
AVRO_FILE_PART = "OPIEC-Linked-triples/part-r-0"
FILE_PART = str()
SUFFIX = ".avro"

i = 2
j = 1

# filename_final_dataset_OPIEC = './file/final_dataset/OPIEC_53k_triple_id'
# pass_filtration_triple_id = pickle.load(open(filename_final_dataset_OPIEC, 'rb'))
filename_final_dataset_OPIEC_valid = '../file/final_dataset/OPIEC_valid_triple_id'
pass_filtration_triple_id = pickle.load(open(filename_final_dataset_OPIEC_valid, 'rb'))
# filename1 = './file/final_dataset/OPIEC_53k'
filename1 = './file/final_dataset/OPIEC_valid_origin'

# filename7_triple_id = './file/second_filtration/pass/filtration_entity_frequency_' + str(i) + \
#                       'np_frequency_' + str(j) + '_triple_id'
# filename7_entity = './file/second_filtration/pass/filtration_entity_frequency_' + str(i) + \
#                    'np_frequency_' + str(j) + '_entity'
# filename7_np = './file/second_filtration/pass/filtration_entity_frequency_' + str(i) + \
#                'np_frequency_' + str(j) + '_np'

# pass_filtration_entity = pickle.load(open(filename7_entity, 'rb'))
# pass_filtration_np = pickle.load(open(filename7_np, 'rb'))
print('pass_filtration_triple_id:', type(pass_filtration_triple_id),
      len(pass_filtration_triple_id))  # 87513
# print('pass_filtration_entity:', type(pass_filtration_entity),
#       len(pass_filtration_entity))
# print('pass_filtration_np:', type(pass_filtration_np), len(pass_filtration_np))
pass_triple_id = len(pass_filtration_triple_id)
# pass_entity = len(pass_filtration_entity)
# pass_np = len(pass_filtration_np)
print('pass_triple_id:', pass_triple_id)  # 87513
# print('pass_entity:', pass_entity)
# print('pass_np:', pass_np)
print()

OPIEC_dataset = []
if not pathlib.Path(filename1).is_file():
    print('generate OPIEC_dataset :', filename1)
    for FILE_NUM in range(all_file_num):
        if FILE_NUM < 1000:
            if FILE_NUM < 100:
                if FILE_NUM < 10:
                    FILE_PART = str(str(0) + str(0) + str(0) + str(FILE_NUM))
                else:
                    FILE_PART = str(str(0) + str(0) + str(FILE_NUM))
            else:
                FILE_PART = str(str(0) + str(FILE_NUM))
        else:
            FILE_PART = str(FILE_NUM)
        AVRO_FILE = AVRO_FILE_PART + FILE_PART + SUFFIX
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print('FILE_NUM:', FILE_NUM, 'FILE_PART:', FILE_PART, 'AVRO_FILE:', AVRO_FILE)
        # AVRO_FILE = "OPIEC-Linked-triples/part-r-00000.avro"
        reader = DataFileReader(open(AVRO_FILE, "rb"), DatumReader())
        for triple_origin in reader:
            # for k in triple_origin.keys():
            #     print('keys:', type(k), k)
            #     print('values:', type(triple_origin[k]), triple_origin[k])
            #     print()
            # exit()
            quantities_dict = triple_origin['quantities']
            triple_list = [triple_origin['subject'], triple_origin['relation'], triple_origin['object']]
            sentence_linked = triple_origin['sentence_linked']
            sentence = sentence_linked['tokens']
            src_sentences = str()
            for sentence_word in sentence:
                word = sentence_word['word']
                if len(quantities_dict) > 0:
                    for placeholder_str in quantities_dict:
                        information_str = quantities_dict[placeholder_str]
                        quant_str = 'QUANT_' + str(placeholder_str)
                        if word == quant_str:
                            word = information_str
                src_sentences = src_sentences + word + ' '
            src_sentences = src_sentences.strip()
            triple_origin.update({'src_sentences': src_sentences})
            triple = []
            for i in range(len(triple_list)):
                np_string = str()
                NP = triple_list[i]
                if len(NP) > 1:  # start combine words to a np
                    for NP_word in NP:
                        word = NP_word['word']
                        if len(quantities_dict) > 0:
                            for placeholder_str in quantities_dict:
                                information_str = quantities_dict[placeholder_str]
                                quant_str = 'QUANT_' + str(placeholder_str)
                                if word == quant_str:
                                    word = information_str
                        np_string = np_string + word + ' '
                    np_string = np_string.strip()
                else:  # start combine word to a np
                    NP_word = NP[0]
                    np_string = NP_word['word']
                    if len(quantities_dict) > 0:
                        for placeholder_str in quantities_dict:
                            information_str = quantities_dict[placeholder_str]
                            quant_str = 'QUANT_' + str(placeholder_str)
                            if np_string == quant_str:
                                np_string = information_str
                NP_word = NP[0]
                wiki_link = NP_word['w_link']['wiki_link']
                if i == 0:
                    triple_origin.update({'subject_wiki_link': wiki_link})
                if i == 2:
                    triple_origin.update({'object_wiki_link': wiki_link})
                triple.append(np_string)
                if not np_string.find('QUANT_') == -1:
                    triple_id = triple_origin['triple_id']
                    print('triple_id:', triple_id)
                    print('np_string:', np_string)
                    print('quantities_dict:', len(quantities_dict), quantities_dict)
                    exit()
            triple_origin.update({'triple': triple})
            all_triple_num += 1
            triple_id = triple_origin['triple_id']

            sub, rel, obj = triple[0], triple[1], triple[2]
            triple_unique = [sub + '|' + str(triple_id), rel + '|' + str(triple_id), obj + '|' + str(triple_id)]
            triple_origin.update({'triple_unique': triple_unique})

            if triple_id in pass_filtration_triple_id:  # filtration of 1 np to many entity
                OPIEC_dataset.append(triple_origin)
        reader.close()
    pickle.dump(OPIEC_dataset, open(filename1, 'wb'))
    print('all_triple_num:', all_triple_num)  # 5819752
else:
    print('load OPIEC_dataset ... ')
    OPIEC_dataset = pickle.load(open(filename1, 'rb'))

print('OPIEC_dataset: ', type(OPIEC_dataset), len(OPIEC_dataset))  # <class 'list'> 87513


entity_dict, np_dict = dict(), dict()
subject_dict, relation_dict, object_dict = dict(), dict(), dict()
subject_entity_dict, object_entity_dict = dict(), dict()
subject_num, object_num, np_num = 0, 0, 0
for triple_origin in OPIEC_dataset:
    triple_id = triple_origin['triple_id']
    triple = triple_origin['triple']
    subject, relation, object = triple[0], triple[1], triple[2]
    subject_wiki_link, object_wiki_link = triple_origin['subject_wiki_link'], triple_origin['object_wiki_link']
    # print('triple_id:', type(triple_id), triple_id)
    # print('triple:', type(triple), len(triple), triple)
    # print('subject:', type(subject), subject)
    # print('relation:', type(relation), relation)
    # print('object:', type(object), object)
    # print('subject_wiki_link:', type(subject_wiki_link), subject_wiki_link)
    # print('object_wiki_link:', type(object_wiki_link), object_wiki_link)
    # exit()
    if subject not in subject_dict:
        subject_dict.update({subject: [subject_wiki_link]})
    else:
        if subject_wiki_link not in subject_dict[subject]:
            subject_dict[subject].append(subject_wiki_link)
    if subject not in np_dict:
        np_dict.update({subject: [subject_wiki_link]})
    else:
        if subject_wiki_link not in np_dict[subject]:
            np_dict[subject].append(subject_wiki_link)
    if relation not in relation_dict:
        relation_dict.update({relation: 1})
    if object not in object_dict:
        object_dict.update({object: [object_wiki_link]})
    else:
        if object_wiki_link not in object_dict[object]:
            object_dict[object].append(object_wiki_link)
    if object not in np_dict:
        np_dict.update({object: [object_wiki_link]})
    else:
        if object_wiki_link not in np_dict[object]:
            np_dict[object].append(object_wiki_link)
    if subject_wiki_link not in subject_entity_dict:
        subject_entity_dict.update({subject_wiki_link: 1})
    if object_wiki_link not in object_entity_dict:
        object_entity_dict.update({object_wiki_link: 1})
    if subject_wiki_link not in entity_dict:
        entity_dict.update({subject_wiki_link: 1})
    if object_wiki_link not in entity_dict:
        entity_dict.update({object_wiki_link: 1})
for subject in subject_dict.keys():
    subject_num += len(subject_dict[subject])
for object in object_dict.keys():
    object_num += len(object_dict[object])
for np in np_dict.keys():
    np_num += len(np_dict[np])
print('subject_dict:', subject_num, 'object_dict:', object_num, 'np_dict:', np_num, 'relation_dict:', len(relation_dict))
print('subject_entity_dict:', len(subject_entity_dict), 'object_entity_dict:', len(object_entity_dict), 'entity_dict:', len(entity_dict))
print('no repeat')
print('subject_dict:', len(subject_dict), 'object_dict:', len(object_dict), 'np_dict:', len(np_dict))
# subject_dict: 21288 object_dict: 29469 np_dict: 47327 relation_dict: 25858
# subject_entity_dict: 17530 object_entity_dict: 25913 entity_dict: 39469

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


# for k in subject_entity_dict:
#     print('k:', type(k), k)
# print('subject_entity_dict:', type(subject_entity_dict), len(subject_entity_dict))
exit()
# get triple_id2entity_dict and triple_id_np_dict to check OPIEC_dataset

# for k in triple.keys():
#     print('keys:', type(k), k)
#     print('values:', type(triple[k]), triple[k])
#     print()
# use triple.keys() to see every field in the schema (it's a dictionary)
# pdb.set_trace()
