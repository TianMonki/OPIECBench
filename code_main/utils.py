import gc
import random
from collections import defaultdict
from itertools import permutations


class EarlyStopping:
    def __init__(self, patience, delta, trace_func=print, type='loss'):
        """
        Args:
            patience (int): How long to wait after last time validation loss improved.
                            Default: 7
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
            path (str): Path for the checkpoint to be saved to.
                            Default: 'checkpoint.pt'
            trace_func (function): trace print function.
                            Default: print
        """
        self.patience = patience
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        # self.path1 = path1
        # self.path2 = path2
        self.trace_func = trace_func
        self.type = type

    def __call__(self, loss):

        if self.type == 'loss':
            score = -loss

            if self.best_score is None:
                self.best_score = score
                # self.save_checkpoint(loss, model, model2)
            elif score < self.best_score + self.delta:
                self.counter += 1
                if self.counter >= self.patience:
                    self.early_stop = True
            else:
                self.best_score = score
                # self.save_checkpoint(loss, model, model2)
                self.counter = 0

        elif self.type == 'acc':
            score = -loss

            if self.best_score is None:
                self.best_score = score
                # self.save_checkpoint(loss, model, model2)
            elif score > self.best_score + self.delta:
                self.counter += 1
                if self.counter >= self.patience:
                    self.early_stop = True
            else:
                self.best_score = score
                # self.save_checkpoint(loss, model, model2)
                self.counter = 0

    # def save_checkpoint(self, loss, model, model2):
    #     # if self.local_rank == 0:
    #     #     torch.save(model.module.state_dict(), self.path)
    #     torch.save(model.state_dict(), self.path1)
    #     torch.save(model2.state_dict(), self.path2)
    #
    #     self.val_loss_min = loss


# 归一化
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


# 余弦相似度
def cos_sim(a, b):
    # a = np.array(a)
    # b = np.array(b)
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    cos_theta = float(np.dot(a, b) / (a_norm * b_norm))
    cos_theta = 0.5 + 0.5 * cos_theta
    return cos_theta


# 余弦距离
def cosine_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    cos_theta = float(np.dot(a, b) / (a_norm * b_norm))
    cos_distance = 1 - cos_theta
    # cos_distance = 0.5 - 0.5 * cos_theta
    return cos_distance


import os, sys
import numpy as np, json
from nltk.tokenize import word_tokenize
import pathlib
import heapq
from sklearn.metrics.pairwise import cosine_similarity


def checkFile(filename):
    return pathlib.Path(filename).is_file()


def invertDic(my_map, struct='o2o'):
    inv_map = {}

    if struct == 'o2o':  # Reversing one-to-one dictionary
        for k, v in my_map.items():
            inv_map[v] = k

    elif struct == 'm2o':  # Reversing many-to-one dictionary
        for k, v in my_map.items():
            inv_map[v] = inv_map.get(v, [])
            inv_map[v].append(k)

    elif struct == 'm2ol':  # Reversing many-to-one list dictionary
        for k, v in my_map.items():
            for ele in v:
                inv_map[ele] = inv_map.get(ele, [])
                inv_map[ele].append(k)

    elif struct == 'm2os':
        for k, v in my_map.items():
            for ele in v:
                inv_map[ele] = inv_map.get(ele, set())
                inv_map[ele].add(k)

    elif struct == 'ml2o':  # Reversing many_list-to-one dictionary
        for k, v in my_map.items():
            for ele in v:
                inv_map[ele] = inv_map.get(ele, [])
                inv_map[ele] = k
    return inv_map


# Get embedding of words from gensim word2vec model
# clean_list == phr_list
def getEmbeddings(model, phr_list, embed_dims):
    embed_list = []
    all_num, oov_num, oov_rate = 0, 0, 0
    for phr in phr_list:
        if phr in model.vocab:
            embed_list.append(model.word_vec(phr))
            all_num += 1
        else:
            vec = np.zeros(embed_dims, np.float32)
            wrds = word_tokenize(phr)
            for wrd in wrds:
                all_num += 1
                if wrd in model.vocab:
                    vec += model.word_vec(wrd)
                else:
                    vec += np.random.randn(embed_dims)
                    oov_num += 1
            if len(wrds) == 0:
                embed_list.append(vec / 10000)
            else:
                embed_list.append(vec / len(wrds))
    oov_rate = oov_num / all_num
    print('oov rate:', oov_rate, 'oov num:', oov_num, 'all num:', all_num)
    return np.array(embed_list)


# embedding ndarray_list
def getTopk(embedding, k):
    max_topks, cosines = [], []
    embedding = np.array(embedding)

    sim_matrix = cosine_similarity(embedding)
    np.fill_diagonal(sim_matrix,-1)
    topk_indices = np.argsort(sim_matrix,axis=1)[:,-k:]
    sorted_topk = topk_indices[:,::-1]

    return sorted_topk


# def union_topk(str_topks, con_topks):
#     union_topks = []
#     for s, c in str_topks, con_topks:
#         union_topks.append(list(set(s).union(set(c))))
#     return union_topks
#
# def intersection_topk(str_topks, con_topks):
#     intersection_topks = []
#     for i in range(len(str_topks)):
#         intersection_topks.append(list(set(str_topks[i]).intersection(set(con_topks[i]))))
#
#     return intersection_topks

def merge_dicts(dict1, dict2, intersection_seed, union_seed):
    all_result = dict()
    intersection_result = dict()
    union_result = dict()
    for k, v in dict1.items():
        all_result[k] = (v[0] + dict2[k][0]) / 2

    for i in intersection_seed:
        intersection_result[i] = all_result[i]
    for j in union_seed:
        union_result[j] = all_result[j]

    return all_result, intersection_result, union_result


def get_sims_dict(dict1, dict2):
    # key_set1 = set(dict1.keys())
    # key_set2 = set(dict2.keys())
    # if key_set1 == key_set2:
    #     print()
    sims_res = dict()
    # for name in dict1.keys():
    #     # if name in dict2.keys():
    #     for k, v in dict2[name].items():
    #         sims = []
    #         for ent, des_embed in dict1[name].items():
    #             # sim = cosine_similarity(v, des_embed)[0][0]
    #             sim = cos_sim(v, des_embed.T)
    #             # sim = 0.5 + 0.5 * sim
    #             sims.append((ent, sim))
    #         sims.sort(key=lambda x: x[1], reverse=True)
    #         if k not in sims_res.keys():
    #             sims_res[k] = sims
    for k, v in dict1.items():
        cand_ent = dict2[k]
        if len(cand_ent) == 0:
            print()
        for sub_k, sub_v in v.items():
            sims = []
            for ent, emb in cand_ent.items():
                sim = cos_sim(sub_v, emb.T)
                sims.append((ent, sim))
            sims.sort(key=lambda x: x[1], reverse=True)
            sims_res[sub_k] = sims
    return sims_res


def get_random_dict(dict1, dict2):
    link_res = dict()
    # for name in dict1.keys():
    #     # if name in dict2.keys():
    #     for k, v in dict2[name].items():
    #         sims = []
    #         for ent, des_embed in dict1[name].items():
    #             # sim = cosine_similarity(v, des_embed)[0][0]
    #             sim = cos_sim(v, des_embed.T)
    #             # sim = 0.5 + 0.5 * sim
    #             sims.append((ent, sim))
    #         sims.sort(key=lambda x: x[1], reverse=True)
    #         if k not in sims_res.keys():
    #             sims_res[k] = sims
    for k, v in dict1.items():
        cand_ent = dict2[k]
        for sub_k in v.keys():
            link = random.choice(list(cand_ent.keys()))
            link_res[sub_k] = link
    return link_res


# 拼接三元组（考虑所有可能的拼接顺序）
def concatenate_triples_all_permutations(name, cls_ids, triples):
    cluster_triples = [triples[i] for i in cls_ids]
    cnt = 0
    max_permutations = 50
    concatenated_texts = []
    for perm in permutations(cluster_triples):
        if cnt >= max_permutations:
            break
        text = " [TRI] ".join(["".join(triple) for triple in perm])
        text = "sub" + " [TRI] " + text
        concatenated_texts.append(text)
        cnt += 1
    # all_perm = list(permutations(cluster_triples))
    # if len(all_perm) > 100:
    #     all_perm = all_perm[:100]
    # for perm in all_perm:
    #     text = " [TRI] ".join(["".join(triple) for triple in perm])
    #     concatenated_texts.append(text)
    # del all_perm
    # gc.collect()
    return concatenated_texts


# 计算余弦相似度并找出最相似的实体索引
def get_most_similar_entity_index(cluster_embedding, candidate_embeddings):
    similarities = cosine_similarity(cluster_embedding, candidate_embeddings)
    return np.argmax(similarities)


def get_sims_dict_forkl(dict1, dict2):
    sims_res = dict()
    for name in dict1.keys():
        # if name in dict2.keys():
        for k, v in dict2[name].items():
            sims = []
            for ent, des_embed in dict1[name].items():
                # sim = cosine_similarity(v, des_embed)[0][0]
                sim = cos_sim(v, des_embed.T)
                # sim = 0.5 + 0.5 * sim
                sims.append(sim)
            sims_res[k] = np.array(sims) / np.sum(np.array(sims))
    return sims_res


def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def get_vote_result_wrong(tri_link_res, cls_trps):
    conf_list = []
    for id in cls_trps:
        conf = sigmoid((tri_link_res[id][0][1] - tri_link_res[id][1][1]) / tri_link_res[id][0][1])
        conf_list.append(conf)
    sum_1 = sum(conf_list)
    p_list = []
    ent_cand_list = [pair[0] for pair in tri_link_res[cls_trps[0]]]
    for ent in ent_cand_list:
        sum_2 = 0
        for i, cls_trp_id in enumerate(cls_trps):
            for lk_sc in tri_link_res[cls_trp_id]:
                if lk_sc[0] == ent:
                    sum_2 += conf_list[i]
                    break
        p_thres = sum_2 / sum_1
        p_list.append(p_thres)

    ent_p = max(p_list)
    ent_vote = ent_cand_list[p_list.index(max(p_list))]
    return ent_vote

def get_vote_result(tri_link_res, cls_link_ent, cls_trps):
    conf_list = []
    conf_list_ent = []
    for id in cls_trps:
        conf = sigmoid((tri_link_res[id][0][1] - tri_link_res[id][1][1]) / tri_link_res[id][0][1])
        conf_list.append(conf)
        if tri_link_res[id][0][0] == cls_link_ent:
            conf_list_ent.append(conf)
    sum_1 = sum(conf_list)
    sum_2 = sum(conf_list_ent)
    ent_p = sum_2 / sum_1
    # ent_cand_list = [pair[0] for pair in tri_link_res[cls_trps[0]]]
    # for ent in ent_cand_list:
    #     sum_2 = 0
    #     for i, cls_trp_id in enumerate(cls_trps):
    #         for lk_sc in tri_link_res[cls_trp_id]:
    #             if lk_sc[0] == ent:
    #                 sum_2 += conf_list[i]
    #                 break
    #     p_thres = sum_2 / sum_1
    #     p_list.append(p_thres)
    #
    # ent_p = max(p_list)
    # ent_vote = ent_cand_list[p_list.index(max(p_list))]
    return ent_p


def group_by_ent(tuple_list):
    ent_dict = defaultdict(list)
    for name, ent, id in tuple_list:
        ent_dict[ent].append((name, id))
    result = []
    for ent, name_id_pairs in ent_dict.items():
        if len(name_id_pairs) > 1:
            for i in range(len(name_id_pairs)):
                for j in range(i + 1, len(name_id_pairs)):
                    name1, id1 = name_id_pairs[i]
                    name2, id2 = name_id_pairs[j]
                    # if name1 != name2:
                    result.append((name1, name2, ent, id1, id2))
    return result
