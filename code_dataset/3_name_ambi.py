import os
import pickle
import math

from test_performance import upper_bound
from helper import *
# method-1
# input_list [(),(),...,()]
import pathlib
import time
# from avro.datafile import DataFileReader
# from avro.io import DatumReader
from collections import defaultdict as ddict
from collections import Counter


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


def most_occ_ent(v):
    data = Counter(v)
    return data.most_common(1)[0][0]


filename1 = '../file/second_filtration/np2ent_trpid_cnt_dict'
filename2 = '../file/second_filtration/np_multi_ent_cnt_dict'
filename3 = '../file/second_filtration/ent_multi_np_cnt_dict'
filename4 = '../file/third_filtration_name_ambi/name_ambi_trpids'
filename5 = '../file/third_filtration_name_ambi/uni_ent'
filename6 = '../file/third_filtration_name_ambi/uni_name'
filename7 = '../file/third_filtration_name_ambi/triples'
filename8 = '../file/third_filtration_name_ambi/np2ent_trpid_cnt_dict'
filename9 = '../file/third_filtration_name_ambi/np_multi_ent_cnt_dict'
filename10 = '../file/third_filtration_name_ambi/ent_multi_np_cnt_dict'

if not pathlib.Path(filename4).is_file() or not pathlib.Path(filename10).is_file():
    print('load data ... ')
    np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
    np_multi_ent_cnt_dict = pickle.load(open(filename2, 'rb'))
    ent_multi_np_cnt_dict = pickle.load(open(filename3, 'rb'))
    np_ambi_dict = dict()
    os.makedirs( '../file/third_filtration_name_ambi')

    np_multi_ent_cnt_dict_cy = np_multi_ent_cnt_dict.copy()
    for name, ent_occs in np_multi_ent_cnt_dict.items():
        np_multi_ent_cnt_dict_cy[name] = []
        for ent_occ in ent_occs:
            if ent_occ[1] > 1:
                np_multi_ent_cnt_dict_cy[name].append(ent_occ)
        ent_occ_list = np_multi_ent_cnt_dict_cy[name]
        if len(ent_occ_list) > 1:
            entropy = ambi_entropy(ent_occ_list)
            np_ambi_dict[name] = entropy

    np_ent_add_bool = dict()
    trpids = []
    for np_ent in np2ent_trpid_cnt_dict.keys():
        np_ent_add_bool[np_ent] = 0

    ent_multi_np_cnt_dict_cy = ent_multi_np_cnt_dict.copy()
    for ent, name_occs in ent_multi_np_cnt_dict.items():
        ent_multi_np_cnt_dict_cy[ent] = []
        for name_occ in name_occs:
            name = name_occ[0]
            if name in np_ambi_dict.keys():
                # first limitation
                if np_ambi_dict[name] > 1.5 and np_ambi_dict[name] < 4:
                # if np_ambi_dict[name] > 1.5 :
                    ent_multi_np_cnt_dict_cy[ent].append(name)
        names = ent_multi_np_cnt_dict_cy[ent]
        # second limitation
        if 3 < len(names) < 10:
            for name in names:
                for ent_occ in np_multi_ent_cnt_dict_cy[name]:
                    if not np_ent_add_bool[(name, ent_occ[0])]:
                        np_ent_add_bool[(name, ent_occ[0])] = 1

    uni_name = []
    uni_ent = []
    triples = []
    for np_ent, flag in np_ent_add_bool.items():
        if flag == 1:
            ids = np2ent_trpid_cnt_dict[np_ent][0:-1]
            for id in ids:
                triple = dict()
                triple['subject_wiki_link'] = np_ent[1]
                triple['triple_unique'] = [np_ent[0] + '|' + str(id)]
                triples.append(triple)
            trpids += ids
            if np_ent[0] not in uni_name:
                uni_name.append(np_ent[0])
            if np_ent[1] not in uni_ent:
                uni_ent.append(np_ent[1])

    ent_avg_occ = len(trpids) / len(uni_ent)
    print('triple_len : ', len(trpids))
    print('uni_ent : ', len(uni_ent))
    print('uni_name : ', len(uni_name))
    print('ent_avg_occ : ', ent_avg_occ)

    trp_num = 0
    ent_trp_ratio = 0
    tps = []
    for ent in uni_ent:
        ent_trp_num = 0
        multi_nps = ent_multi_np_cnt_dict_cy[ent]
        if (len(multi_nps)) > 1:
            for np in multi_nps:
                # tps += np2ent_trpid_cnt_dict[(np, ent)][0:-1]
                ent_trp_num += np2ent_trpid_cnt_dict[(np, ent)][-1]
                trp_num += np2ent_trpid_cnt_dict[(np, ent)][-1]
        if ent_trp_num > 2:
            ent_trp_ratio += 1

    ent_trp_ratio /= len(uni_ent)
    print('ent_trp_ratio : ', ent_trp_ratio)

    ambi_entropy_sum = 0
    for name in uni_name:
        ambi_entropy_sum += np_ambi_dict[name]
    avg_ambi_entropy = ambi_entropy_sum / len(uni_name)
    print('avg_ambi_entropy : ', avg_ambi_entropy)

    # avg_name_entropy = 0
    # avg_name_entropy /= len(uni_name)
    # print('avg_name_entropy : ', avg_name_entropy)

    pickle.dump(trpids, open(filename4, 'wb'))
    pickle.dump(uni_ent, open(filename5, 'wb'))
    pickle.dump(uni_name, open(filename6, 'wb'))
    pickle.dump(triples, open(filename7, 'wb'))
    pickle.dump(np2ent_trpid_cnt_dict, open(filename8, 'wb'))
    pickle.dump(np_multi_ent_cnt_dict_cy, open(filename9, 'wb'))
    pickle.dump(ent_multi_np_cnt_dict_cy, open(filename10, 'wb'))

else:
    trpids = pickle.load(open(filename4, 'rb'))
    uni_ent = pickle.load(open(filename5, 'rb'))
    uni_name = pickle.load(open(filename6, 'rb'))
    triples = pickle.load(open(filename7, 'rb'))
    np2ent_trpid_cnt_dict = pickle.load(open(filename8, 'rb'))
    np_multi_ent_cnt_dict = pickle.load(open(filename9, 'rb'))
    ent_multi_np_cnt_dict = pickle.load(open(filename10, 'rb'))

true_ent2clust = ddict(set)
ent2clust = ddict(set)
np2most_occ_ent = dict()
for trp in triples:
    sub_u = trp['triple_unique'][0]
    clean_sub_u = sub_u.split('|')[0]
    sub_wiki_link = trp['subject_wiki_link']
    true_ent2clust[sub_u].add(sub_wiki_link)
    if clean_sub_u not in np2most_occ_ent.keys():
        np2most_occ_ent[clean_sub_u] = []
    np2most_occ_ent[clean_sub_u].append(sub_wiki_link)

for k, v in np2most_occ_ent.items():
    np2most_occ_ent[k] = most_occ_ent(v)

for trp in triples:
    sub_u = trp['triple_unique'][0]
    clean_sub_u = sub_u.split('|')[0]
    ent2clust[sub_u].add(np2most_occ_ent[clean_sub_u])

true_clust2ent = invertDic(true_ent2clust, 'm2os')
clust2ent = invertDic(ent2clust, 'm2os')
upper_bound(uni_name, triples, true_clust2ent, true_ent2clust, clust2ent)

# print('load data ... ')
# np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
# np_multi_ent_cnt_dict = pickle.load(open(filename2, 'rb'))
# ent_multi_np_cnt_dict = pickle.load(open(filename3, 'rb'))
# np_ambi_dict = dict()
#
# for name, ent_occs in np_multi_ent_cnt_dict.items():
#     np_multi_ent_cnt_dict[name] = []
#     for ent_occ in ent_occs:
#         if ent_occ[1] > 1:
#             np_multi_ent_cnt_dict[name].append(ent_occ)
#     ent_occ_list = np_multi_ent_cnt_dict[name]
#     if len(ent_occ_list) > 1:
#         entropy = ambi_entropy(ent_occ_list)
#         np_ambi_dict[name] = entropy
#
# np_ent_add_bool = dict()
# trpids = []
# for np_ent in np2ent_trpid_cnt_dict.keys():
#     np_ent_add_bool[np_ent] = 0
#
# for ent, name_occs in ent_multi_np_cnt_dict.items():
#     ent_multi_np_cnt_dict[ent] = []
#     for name_occ in name_occs:
#         name = name_occ[0]
#         if name in np_ambi_dict.keys():
#             # first limitation
#             if np_ambi_dict[name] > 2 and np_ambi_dict[name] < 6:
#                 ent_multi_np_cnt_dict[ent].append(name)
#     names = ent_multi_np_cnt_dict[ent]
#     # second limitation
#     if len(names) > 3:
#         for name in names:
#             for ent_occ in np_multi_ent_cnt_dict[name]:
#                 if np_ent_add_bool[(name, ent_occ[0])] == 0:
#                     np_ent_add_bool[(name, ent_occ[0])] = 1
#                     trpids += np2ent_trpid_cnt_dict[(name, ent_occ[0])][0:-1]
#
# print(len(trpids))

# uni_name, uni_ent = [], []
# for np_ent, flag in np_ent_add_bool.items():
#     if flag == 1:
#         name = np_ent[0]
#         ent = np_ent[1]
#         if name not in uni_name:
#             uni_name.append(name)
#         if ent not in uni_ent:
#             uni_ent.append(ent)
# ent_avg_occ = len(trpids) / len(uni_ent)
# print('uni_name_len : ', len(uni_name))
# print('uni_ent_len : ', len(uni_ent))
# print('ent_avg_occ : ', ent_avg_occ)
#
# trp_num = 0
# ent_trp_ratio = 0
# tps = []
# for ent in uni_ent:
#     ent_trp_num = 0
#     multi_nps = ent_multi_np_cnt_dict[ent]
#     if (len(multi_nps)) > 1:
#         for np in multi_nps:
#             # tps += np2ent_trpid_cnt_dict[(np, ent)][0:-1]
#             ent_trp_num += np2ent_trpid_cnt_dict[(np, ent)][-1]
#             trp_num += np2ent_trpid_cnt_dict[(np, ent)][-1]
#     if ent_trp_num > 2:
#         ent_trp_ratio += 1
#
# ent_trp_ratio /= len(uni_ent)
# print('ent_trp_ratio : ', ent_trp_ratio)
#
# ambi_entropy_sum = 0
# for name in uni_name:
#     ambi_entropy_sum += np_ambi_dict[name]
# avg_ambi_entropy = ambi_entropy_sum / len(uni_name)
# print('avg_ambi_entropy : ', avg_ambi_entropy)
