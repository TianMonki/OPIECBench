# find_every_np2ent_link

# filtration 2 entity frequency >= 2
# in filtration_frequency_triple_id is ok
# filtration_frequency_triple_id, filtration_frequency_entity, filtration_frequency_np has pass the first filtration
import math

from avro.datafile import DataFileReader
from avro.io import DatumReader
import numpy as np
import pathlib
import pickle
import pdb
import time


# input_list [(),(),...,()]
def ambi_entropy(input_list):
    occ_list = []
    total_occ, entropy_val = 0, 0
    for item in input_list:
        occ_list.append(item[1])
        total_occ += item[1]
    occ_list = [occ / total_occ for occ in occ_list]
    for occ in occ_list:
        entropy_val += occ * math.log2(occ)

    return -entropy_val


all_file_num = 7789
filename0 = '../file/first_filtration/multi_entity_triple_id_dict'  # the first filtration
filename1 = '../file/second_filtration/np2ent_trpid_cnt_dict'
filename2 = '../file/second_filtration/np_multi_ent_cnt_dict'
filename3 = '../file/second_filtration/ent_multi_np_cnt_dict'
filename4 = '../file/second_filtration/np_ambi_dict'
filename5 = '../file/second_filtration/ent_ambi_dict'

print('load multi_entity_triple_id dict')
multi_entity_triple_id_dict = pickle.load(open(filename0, 'rb'))
print('multi_entity_triple_id_dict:', type(multi_entity_triple_id_dict),
      len(multi_entity_triple_id_dict))  # <class 'dict'> 1985
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# open origin dataset system setting
all_triple_num, after_first_filtration_triple_num, all_frequency = 0, 0, 0
wiki_links_num = 0
AVRO_SCHEMA_FILE = "../OPIEC-master/avroschema/TripleLinked.avsc"
AVRO_FILE_PART = "../OPIEC-Linked/OPIEC-Linked-triples/part-r-0"
# all_file_num = 7789
FILE_PART = str()
SUFFIX = ".avro"

np2ent_trpid_cnt_dict = dict()
# ent2np_trpid_cnt_dict = dict()
np_multi_ent_cnt_dict = dict()
ent_multi_np_cnt_dict = dict()
np_ambi_dict = dict()
ent_ambi_dict = dict()

if not pathlib.Path(filename1).is_file() or not pathlib.Path(filename3).is_file():
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
        for triple in reader:
            all_triple_num += 1
            triple_id = triple['triple_id']
            if triple_id in multi_entity_triple_id_dict:  # filtration of 1 np to many entity
                continue
            else:
                after_first_filtration_triple_num += 1
                triple_list = [triple['subject']]
                for i in range(len(triple_list)):
                    NP = triple_list[i]
                    np_string = str()
                    if len(NP) > 1:  # start combine words to a np
                        for NP_word in NP:
                            word = NP_word['word']
                            # if word == 'QUAN_S_1':
                            #     print()
                            np_string = np_string + word + ' '
                        np_string = np_string.strip()
                    else:  # start combine word to a np
                        NP_word = NP[0]
                        np_string = NP_word['word']
                    NP_word = NP[0]
                    wiki_link = NP_word['w_link']['wiki_link']
                    if np_string == 'QUANT_S_1 DDT':
                        print()
                    if len(wiki_link) > 0:
                        np2ent = (np_string, wiki_link)
                        if np2ent not in np2ent_trpid_cnt_dict:
                            np2ent_trpid_cnt_dict[np2ent] = []
                        np2ent_trpid_cnt_dict[np2ent].append(triple_id)

        reader.close()

    # np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
    # np_multi_ent ent_multi_np
    for np2ent, trpids in np2ent_trpid_cnt_dict.items():
        np2ent_trpid_cnt_dict[np2ent].append(len(trpids))
        np = np2ent[0]
        ent = np2ent[1]
        occ = np2ent_trpid_cnt_dict[np2ent][-1]
        if np in np_multi_ent_cnt_dict:
            np_multi_ent_cnt_dict[np].append((ent, occ))
        else:
            np_multi_ent_cnt_dict.update({np: [(ent, occ)]})
        if ent in ent_multi_np_cnt_dict:
            if np not in ent_multi_np_cnt_dict[ent]:
                ent_multi_np_cnt_dict[ent].append((np, occ))
        else:
            ent_multi_np_cnt_dict.update({ent: [(np, occ)]})

    # np_multi_ent_cnt ent_multi_np_cnt
    # for np, ent_list in np_multi_ent_cnt_dict.items():
    #     np_multi_ent_cnt_dict.update({np: []})
    #     for ent in ent_list:
    #         np_multi_ent_cnt_dict[np].append((ent, ent_list.count(ent)))
    # for ent, np_list in ent_multi_np_cnt_dict.items():
    #     ent_multi_np_cnt_dict.update({ent: []})
    #     for np in np_list:
    #         ent_multi_np_cnt_dict[ent].append((np, np_list.count(np)))

    pickle.dump(np2ent_trpid_cnt_dict, open(filename1, 'wb'))
    pickle.dump(np_multi_ent_cnt_dict, open(filename2, 'wb'))
    pickle.dump(ent_multi_np_cnt_dict, open(filename3, 'wb'))

else:
    print('load np2entity_dict ... ')
    np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
    # ent2np_trpid_cnt_dict = dict()
    np_multi_ent_cnt_dict = pickle.load(open(filename2, 'rb'))
    ent_multi_np_cnt_dict = pickle.load(open(filename3, 'rb'))

num = len([name for name in np_multi_ent_cnt_dict if len(np_multi_ent_cnt_dict[name]) == 1])

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print('all_triple_num:', all_triple_num)  # demo 5875  5819752
print('after_first_filtration_triple_num:', after_first_filtration_triple_num)  # demo 5875  5817767

print("排序:")
if not pathlib.Path(filename4).is_file() or not pathlib.Path(filename5).is_file():
    for np, ent_list in np_multi_ent_cnt_dict.items():
        if len(ent_list) > 1:
            entropy = ambi_entropy(ent_list)
            np_ambi_dict[np] = entropy

    for ent, np_list in ent_multi_np_cnt_dict.items():
        if len(np_list) > 1:
            entropy = ambi_entropy(np_list)
            ent_ambi_dict[ent] = entropy

    np_ambi_dict = dict(sorted(np_ambi_dict.items(), key=lambda x: x[1], reverse=True))
    ent_ambi_dict = dict(sorted(ent_ambi_dict.items(), key=lambda x: x[1], reverse=True))
    pickle.dump(np_ambi_dict, open(filename4, 'wb'))
    pickle.dump(ent_ambi_dict, open(filename5, 'wb'))

else:
    np_ambi_dict = pickle.load(open(filename4, 'rb'))
    ent_ambi_dict = pickle.load(open(filename5, 'rb'))
    # print(len(np_multi_ent_cnt_dict['railway station']))
exit()
