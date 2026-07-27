import os, sys
from collections import defaultdict

import numpy as np, json
from nltk.tokenize import word_tokenize
import pathlib
import heapq
from sklearn.metrics.pairwise import cosine_similarity


# from torch.nn.functional import cosine_similarity

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
    for i in range(len(embedding)):
        target_embedding = embedding[i].reshape(1, -1)
        cos_sim = cosine_similarity(embedding, target_embedding)
        cos_sim = cos_sim.tolist()
        cosines.append(cos_sim)

        max_topk = list(map(cos_sim.index, heapq.nlargest(k + 1, cos_sim)))
        max_topk.remove(i)
        max_topks.append(max_topk)

    return max_topks, cosines


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


# def merge_cls(seed_pairs, cls2trp):
#     sets = [set(pair) for pair in seed_pairs]
#
#     i = 0
#     while i < len(sets):
#         merged = False
#         j = i + 1
#         while j < len(sets):
#             if sets[i].intersection(sets[j]):
#                 sets[i] = sets[i].union(sets[j])
#                 del sets[j]
#                 merged = True
#             else:
#                 j += 1
#         if not merged:
#             i += 1
#
#     merge_list = [tuple(sorted(s)) for s in sets]
#     rm_index_list = sorted([idx for i in merge_list for idx in i], reverse=True)
#
#     cls2trp_cy = cls2trp.copy()
#     for idx in rm_index_list:
#         del cls2trp_cy[idx]
#
#     merge_cls2trp = []
#     merge_cls2trp += cls2trp_cy
#     for i in merge_list:
#         trps = []
#         for j in i:
#             trps += cls2trp[j]
#         merge_cls2trp.append(sorted(trps))
#
#     # merge_cls2trp += cls2trp_cy
#
#     return merge_cls2trp

def merge_cls(seed_pairs, cls2trp):
    num_classes = len(cls2trp)

    graph = defaultdict(list)
    for u, v in seed_pairs:
        if 0 <= u < num_classes and 0 <= v < num_classes:
            graph[u].append(v)
            graph[v].append(u)

    visited = set()
    all_cls_groups = []
    merged_trp_data = []

    for i in range(num_classes):
        if i not in visited:
            # 发现了一个新组（包括独立的节点）
            current_group_ids = []
            current_trps = []

            stack = [i]
            visited.add(i)

            while stack:
                node = stack.pop()
                current_group_ids.append(node)
                current_trps.extend(cls2trp[node])

                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)

            # 3. 保存这个连通分量的结果
            all_cls_groups.append(tuple(sorted(current_group_ids)))
            merged_trp_data.append(sorted(current_trps))

    return merged_trp_data, all_cls_groups

def process_duplicates(str_list):
    count_dict = {}
    for s in str_list:
        count_dict[s] = count_dict.get(s, 0) + 1
    index_dict = {}
    result = []
    for s in str_list:
        if count_dict[s] > 1:
            current_index = index_dict.get(s, 0)
            result.append(f"{s}  {current_index}")
            index_dict[s] = current_index + 1
        else:
            result.append(s)
    return result
