import copy
import pickle

# filename1 = '../file/second_filtration/np2ent_trpid_cnt_dict'
# filename2 = '../file/second_filtration/np_multi_ent_cnt_dict'
# filename3 = '../file/second_filtration/ent_multi_np_cnt_dict'
# filename4 = '../file/third_filtration_name_ambi/name_ambi_trpids'
# filename5 = '../file/third_filtration_name_ambi/uni_ent'
# filename6 = '../file/third_filtration_name_ambi/uni_name'
# filename7 = '../file/third_filtration_name_ambi/triples'
# filename8 = '../file/second_filtration_old/np2ent_trpid_cnt_dict'
# filename9 = '../file/second_filtration_old/np_multi_ent_cnt_dict'
# filename10 = '../file/second_filtration_old/ent_multi_np_cnt_dict'
#
# np2ent_trpid_cnt_dict = pickle.load(open(filename1, 'rb'))
# # ent2np_trpid_cnt_dict = dict()
# np_multi_ent_cnt_dict = pickle.load(open(filename2, 'rb'))
# ent_multi_np_cnt_dict = pickle.load(open(filename3, 'rb'))
#
# np2ent_trpid_cnt_dict_old = pickle.load(open(filename8, 'rb'))
# # ent2np_trpid_cnt_dict = dict()
# np_multi_ent_cnt_dict_old = pickle.load(open(filename9, 'rb'))
# ent_multi_np_cnt_dict_old = pickle.load(open(filename10, 'rb'))
# ent_link_des = pickle.load(open('../ent_link_desc/ent_link_des', 'rb'))
# # filename7 = '../file/final_dataset_name_ambi_old/OPIEC_name_ambi_triples'
# filename7 = '../file/final_dataset_ent_multi/OPIEC_ent_multi_triples'
# redirect_pairs = pickle.load(open('../file/second_filtration/redirect_pairs', 'rb'))
# no_des_ent = pickle.load(open('../file/second_filtration/no_desc_ent', 'rb'))
# ent_multi_np = pickle.load(open('../file/second_filtration/ent_multi_np_cnt_dict', 'rb'))
#
# no_des_ent = set(no_des_ent)
#
# redirect_ent = set()
# for k,v in redirect_pairs.items():
#     redirect_ent.add(k)
#     redirect_ent.add(v)
# ratio_redirect_ent = len(redirect_ent) / len(list(ent_multi_np.keys()))
# print(ratio_redirect_ent)
# redirect = {}
# for inner_dict in redirect_pairs.values():
#     redirect.update(inner_dict)
# print()
# name_key = set(redirect.keys())
# name_val = set(redirect.values())
# triples = pickle.load(open(filename7, 'rb'))
# num = 0
# for t in triples:
#     sub_link = t['subject_wiki_link']
#     sub = t['triple'][0]
#     if sub in names and sub_link in redirect_pairs[sub].keys():
#         num+=1
#         print()
# print(num)
#
# trpids = pickle.load(open(filename4, 'rb'))
# uni_ent = pickle.load(open(filename5, 'rb'))
# uni_name = pickle.load(open(filename6, 'rb'))
# triples = pickle.load(open(filename7, 'rb'))
# print()

# tri_dict = {}
# tri_dict_part = pickle.load(open('../file/second_filtration/tri_dict_0', 'rb'))
#
# for i in range(4):
#     tri_dict_part = pickle.load(open('../file/second_filtration/tri_dict_' + str(i), 'rb'))
#     for outer_key, inner_list in tri_dict_part.items():
#         if outer_key in tri_dict:
#             tri_dict[outer_key].extend(inner_list)
#         else:
#             tri_dict[outer_key] = inner_list.copy()
# pickle.dump(tri_dict, open('../file/second_filtration/tri_dict_new', 'wb'))

# np2ent_trpid_cnt = pickle.load(open('../file/second_filtration/np2ent_trpid_cnt_dict', 'rb'))
# np_multi_ent_ct = pickle.load(open('../file/second_filtration/np_multi_ent_cnt_dict', 'rb'))
# ent_link_dict = dict()
# for key, val in np_multi_ent_ct.items():
#     cand_ent_ct = dict()
#     for ent_ct in val:
#         cand_ent_ct[ent_ct[0]] = ent_ct[1]
#     ent_link_dict[key] = cand_ent_ct
# pickle.dump(ent_link_dict, open('../ent_link_desc/ent_link_dict', 'wb'))
# ent_link_dict = pickle.load(open('../ent_link_desc/ent_link_dict', 'rb'))
# # ent_link_des = pickle.load(open('../ent_link_desc/ent_link_des', 'rb'))
# num_none, num_total = 0, 0
# for k, v in ent_link_dict.items():
#     for sub_k in v.keys():
#         num_total += 1
#         if len(ent_link_des[k][sub_k]) == 0:
#             num_none += 1
# ratio = num_none / num_total
# print(ratio)
# ent_link_dict_ps = copy.deepcopy(ent_link_dict)
# ent_link_description_ps = copy.deepcopy(ent_link_des)

# redirect_pairs = {}
# keys_to_rm_all = []
# k_to_rm_all_set = set()
# no_des_ent = set()
# for key in ent_link_des:
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
#     # for rm_k in keys_to_rm:
#     #     del ent_link_description_ps[key][rm_k]
#     #     del ent_link_dict_ps[key][rm_k]
#
# # if wiki_link not in no_des_ent:
# #     if wiki_link in redirect_pairs[sub].keys():
# #         wiki_link = redirect_pairs[sub][wiki_link]
# #     if wiki_link == trient[0]:
# #         true_link_ratio += 1
# tri_dict = dict()
# for i, triple in enumerate(self.triples_list):
#     tri_text = triple['raw_triple'][0] + ' ' + triple['raw_triple'][1] + ' ' + triple['raw_triple'][2]
#     sub_link = triple['ent_lnk_sub']
#     if tri_text not in tri_dict.keys():
#         tri_dict[tri_text] = [sub_link]
#     else:
#         tri_dict[tri_text].append(sub_link)
# # # tri_1 = self.triples_list[6]
# # # tri_2 = self.triples_list[23]
# total, unique, num = 0, 0, 0
# for value_list in tri_dict.values():
#     if len(value_list) > 1:
#         num += 1
#         combos = list(itertools.combinations(value_list,2))
#         total += len(combos)
#         for combo in combos:
#             if combo[0] != combo[1]:
#                 unique += 1
# proportion = unique / total
# print(proportion)
# # ent_multi_np = pickle.load(open('../file/second_filtration/np_multi_ent_cnt_dict', 'rb'))
#
# print()

triples = pickle.load(open('../file/OPIEC/reverb45k_change_test', 'rb'))
triples_1 = pickle.load(open('../file/OPIEC/OPIEC59k_valid', 'rb'))

np2ent_trpid_cnt_dict = dict()
# ent2np_trpid_cnt_dict = dict()
np_multi_ent_cnt_dict = dict()
ent_multi_np_cnt_dict = dict()
np_ambi_dict = dict()
ent_ambi_dict = dict()
# reverb
for id, triple in enumerate(triples):
    link = triple['true_link']['subject']
    np_string = triple['triple_norm'][0]
    if len(link) > 0:
        np2ent = (np_string, link)
        if np2ent not in np2ent_trpid_cnt_dict:
            np2ent_trpid_cnt_dict[np2ent] = []
        np2ent_trpid_cnt_dict[np2ent].append(id)
# opiec
# for triple in triples:
#     triple_id = triple['triple_id']
#     triple_list = [triple['subject']]
#     quantities_dict = triple['quantities']
#
#     for i in range(len(triple_list)):
#         NP = triple_list[i]
#         np_string = str()
#         if len(NP) > 1:  # start combine words to a np
#             for NP_word in NP:
#                 word = NP_word['word']
#                 if len(quantities_dict) > 0:
#                     for placeholder_str in quantities_dict:
#                         information_str = quantities_dict[placeholder_str]
#                         quant_str = 'QUANT_' + str(placeholder_str)
#                         if word == quant_str:
#                             word = information_str
#                 np_string = np_string + word + ' '
#             np_string = np_string.strip()
#         else:  # start combine word to a np
#             NP_word = NP[0]
#             np_string = NP_word['word']
#             if len(quantities_dict) > 0:
#                 for placeholder_str in quantities_dict:
#                     information_str = quantities_dict[placeholder_str]
#                     quant_str = 'QUANT_' + str(placeholder_str)
#                     if np_string == quant_str:
#                         np_string = information_str
#
#         NP_word = NP[0]
#         wiki_link = NP_word['w_link']['wiki_link']
#         # if np_string == 'QUANT_S_1 DDT':
#         #     print()
#         if len(wiki_link) > 0:
#             np2ent = (np_string, wiki_link)
#             if np2ent not in np2ent_trpid_cnt_dict:
#                 np2ent_trpid_cnt_dict[np2ent] = []
#             np2ent_trpid_cnt_dict[np2ent].append(triple_id)

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

np_num = 0
np_ambi_num = 0
np_ambi_occ_tot = 0
np_ambi_occ = 0
np_set = len(set(np_multi_ent_cnt_dict.keys()))
for np in np_multi_ent_cnt_dict:
    if len(np_multi_ent_cnt_dict[np]) > 1:
        np_multi_ent_cnt = sorted(np_multi_ent_cnt_dict[np], key=lambda x: x[1], reverse=True)
        np_ambi_num += 1
        np_ambi_occ += sum(tp[1] for tp in np_multi_ent_cnt[1:])
        np_ambi_occ_tot += sum(tp[1] for tp in np_multi_ent_cnt)
        # for ent_cnt in np_multi_ent_cnt_dict[np]:
        #     np_ambi_occ += ent_cnt[1]

np_ambi_rate = np_ambi_num / len(np_multi_ent_cnt_dict)
np_ambi_occ_rate = np_ambi_occ / len(triples)

print(np_ambi_rate)
print(np_ambi_occ_rate)
