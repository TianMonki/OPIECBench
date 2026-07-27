# in triple_id is ok
# filtration_frequency_triple_id, filtration_frequency_entity, filtration_frequency_np has pass the first filtration
import fastavro
from avro.datafile import DataFileReader
from avro.io import DatumReader
import numpy as np
import pathlib
import pickle
import pdb
import time
import json
import argparse
import os

# open origin dataset system setting
all_file_num = 7789
all_triple_num = 0
AVRO_SCHEMA_FILE = "../OPIEC-master/avroschema/TripleLinked.avsc"
AVRO_FILE_PART = "../OPIEC-Linked/OPIEC-Linked-triples-Final/part-r-0"

FILE_PART = str()
SUFFIX = ".avro"

with open(AVRO_SCHEMA_FILE, 'r') as f:
    schema = json.load(f)
parser = argparse.ArgumentParser(description='Materialize a final OPIEC benchmark dataset')
parser.add_argument('dataset', choices=['name_ambi', 'ent_multi'],
                    help='name_ambi=OPIEC-Poly; ent_multi=OPIEC-Syno')
args = parser.parse_args()

dataset_config = {
    'name_ambi': (
        '../file/third_filtration_name_ambi/name_ambi_trpids',
        '../data/name_ambi/OPIEC_name_ambi_triples',
    ),
    'ent_multi': (
        '../file/third_filtration_ent_multi/ent_multi_trpids',
        '../data/ent_multi/OPIEC_ent_multi_triples',
    ),
}
filename_final_trpid, filename1 = dataset_config[args.dataset]
os.makedirs(os.path.dirname(filename1), exist_ok=True)

pass_filtration_triple_id = pickle.load(open(filename_final_trpid, 'rb'))
pass_filtration_triple_id = set(pass_filtration_triple_id)
print('pass_filtration_triple_id:', type(pass_filtration_triple_id),
      len(pass_filtration_triple_id))
pass_triple_id = len(pass_filtration_triple_id)
print('pass_triple_id:', pass_triple_id)
print()

OPIEC_dataset = []
# duplicate_triple = []
# tri_dict = pickle.load(open('../file/second_filtration/tri_dict_new', 'rb'))
# for v in tri_dict.values():
#     if len(v) > 1:
#         links = set()
#         link_trp_ids = []
#         for link_id in v:
#             link_trp_ids.append(link_id[1])
#             if link_id[0] not in links:
#                 links.add(link_id[0])
#         if len(links) > 1:
#             duplicate_triple += link_trp_ids
# print()
# # id_set = set()
# duplicate_triple = set(duplicate_triple)
# redirect_pairs = pickle.load(open('../file/second_filtration/redirect_pairs', 'rb'))
# no_des_ent = pickle.load(open('../file/second_filtration/no_desc_ent', 'rb'))
# no_des_ent = set(no_des_ent)
# names = set(redirect_pairs.keys())
# redirect = {}
# for inner_dict in redirect_pairs.values():
#     redirect.update(inner_dict)
# set_redirect_keys = set(redirect.keys())
# num = 0
# tri_dict = {}
if not pathlib.Path(filename1).is_file():
    print('generate OPIEC_dataset :', filename1)
    sub_list = set()
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
        reader = DataFileReader(open(AVRO_FILE, "rb"), DatumReader())
        # reader = pickle.load(open(AVRO_FILE, "rb"))
        # triple_origin_record = []
        for triple_origin in reader:
            trp_id = triple_origin['triple_id']
            # triple_origin_record.append(triple_origin)
            if trp_id in pass_filtration_triple_id:
                # sub_link = triple_origin['subject_wiki_link']
                # triple = triple_origin['triple']
                # triple_str = " ".join(triple)
                # if triple_str not in tri_dict.keys():
                #     tri_dict[triple_str] = sub_link
                # else:
                #     if sub_link != tri_dict[triple_str]:
                #         print('rm duplicate wrong!')
                    # tri_dict[triple_str].append((sub_link, trp_id))
                # if sub_link in set_redirect_keys:
                #     print('redirect wrong!')
                #     num += 1
                # quantities_dict = triple_origin['quantities']
                # triple_list = [triple_origin['subject'], triple_origin['relation'], triple_origin['object']]
                # sentence_linked = triple_origin['sentence_linked']
                # sentence = sentence_linked['tokens']
                # src_sentences = str()
                # for sentence_word in sentence:
                #     word = sentence_word['word']
                #     # if len(quantities_dict) > 0:
                #     #     for placeholder_str in quantities_dict:
                #     #         information_str = quantities_dict[placeholder_str]
                #     #         quant_str = 'QUANT_' + str(placeholder_str)
                #     #         if word == quant_str:
                #     #             word = information_str
                #     src_sentences = src_sentences + word + ' '
                # src_sentences = src_sentences.strip()
                # triple_origin.update({'src_sentences': src_sentences})
                # triple = []
                # for i in range(len(triple_list)):
                #     np_string = str()
                #     NP = triple_list[i]
                #     if len(NP) > 1:  # start combine words to a np
                #         for NP_word in NP:
                #             word = NP_word['word']
                #             # if len(quantities_dict) > 0:
                #             #     for placeholder_str in quantities_dict:
                #             #         information_str = quantities_dict[placeholder_str]
                #             #         quant_str = 'QUANT_' + str(placeholder_str)
                #             #         if word == quant_str:
                #             #             word = information_str
                #             np_string = np_string + word + ' '
                #         np_string = np_string.strip()
                #     else:  # start combine word to a np
                #         NP_word = NP[0]
                #         np_string = NP_word['word']
                #         # if len(quantities_dict) > 0:
                #         #     for placeholder_str in quantities_dict:
                #         #         information_str = quantities_dict[placeholder_str]
                #         #         quant_str = 'QUANT_' + str(placeholder_str)
                #         #         if np_string == quant_str:
                #         #             np_string = information_str
                #     NP_word = NP[0]
                #     wiki_link = NP_word['w_link']['wiki_link']
                #     if i == 0:
                #         triple_origin.update({'subject_wiki_link': wiki_link})
                #     if i == 2:
                #         triple_origin.update({'object_wiki_link': wiki_link})
                #     triple.append(np_string)
                #     # if not np_string.find('QUANT_') == -1:
                #     #     print('triple_id:', triple_id)
                #     #     print('np_string:', np_string)
                #     #     print('quantities_dict:', len(quantities_dict), quantities_dict)
                #     #     exit()
                # triple_origin.update({'triple': triple})
                # triple_id = triple_origin['triple_id']
                #
                # sub, rel, obj = triple[0], triple[1], triple[2]
                # sub_list.add(sub)
                # triple_unique = [sub + '|' + str(triple_id), rel + '|' + str(triple_id), obj + '|' + str(triple_id)]
                # triple_origin.update({'triple_unique': triple_unique})
                OPIEC_dataset.append(triple_origin)
        reader.close()
        # with open(AVRO_FILE_NEW, 'wb') as out:
        #     fastavro.writer(out, fastavro.parse_schema(schema), reader)
    pickle.dump(OPIEC_dataset, open(filename1, 'wb'))
    # print(len(sub_list))
else:
    print('load OPIEC_dataset ... ')
    OPIEC_dataset = pickle.load(open(filename1, 'rb'))

print('OPIEC_dataset: ', type(OPIEC_dataset), len(OPIEC_dataset))  # <class 'list'> 87513
sub_set = set()
uni_ent = set()
for triple in OPIEC_dataset:
    sub, rel, obj = triple['triple'][0], triple['triple'][1], triple['triple'][2]
    uni_ent.add(triple['subject_wiki_link'])
    # uni_ent.add(triple['object_wiki_link'])
    sub_set.add(sub)
print(len(sub_set))
print(len(uni_ent))
