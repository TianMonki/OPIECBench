import pickle, os
import math
import numpy as np

from test_performance import upper_bound
from helper import *
# method-2
# input_list [(),(),...,()]
import pathlib
import time
from avro.datafile import DataFileReader
from avro.io import DatumReader
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
filename4 = '../file/third_filtration_ent_multi/ent_multi_trpids'
filename5 = '../file/third_filtration_ent_multi/uni_ent'
filename6 = '../file/third_filtration_ent_multi/uni_name'
filename7 = '../file/third_filtration_ent_multi/triples'
filename8 = '../file/third_filtration_ent_multi/np2ent_trpid_cnt_dict'
filename9 = '../file/third_filtration_ent_multi/np_multi_ent_cnt_dict'
filename10 = '../file/third_filtration_ent_multi/ent_multi_np_cnt_dict'
filename11 = '../file/third_filtration_ent_multi/ambi_name'

if not pathlib.Path(filename4).is_file() or not pathlib.Path(filename11).is_file():
    print('load data ... ')
    np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
    np_multi_ent_cnt_dict = pickle.load(open(filename2, 'rb'))
    ent_multi_np_cnt_dict = pickle.load(open(filename3, 'rb'))
    list_len = np.array([len(value) for value in ent_multi_np_cnt_dict.values() if len(value) > 5 and len(value) < 10])
    avg_len = np.mean(list_len)
    os.makedirs('../file/third_filtration_ent_multi')
    np_ambi_dict = dict()
    for ent, nps in ent_multi_np_cnt_dict.items():
        ent_multi_np_cnt_dict[ent] = []
        # first limitation ent multi-name
        if 4 < len(nps) < 10:
            ent_multi_np_cnt_dict[ent] = nps

    np_ent_add_bool = dict()
    trpids = []

    for np_ent in np2ent_trpid_cnt_dict.keys():
        np_ent_add_bool[np_ent] = 0

    # cnt = {S
    #     "01":0,
    #     "12":0,
    #     "23":0,
    #     "34":0,
    #     "45":0,
    #     "56":0,
    #     "67":0,
    #     "78":0,
    # }
    entropy_list = []
    for np, ent_list in np_multi_ent_cnt_dict.items():
        np_multi_ent_cnt_dict[np] = []
        for ent_occ in ent_list:
            ent = ent_occ[0]
            if len(ent_multi_np_cnt_dict[ent]) > 0:
                np_multi_ent_cnt_dict[np].append(ent_occ)
        new_ent_occ_list = np_multi_ent_cnt_dict[np]
        # if len(new_ent_occ_list) > 1:
        entropy = ambi_entropy(new_ent_occ_list)
        np_ambi_dict[np] = entropy
        entropy_list.append(entropy)
        # if 0<= entropy < 1:
        #     cnt['01'] += 1
        # if 1<= entropy < 2:
        #     cnt['12'] += 1
        # if 2<= entropy < 3:
        #     cnt['23'] += 1
        # if 3<= entropy < 4:
        #     cnt['34'] += 1
        # if 4<= entropy < 5:
        #     cnt['45'] += 1
        # if 5<= entropy < 6:
        #     cnt['56'] += 1
        # if 6<= entropy < 7:
        #     cnt['67'] += 1
        # if 7<= entropy < 8:
        #     cnt['78'] += 1
        # second limitation
        if entropy > 2 and entropy < 3:
            for new_ent_occ in new_ent_occ_list:
                ent = new_ent_occ[0]
                if len(ent_multi_np_cnt_dict[ent]) > 0:
                    for name in ent_multi_np_cnt_dict[ent]:
                        # if name[0] == 'Kings':
                        #     print()
                        np_ent_add_bool[(name[0], ent)] = 1
    # print(cnt)
    uni_name = []
    uni_ent = []
    triples = []
    for np_ent, flag in np_ent_add_bool.items():
        if flag == 1:
            ids = np2ent_trpid_cnt_dict[np_ent][0:-1]
            # if np_ent[0] == 'Kings':
            #     print(ids)
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

    ambi_name_rate = 0
    avg_name_entropy = 0
    ambi_name = []
    ambi_name_tri_rat = 0
    ambi_name_tri_tot = 0
    total = 0
    for name in uni_name:
        avg_name_entropy += np_ambi_dict[name]
        for tp in np_multi_ent_cnt_dict[name]:
            if tp[0] in uni_ent:
                total += tp[1]
        # total += sum(tp[1] for tp in np_multi_ent_cnt_dict[name])
        np_multi_ent_cnt = [tp for tp in np_multi_ent_cnt_dict[name] if tp[0] in uni_ent]
        if len(np_multi_ent_cnt_dict[name]) > 1:
            np_multi_ent_cnt = sorted(np_multi_ent_cnt, key=lambda x: x[1], reverse=True)
            ambi_name_tri_tot += sum(tp[1] for tp in np_multi_ent_cnt)
            ambi_name_tri_rat += sum(tp[1] for tp in np_multi_ent_cnt[1:])
            # for tp in np_multi_ent_cnt[1:]:
            #     # if tp[0] in uni_ent:
            #     ambi_name_tri_rat += tp[1]
            ambi_name.append(name)
            ambi_name_rate += 1

    ambi_name_rate /= len(uni_name)
    ambi_name_tri_rat /= len(triples)
    avg_name_entropy /= len(uni_name)
    print('ambi_name_rate : ', ambi_name_rate)
    print('ambi_name_tri_rate : ', ambi_name_tri_rat)
    print('avg_name_entropy : ', avg_name_entropy)
    print('ent_avg_occ : ', ent_avg_occ)

    pickle.dump(trpids, open(filename4, 'wb'))
    pickle.dump(uni_ent, open(filename5, 'wb'))
    pickle.dump(uni_name, open(filename6, 'wb'))
    pickle.dump(triples, open(filename7, 'wb'))
    pickle.dump(np2ent_trpid_cnt_dict, open(filename8, 'wb'))
    pickle.dump(np_multi_ent_cnt_dict, open(filename9, 'wb'))
    pickle.dump(ent_multi_np_cnt_dict, open(filename10, 'wb'))
    pickle.dump(ambi_name, open(filename11, 'wb'))

else:
    trpids = pickle.load(open(filename4, 'rb'))
    uni_ent = pickle.load(open(filename5, 'rb'))
    uni_name = pickle.load(open(filename6, 'rb'))
    triples = pickle.load(open(filename7, 'rb'))
    np2ent_trpid_cnt_dict = pickle.load(open(filename8, 'rb'))
    np_multi_ent_cnt_dict = pickle.load(open(filename9, 'rb'))
    ent_multi_np_cnt_dict = pickle.load(open(filename10, 'rb'))
    ambi_name = pickle.load(open(filename11, 'rb'))

# print(np_multi_ent_cnt_dict['Kings'])
# for k in np2ent_trpid_cnt_dict.keys():
#     if k[0] == 'Kings':
#         print(np2ent_trpid_cnt_dict[k])
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
