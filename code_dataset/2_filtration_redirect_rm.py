import math
import pickle
import time
import json
import pathlib
from avro.datafile import DataFileReader
from avro.io import DatumReader
import fastavro

# input_list [(),(),...,()]
from infer_schema import generate_avro_schema


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


# ent_link_dict
# np2ent_trpid_cnt = pickle.load(open('../file/second_filtration/np2ent_trpid_cnt_dict', 'rb'))
# np_multi_ent_ct = pickle.load(open('../file/second_filtration/np_multi_ent_cnt_dict', 'rb'))
# ent_link_dict = dict()
# for key, val in np_multi_ent_ct.items():
#     cand_ent_ct = dict()
#     for ent_ct in val:
#         cand_ent_ct[ent_ct[0]] = ent_ct[1]
#     ent_link_dict[key] = cand_ent_ct
# pickle.dump(ent_link_dict, open('../ent_link_desc/ent_link_dict', 'wb'))

filename0 = '../file/first_filtration/multi_entity_triple_id_dict'  # the first filtration
filename1 = '../file/second_filtration/no_desc_ent'  # the first filtration
filename2 = '../file/second_filtration/redirect_pairs'  # the first filtration
filename3 = '../file/second_filtration/tri_dict_new'  # the first filtration

name_ent_link_dict = pickle.load(open('../ent_link_desc/ent_link_dict', 'rb'))
name_ent_link_des = pickle.load(open('../ent_link_desc/ent_link_des', 'rb'))
# ent_link_dict_ps = copy.deepcopy(ent_link_dict)
# ent_link_description_ps = copy.deepcopy(ent_link_des)

ent_link_des = {}
for inner_dict in name_ent_link_des.values():
    ent_link_des.update(inner_dict)
if not pathlib.Path(filename1).is_file() or not pathlib.Path(filename2).is_file():
    num_none, num_total = 0, 0
    for k, v in name_ent_link_dict.items():
        for sub_k in v.keys():
            num_total += 1
            if len(name_ent_link_des[k][sub_k]) == 0:
                num_none += 1
    ratio = num_none / num_total
    print(ratio)

    redirect_pairs = {}
    des_first_occ = {}
    keys_to_rm_all = []
    k_to_rm_all_set = set()
    no_des_ent = set()
    for key, value in ent_link_des.items():
        if value not in des_first_occ:
            des_first_occ[value] = key
        else:
            redirect_pairs[key] = des_first_occ[value]
    #     redirect_pairs[key] = {}
    #     values = {}
    #     val = ent_link_des[key]
    #     keys_to_rm = []
    #     for sub_k, sub_v in val.items():
    #         if len(sub_v) == 0:
    #             no_des_ent.add(sub_k)
    #             # del ent_link_description_ps[key][sub_k]
    #             # del ent_link_dict_ps[key][sub_k]
    #         else:
    #             # if sub_k == 'Academy Award for Writing Adapted Screenplay':
    #             #     print()
    #             if sub_v in values:
    #                 redirect_pairs[key][sub_k] = values[sub_v]
    #                 keys_to_rm.append(sub_k)
    #                 keys_to_rm_all.append(sub_k)
    #                 k_to_rm_all_set.add(sub_k)
    #             else:
    #                 values[sub_v] = sub_k
    pickle.dump(list(no_des_ent), open(filename1, 'wb'))
    pickle.dump(redirect_pairs, open(filename2, 'wb'))
else:
    no_des_ent = pickle.load(open(filename1, 'rb'))
    redirect_pairs = pickle.load(open(filename2, 'rb'))

multi_entity_triple_id_dict = pickle.load(open(filename0, 'rb'))
print('multi_entity_triple_id_dict:', type(multi_entity_triple_id_dict),
      len(multi_entity_triple_id_dict))  # <class 'dict'> 1985


# open origin dataset system setting
all_triple_num, after_first_filtration_triple_num, after_second_filtration_triple_num = 0, 0, 0
# wiki_links_num = 0
AVRO_SCHEMA_FILE = "../OPIEC-master/avroschema/TripleLinked.avsc"
AVRO_FILE_PART = "../OPIEC-Linked/OPIEC-Linked-triples/part-r-0"
AVRO_FILE_PART_NEW = "../OPIEC-Linked/OPIEC-Linked-triples-New/part-r-0"
AVRO_FILE_PART_FINAL = "../OPIEC-Linked/OPIEC-Linked-triples-Final/part-r-0"
all_file_num = 7789
FILE_PART = str()
SUFFIX = ".avro"
# print(redirect_pairs['QUANT_S_1'])
tri_dict = dict()
num_tri_red = 0
if not pathlib.Path(filename3).is_file():
    for FILE_NUM in range(all_file_num):
        triple_origin_dict = {}
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
        AVRO_FILE_NEW = AVRO_FILE_PART_NEW + FILE_PART + SUFFIX

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print('FILE_NUM:', FILE_NUM, 'FILE_PART:', FILE_PART, 'AVRO_FILE:', AVRO_FILE)
        # AVRO_FILE = "OPIEC-Linked-triples/part-r-00000.avro"
        reader = DataFileReader(open(AVRO_FILE, "rb"), DatumReader())
        triple_origin_record = []
        for triple_origin in reader:
            # print(triple_origin)
            all_triple_num += 1
            triple_id = triple_origin['triple_id']
            quantities_dict = triple_origin['quantities']

            if triple_id in multi_entity_triple_id_dict:  # filtration of 1 np to many entity
                continue
            else:
                after_first_filtration_triple_num += 1
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
                wiki_link_sub = ''
                for i in range(len(triple_list)):
                    NP = triple_list[i]
                    np_string = str()
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
                        # if len(wiki_link) == 0:
                        #     print()
                        wiki_link_sub = wiki_link
                        if len(wiki_link) > 0:
                            # if np_string not in redirect_pairs.keys():
                            #     print()
                            if wiki_link in redirect_pairs.keys():
                                num_tri_red += 1
                                wiki_link_sub = redirect_pairs[wiki_link]
                                # if len(NP) > 1:
                                #     print()
                                for j in range(len(NP)):
                                    triple_origin['subject'][j]['w_link']['wiki_link'] = wiki_link_sub
                        triple_origin.update({'subject_wiki_link': wiki_link_sub})
                    triple.append(np_string)
                    if i == 2:
                        triple_origin.update({'object_wiki_link': wiki_link})
                        triple_str = " ".join(triple)
                        if triple_str not in tri_dict.keys():
                            tri_dict[triple_str] = [(wiki_link_sub, triple_id)]
                        else:
                            tri_dict[triple_str].append((wiki_link_sub, triple_id))

                triple_origin.update({'triple': triple})
                sub, rel, obj = triple[0], triple[1], triple[2]
                triple_unique = [sub + '|' + str(triple_id), rel + '|' + str(triple_id), obj + '|' + str(triple_id)]
                triple_origin.update({'triple_unique': triple_unique})
                triple_origin_record.append(triple_origin)
        pickle.dump(triple_origin_record, open(AVRO_FILE_NEW, 'wb'))
        # schema = generate_avro_schema(triple_origin_record)
        # with open(AVRO_FILE_NEW, 'wb') as out:
        #     fastavro.writer(out, fastavro.parse_schema(schema), triple_origin_record)
        reader.close()

    pickle.dump(tri_dict, open(filename3, 'wb'))
else:
    tri_dict = pickle.load(open(filename3, 'rb'))

print('num redirect triple: ', num_tri_red)
# rm duplicate
filename1 = '../file/second_filtration/np2ent_trpid_cnt_dict'
filename2 = '../file/second_filtration/np_multi_ent_cnt_dict'
filename3 = '../file/second_filtration/ent_multi_np_cnt_dict'
filename4 = '../file/second_filtration/np_ambi_dict'
filename5 = '../file/second_filtration/ent_ambi_dict'

np2ent_trpid_cnt_dict = dict()
# ent2np_trpid_cnt_dict = dict()
np_multi_ent_cnt_dict = dict()
ent_multi_np_cnt_dict = dict()
np_ambi_dict = dict()
ent_ambi_dict = dict()

with open(AVRO_SCHEMA_FILE, 'r') as f:
    schema = json.load(f)
# num = sum(len(list(i)) for i in tri_dict.values())
# id_list = []
# for i in tri_dict.values():
#     for j in i:
#         id_list.append(j[1])
# print()
# id_list = set(id_list)
duplicate_triple = []
for v in tri_dict.values():
    if len(v) > 1:
        links = set()
        link_trp_ids = []
        for link_id in v:
            link_trp_ids.append(link_id[1])
            if link_id[0] not in links:
                links.add(link_id[0])
        if len(links) > 1:
            duplicate_triple += link_trp_ids
print('duplicate_triple: ', len(duplicate_triple))
# id_set = set()
duplicate_triple = set(duplicate_triple)

num = 0
if not pathlib.Path(filename1).is_file() or not pathlib.Path(filename3).is_file():
    for FILE_NUM in range(all_file_num):
        triple_origin_dict = {}
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
        AVRO_FILE_NEW = AVRO_FILE_PART_NEW + FILE_PART + SUFFIX
        AVRO_FILE_FINAL = AVRO_FILE_PART_FINAL + FILE_PART + SUFFIX

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print('FILE_NUM:', FILE_NUM, 'FILE_PART:', FILE_PART, 'AVRO_FILE:', AVRO_FILE_NEW)
        # AVRO_FILE = "OPIEC-Linked-triples/part-r-00000.avro"
        # reader = DataFileReader(open(AVRO_FILE_NEW, "rb"), DatumReader())
        reader = pickle.load(open(AVRO_FILE_NEW, "rb"))
        triple_origin_record = []
        for triple_origin in reader:
            # quantities_dict = triple_origin['quantities']
            # after_first_filtration_triple_num += 1
            triple_id = triple_origin['triple_id']
            # id_set.add(triple_id)
            if triple_id in duplicate_triple:  # filtration of duplicate triples
                continue
            else:
                after_second_filtration_triple_num += 1
                # triple_list = [triple_origin['subject'], triple_origin['relation'], triple_origin['object']]
                # sentence_linked = triple_origin['sentence_linked']
                # sentence = sentence_linked['tokens']
                # src_sentences = str()
                # for sentence_word in sentence:
                #     word = sentence_word['word']
                #     if len(quantities_dict) > 0:
                #         for placeholder_str in quantities_dict:
                #             information_str = quantities_dict[placeholder_str]
                #             quant_str = 'QUANT_' + str(placeholder_str)
                #             if word == quant_str:
                #                 word = information_str
                #     src_sentences = src_sentences + word + ' '
                # src_sentences = src_sentences.strip()
                # triple_origin.update({'src_sentences': src_sentences})

                # triple = []
                # wiki_link_sub = triple_origin['subject'][0]['w_link']['wiki_link']
                wiki_link_sub = triple_origin['subject_wiki_link']
                np_string = triple_origin['triple'][0]
                if len(wiki_link_sub) > 0:
                    np2ent = (np_string, wiki_link_sub)
                    if np2ent not in np2ent_trpid_cnt_dict:
                        np2ent_trpid_cnt_dict[np2ent] = []
                    np2ent_trpid_cnt_dict[np2ent].append(triple_id)
                # if wiki_link_sub in redirect_pairs.keys():
                #     print(redirect_pairs[wiki_link_sub])
                #     num += 1

                # for i in range(len(triple_list)):
                #     NP = triple_list[i]
                #     np_string = str()
                #     if len(NP) > 1:  # start combine words to a np
                #         # if i == 0:
                #         #     print()
                #         for NP_word in NP:
                #             word = NP_word['word']
                #             if len(quantities_dict) > 0:
                #                 for placeholder_str in quantities_dict:
                #                     information_str = quantities_dict[placeholder_str]
                #                     quant_str = 'QUANT_' + str(placeholder_str)
                #                     if word == quant_str:
                #                         word = information_str
                #             np_string = np_string + word + ' '
                #         np_string = np_string.strip()
                #     else:  # start combine word to a np
                #         NP_word = NP[0]
                #         np_string = NP_word['word']
                #         if len(quantities_dict) > 0:
                #             for placeholder_str in quantities_dict:
                #                 information_str = quantities_dict[placeholder_str]
                #                 quant_str = 'QUANT_' + str(placeholder_str)
                #                 if np_string == quant_str:
                #                     np_string = information_str
                #     NP_word = NP[0]
                #     wiki_link = NP_word['w_link']['wiki_link']
                #     if i == 0:
                #         # wiki_link_sub = wiki_link
                #         wiki_link = triple_origin['subject_wiki_link']
                #         if wiki_link_sub in redirect.keys():
                #             wiki_link_sub = redirect[wiki_link]
                #             num += 1
                #             for j in range(len(NP)):
                #                 triple_origin['subject'][j]['w_link']['wiki_link'] = wiki_link_sub
                #         triple_origin.update({'subject_wiki_link': wiki_link_sub})
                #     elif i == 2:
                #         triple_origin.update({'object_wiki_link': wiki_link})
                #     triple.append(np_string)
                #     # if i == 2:
                #     #     if triple not in tri_dict.keys():
                #     #         tri_dict[triple] = [triple_id]
                #     #     else:
                #     #         tri_dict[triple].append(triple_id)
                # triple_origin.update({'triple': triple})
                # sub, rel, obj = triple[0], triple[1], triple[2]
                # # sub_list.add(sub)
                # triple_unique = [sub + '|' + str(triple_id), rel + '|' + str(triple_id), obj + '|' + str(triple_id)]
                # triple_origin.update({'triple_unique': triple_unique})
                triple_origin_record.append(triple_origin)

        # pickle.dump(triple_origin_record, open(AVRO_FILE_NEW, 'wb'))
        with open(AVRO_FILE_FINAL, 'wb') as out:
            fastavro.writer(out, fastavro.parse_schema(schema), triple_origin_record)
        # reader.close()
    # print(after_second_filtration_triple_num)
    print('still not redirect: ', num)
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

    pickle.dump(np_multi_ent_cnt_dict, open(filename2, 'wb'))
    pickle.dump(ent_multi_np_cnt_dict, open(filename3, 'wb'))
    pickle.dump(np2ent_trpid_cnt_dict, open(filename1, 'wb'))

else:
    print('load np2entity_dict ... ')
    np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
    # ent2np_trpid_cnt_dict = dict()
    np_multi_ent_cnt_dict = pickle.load(open(filename2, 'rb'))
    ent_multi_np_cnt_dict = pickle.load(open(filename3, 'rb'))

# for np2ent, trpids in np2ent_trpid_cnt_dict.items():
#     np2ent_trpid_cnt_dict[np2ent].append(len(trpids))
# pickle.dump(np2ent_trpid_cnt_dict, open(filename1, 'wb'))

num = len([name for name in np_multi_ent_cnt_dict if len(np_multi_ent_cnt_dict[name]) == 1])

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print('all_first_filtration_triple_num:', after_first_filtration_triple_num)  # demo 5875  5819752
print('after_second_filtration_triple_num:', after_second_filtration_triple_num)  # demo 5875  5817767

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

exit()
