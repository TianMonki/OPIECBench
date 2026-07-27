# import gensim, itertools, pickle, time, numpy
# from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, homogeneity_completeness_v_measure
# from test_performance import *
# from train_embedding_model import Train_Embedding_Model, pair2triples
# from model_Bert import *
# from metrics import *
# import os, math
# import collections
# 
# def get_seed_pair_list_strict(embedding, k):
#     sub_len = len(embedding)
#     topks = getTopk(embedding, k)
#     seed_pair_list_uni = set()
#     seed_pair_list = set()
#     for i in range(sub_len):
#         for j in range(k):
#             pair = (i, topks[i][j])
#             if i < topks[i][j]:
#                 pair_uni = (i, topks[i][j])
#             else:
#                 pair_uni = (topks[i][j], i)
#             seed_pair_list.add(pair)
#             seed_pair_list_uni.add(pair_uni)
# 
#         for sub in range(i + 1, sub_len):
#             seed_pair = (i, sub)
# 
#     res_set = set()
#     for t in seed_pair_list:
#         a, b = t
#         target = (b, a)
#         if target in seed_pair_list:
#             if a < b:
#                 res_set.add(t)
# 
#     seed_pair_both = sorted(list(res_set))
#     seed_pair_list = sorted(list(seed_pair_list))
#     seed_pair_list_uni = sorted(list(seed_pair_list_uni))
# 
#     return seed_pair_both, seed_pair_list_uni
# 
# def get_seed_pair_list(embedding, k):
#     sub_len = len(embedding)
#     topks = getTopk(embedding, k)
#     seed_pair_list_uni = set()
#     seed_pair_list = set()
#     for i in range(sub_len):
#         for j in range(k):
#             pair = (i, topks[i][j])
#             if i < topks[i][j]:
#                 pair_uni = (i, topks[i][j])
#             else:
#                 pair_uni = (topks[i][j], i)
#             seed_pair_list.add(pair)
#             seed_pair_list_uni.add(pair_uni)
# 
#         for sub in range(i + 1, sub_len):
#             seed_pair = (i, sub)
# 
#     seed_pair_list = sorted(list(seed_pair_list))
#     seed_pair_list_uni = sorted(list(seed_pair_list_uni))
# 
#     return seed_pair_list, seed_pair_list_uni
# 
# class Embeddings(object):
#     def __init__(self, params, side_info, true_ent2clust, true_clust2ent, sub_uni2triple_dict=None, triple_list=None):
#         self.p = params
#         self.side_info = side_info
#         self.true_ent2clust, self.true_clust2ent = true_ent2clust, true_clust2ent
#         self.sub_uni2triple_dict = sub_uni2triple_dict
#         self.triples_list = triple_list
#         self.bert_model = None
#         # self.iter = 0
#         self.threshold = 0.5
#         # 修正：显式初始化这些属性，防止在 run_test 中引用报错
#         self.clust_bert_embedding = None
#         self.entity_embedding = None
#         self.new_trp_List = []
# 
#     def get_tri_assignments(self, cluster_list):
#         """辅助函数：将聚类列表转换为扁平的ID分配数组，用于计算ARI"""
#         assignments = [0] * len(self.side_info.trpIds)
#         for idx, trp_id_list in enumerate(cluster_list):
#             for tid in trp_id_list:
#                 assignments[tid] = idx
#         return assignments
# 
#     # def test_sec(self):
#     #     """阶段二：整合了 obj_seq/rel_seq 构建、TransE 初始化及动态合并逻辑"""
#     # 
#     #     self.iter = 6
#     #     print(f"\n>>> [Stage 2] 开始动态合并测试 (基准 iter: {self.iter})")
#     # 
#     #     self.bert_model = Bert_Model(self.p, self.side_info)
#     #     self.bert_model.load_state(self.iter - 1)
#     # 
#     #     folder1 = 'multi_view/context_view_' + str(self.iter)
#     #     print('folder:', folder1)
#     #     folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/'
#     #     if not os.path.exists(folder_to_make):
#     #         os.makedirs(folder_to_make)
#     #     folder2 = 'multi_view/semantic_view_' + str(self.iter)
#     #     folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
#     #     if not os.path.exists(folder_to_make):
#     #         os.makedirs(folder_to_make)
#     #     print('self.p.input:', self.p.input)
#     # 
#     #     fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cls_seq_embed' + str(
#     #         self.threshold)
#     #     fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_triple_List' + str(
#     #         self.threshold)
#     #     fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cluster_seq' + str(
#     #         self.threshold)
#     #     fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res' + str(
#     #         self.threshold)
#     #     fname5 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ambi_name2triple_id' + str(
#     #         self.threshold)
#     #     fname6 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq' + str(
#     #         self.threshold)
#     #     fname7 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq' + str(
#     #         self.threshold)
#     #     fname8 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq_embedding' + str(
#     #         self.threshold)
#     #     fname9 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq_embedding' + str(
#     #         self.threshold)
#     #     fname10 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_sub_list' + str(
#     #         self.threshold)
#     #     fname11 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_ent_list' + str(
#     #         self.threshold)
#     #     fname12 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res_sub' + str(
#     #         self.threshold)
#     # 
#     #     self.cluster_res_sub = pickle.load(open(fname12, 'rb'))
#     #     self.cluster_res = pickle.load(open(fname4, 'rb'))
#     #     self.new_sub_list = pickle.load(open(fname10, 'rb'))
#     #     self.ambi_name2triple_id = pickle.load(open(fname5, 'rb'))
#     #     self.new_trp_List = pickle.load(open(fname2, 'rb'))
#     #     self.cluster_first_stage_res = [0 for i in range(len(self.side_info.trpIds))]
#     #     name_cls_seq_embed = pickle.load(open(fname1, 'rb'))
#     #     self.clust_bert_embedding = numpy.array(
#     #         [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)
#     #     # cluster_result(self.p, self.side_info, self.clust_bert_embedding, None,
#     #     #                ('k', 2050),
#     #     #                self.true_ent2clust,
#     #     #                self.true_clust2ent, self.ambi_name2triple_id, mode='name-seq')
#     #     for i, trp_id in enumerate(self.cluster_res):
#     #         for id in trp_id:
#     #             self.cluster_first_stage_res[id] = i
#     #     # first stage cluster result
#     #     # cluster_test_triple(self.p, self.side_info, self.cluster_first_stage_res, self.true_ent2clust,
#     #     #                     self.true_clust2ent,
#     #     #                     print_or_not=True)
#     #     name_cluster_seq_embed = pickle.load(open(fname3, 'rb'))
#     #     self.clust_bert_embedding = pickle.load(open(fname1, 'rb'))
#     # 
#     # 
#     # 
#     # 
#     # 
#     # 
#     # 
#     # 
#     # 
#     # 
#     #     self.cls_param = ('k', 4050)
#     # 
#     #     # 1. 基础环境准备
#     #     folder2 = 'multi_view/semantic_view_' + str(self.iter)
#     #     folder_path = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
#     #     if not os.path.exists(folder_path): os.makedirs(folder_path)
#     # 
#     #     # 加载初始聚类嵌入 (从第一阶段最后的输出加载)
#     #     fname_base_embed = folder_path + 'name_cls_seq_embed' + str(self.threshold)
#     #     if os.path.exists(fname_base_embed):
#     #         name_cls_seq_embed = pickle.load(open(fname_base_embed, 'rb'))
#     #         self.clust_bert_embedding = np.array(
#     #             [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)
#     # 
#     #     # 2. 构建 obj_seq, rel_seq (处理非 Subject 实体)
#     #     fname_obj_emb = folder_path + 'obj_seq_embedding' + str(self.threshold)
#     #     fname_ent_list = folder_path + 'new_ent_list' + str(self.threshold)
#     #     fname_rel_emb = folder_path + 'rel_seq_embedding' + str(self.threshold)
#     #     if not os.path.exists(fname_obj_emb) or not os.path.exists(fname_rel_emb):
#     #         print("正在构建对象/关系序列...")
#     #         self.obj_seq, self.rel_seq = {}, {}
#     #         new_obj_list = []
#     #         for name in self.side_info.obj_list:
#     #             if name not in self.side_info.sub_list:
#     #                 tids = self.side_info.ent2triple_id_list[name]
#     #                 val_list = [name]
#     #                 for tid in tids: val_list.extend(['[TRI]', self.side_info.triple_List[tid]])
#     #                 self.obj_seq[name] = ' '.join((' '.join(val_list)).split()[0:512])
#     #                 new_obj_list.append(name)
#     # 
#     #         self.obj_seq_embedding = self.bert_model.encode_list(list(self.obj_seq.values()))
#     #         self.new_ent_List = self.new_sub_list + new_obj_list
#     #         pickle.dump(self.obj_seq_embedding, open(fname_obj_emb, 'wb'))
#     #         pickle.dump(self.new_ent_List, open(fname_ent_list, 'wb'))
#     # 
#     #         for rel in self.side_info.rel_list:
#     #             obj_triple_id_list = self.side_info.rel2triple_id_list[rel]
#     #             val_list = []
#     #             val_list.append(rel)
#     #             for id in obj_triple_id_list:
#     #                 sub_id, rel_id, obj_id = self.side_info.trpIds[id]
#     #                 sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
#     #                                 self.side_info.ent_list[obj_id]
#     #                 val_list.append('[TRI]')
#     #                 val_list.append(self.side_info.triple_List[id])
#     # 
#     #             self.rel_seq[rel] = ' '.join((' '.join(val_list)).split()[0:512])
#     #         self.rel_seq_embedding = self.bert_model.encode_list(list(self.rel_seq.values()))
#     #         pickle.dump(self.rel_seq_embedding, open(fname_rel_emb, 'wb'))
#     # 
#     #     else:
#     #         self.obj_seq_embedding = pickle.load(open(fname_obj_emb, 'rb'))
#     #         self.new_ent_List = pickle.load(open(fname_ent_list, 'rb'))
#     #         self.rel_seq_embedding = pickle.load(open(fname_rel_emb, 'rb'))
#     # 
#     #     # 3. 初始化 TransE 及 crawl_ent_list
#     #     self.crawl_ent_list = []
#     #     for cls in self.cluster_res:
#     #         if cls:
#     #             trp_id = self.side_info.trpIds[cls[0]]
#     #             self.crawl_ent_list.append(self.side_info.ent_list[trp_id[0]])
#     #     self.crawl_ent_list += self.new_ent_List[len(self.cluster_res):]
#     # 
#     #     model_w2v = gensim.models.KeyedVectors.load_word2vec_format(self.p.embed_loc, binary=False)
#     #     clean_rel_list = [rel.split('|')[0] for rel in self.side_info.rel_list]
#     #     E_init = getEmbeddings(model_w2v, self.crawl_ent_list, self.p.embed_dims)
#     #     R_init = getEmbeddings(model_w2v, clean_rel_list, self.p.embed_dims)
#     #     self.R_init = R_init
#     # 
#     #     # 定义嵌入训练模型
#     #     TEM = Train_Embedding_Model(self.p, self.side_info, E_init, R_init)
#     # 
#     #     # 初始 TransE 训练
#     #     new_trpIds = []
#     #     for trp in self.new_trp_List:
#     #         if trp[0] in self.new_sub_list and trp[2] in self.new_ent_List:
#     #             new_trpIds.append((self.new_sub_list.index(trp[0]),
#     #                                self.side_info.rel_list.index(trp[1]),
#     #                                self.new_ent_List.index(trp[2])))
#     #     self.entity_embedding, self.relation_embedding = TEM.train(new_trpIds, self.crawl_ent_list)
#     #     self.name_seq_embedding = self.entity_embedding[0:len(self.cluster_res)]
#     #     # cluster_result(self.p, self.side_info, self.name_seq_embedding, None,
#     #     #                self.cls_param, self.true_ent2clust,
#     #     #                self.true_clust2ent, self.cluster_res, mode='crawl')
#     # 
#     #     self.ent_embedding_unity = np.concatenate(
#     #         (np.array(self.clust_bert_embedding), self.name_seq_embedding),
#     #         axis=1)
#     #     cluster_result(self.p, self.side_info, self.ent_embedding_unity, None,
#     #                    self.cls_param, self.true_ent2clust,
#     #                    self.true_clust2ent, self.cluster_res, mode='unity')
#     #     # 4. 动态合并循环
#     #     current_cluster_res = [list(c) for c in self.cluster_res]
#     #     current_cluster_res_sub = [list(c) for c in self.cluster_res_sub]
#     #     current_clust_bert_embedding = self.clust_bert_embedding
#     #     current_name_seq_embedding = self.entity_embedding[0:len(self.cluster_res)]
#     #     current_crawl_ent_list = list(self.crawl_ent_list)
#     # 
#     #     last_triple_res = [0] * len(self.side_info.trpIds)
#     #     for i, trp_group in enumerate(current_cluster_res_sub):
#     #         for tid in trp_group:
#     #             last_triple_res[tid] = i
#     # 
#     #     current_k = 1
#     #     num_dynamic_merges = 10
#     # 
#     #     for r in range(num_dynamic_merges):
#     #         print(f"\n===== 动态合并轮次 {r + 1} (k={current_k}) =====")
#     # 
#     #         # --- (A) 获取种子 ---
#     #         # rel_seed, _ = get_seed_pair_list(current_name_seq_embedding, current_k)
#     #         # sem_seed, _ = get_seed_pair_list(current_clust_bert_embedding, current_k)
#     #         _, rel_seed = get_seed_pair_list(current_name_seq_embedding, current_k)
#     #         _, sem_seed = get_seed_pair_list(current_clust_bert_embedding, current_k)
#     #         intersection_seed = list(set(rel_seed).intersection(set(sem_seed)))[::2]
#     # 
#     #         print("intersection_seed len", len(intersection_seed))
#     #         # --- (B) 执行合并 ---
#     #         merge_cls_res, cls_m = merge_cls(intersection_seed, current_cluster_res)
#     #         merge_cls_res_sub, _ = merge_cls(intersection_seed, current_cluster_res_sub)
#     # 
#     #         current_cluster_res = merge_cls_res
#     #         current_cluster_res_sub = merge_cls_res_sub
#     # 
#     #         # --- (C) 更新 BERT 嵌入 ---
#     #         merge_seqs = []
#     #         for i in range(len(current_cluster_res)):
#     #             tmp = []
#     #             if current_cluster_res[i]:
#     #                 for old_idx in cls_m[i]:
#     #                     tmp.append(current_crawl_ent_list[old_idx])
#     #                     tmp.append('[TRI]')
#     #                     for tid in current_cluster_res[i]:
#     #                         tmp.append(self.side_info.triple_List[tid])
#     #                         tmp.append('[TRI]')
#     #                 merge_seqs.append(' '.join((' '.join(tmp)).split()))
#     # 
#     #         if merge_seqs:
#     #             current_clust_bert_embedding = self.bert_model.encode_list(merge_seqs)
#     # 
#     #         # --- (D) 更新 TransE 嵌入 ---
#     #         merge_crawl_ent_list = []
#     #         for cls in current_cluster_res:
#     #             if cls:
#     #                 trp = self.side_info.trpIds[cls[0]]
#     #                 sub = self.side_info.ent_list[trp[0]]
#     #                 merge_crawl_ent_list.append(sub)
#     # 
#     #         merge_crawl_ent_list += self.new_ent_List[len(self.cluster_res):]
#     #         current_crawl_ent_list = merge_crawl_ent_list
#     # 
#     #         idx_1_map = collections.defaultdict(list)
#     #         idx_2_map = collections.defaultdict(list)
#     # 
#     #         for cls_idx, trp_list in enumerate(current_cluster_res_sub):
#     #             for tid in trp_list: idx_1_map[tid].append(cls_idx)
#     # 
#     #         for cls_idx, trp_list in enumerate(current_cluster_res):
#     #             for tid in trp_list: idx_2_map[tid].append(cls_idx)
#     # 
#     #         merge_trpIds = [[0, 0, 0] for _ in range(len(self.side_info.trpIds))]
#     # 
#     #         for i in range(len(self.side_info.trpIds)):
#     #             trp = self.side_info.trpIds[i]
#     #             merge_trpIds[i][1] = trp[1]
#     # 
#     #             idx_1 = idx_1_map[i]
#     #             if idx_1: merge_trpIds[i][0] = idx_1[0]
#     # 
#     #             idx_2 = idx_2_map[i]
#     #             idx_pure_obj = list(set(idx_2) - set(idx_1))
#     # 
#     #             if idx_pure_obj:
#     #                 merge_trpIds[i][2] = idx_pure_obj[0]
#     #             else:
#     #                 obj_name = self.side_info.ent_list[trp[2]]
#     #                 if obj_name in merge_crawl_ent_list:
#     #                     merge_trpIds[i][2] = merge_crawl_ent_list.index(obj_name)
#     # 
#     #         merge_trpIds = [tuple(t) for t in merge_trpIds]
#     # 
#     #         merge_E_init = getEmbeddings(model_w2v, merge_crawl_ent_list, self.p.embed_dims)
#     # 
#     #         print(f'第{r + 1}次训练TransE嵌入...')
#     #         merge_TEM = Train_Embedding_Model(self.p, self.side_info, merge_E_init, self.R_init)
#     # 
#     #         self.entity_embedding, self.relation_embedding = merge_TEM.train(merge_trpIds, merge_crawl_ent_list)
#     #         current_name_seq_embedding = self.entity_embedding[0:len(current_cluster_res)]
#     # 
#     #         # =========================================================
#     #         # --- (E) 评估与 cluster_result 调用  ---
#     #         # =========================================================
#     # 
#     #         # 1. 拼接 BERT 和 TransE 嵌入
#     #         self.ent_embedding_unity = np.concatenate(
#     #             (np.array(current_clust_bert_embedding), current_name_seq_embedding),
#     #             axis=1)
#     # 
#     #         # 2. 调用 cluster_result 进行测试
#     #         print('name-seq')
#     #         if np.array_equal(np.array(current_clust_bert_embedding), current_name_seq_embedding):
#     #             print('................................................................')
#     # 
#     #         # 测试 BERT 嵌入
#     #         cluster_result(
#     #             self.p,
#     #             self.side_info,
#     #             current_clust_bert_embedding,
#     #             None,
#     #             ('k', 4050),
#     #             self.true_ent2clust,
#     #             self.true_clust2ent,
#     #             current_cluster_res_sub,
#     #             mode='name-seq'
#     #         )
#     # 
#     #         # 测试 TransE 嵌入
#     #         print('TransE')
#     #         cluster_result(
#     #             self.p,
#     #             self.side_info,
#     #             current_name_seq_embedding,
#     #             None,
#     #             ('k', 4050),
#     #             self.true_ent2clust,
#     #             self.true_clust2ent,
#     #             current_cluster_res_sub,
#     #             mode='crawl'
#     #         )
#     # 
#     #         # 测试 联合 嵌入
#     #         print('Unity')  # test_a 实际上这里没打印 'Unity'，但紧接着调用了 unity 模式
#     #         cluster_result(
#     #             self.p,
#     #             self.side_info,
#     #             self.ent_embedding_unity,
#     #             None,
#     #             ('k', 4050),
#     #             self.true_ent2clust,
#     #             self.true_clust2ent,
#     #             current_cluster_res_sub,
#     #             mode='unity'
#     #         )
#     # 
#     #         # 3. 计算 ARI 并更新 k
#     #         current_triple_res = [0] * len(self.side_info.trpIds)
#     #         for i, trp_group in enumerate(current_cluster_res_sub):
#     #             for tid in trp_group:
#     #                 current_triple_res[tid] = i
#     # 
#     #         current_ari_val = adjusted_rand_score(last_triple_res, current_triple_res)
#     #         if r > 0:
#     #             change_rate = abs(current_ari_val - last_ari) / (last_ari + 1e-9)
#     #             print(f"[收敛判定] 当前与上轮ARI: {current_ari_val:.4f}, 变化率: {change_rate:.2%}")
#     # 
#     #             if change_rate <= 0.001:
#     #                 print(f"!!! 阶段二收敛 (变化率 < 1%)，停止于 iter = {r}")
#     #                 break
#     #             last_ari = current_ari_val
#     #         else:
#     #             # 兼容 r=0 时的初始化
#     #             last_ari = current_ari_val
#     # 
#     #         # test_a 原有输出与 K 更新
#     #         print(f"ARI.{current_ari_val:.4f}:")
#     # 
#     #         ari_adj = current_ari_val - 1e-3
#     #         delta_k = math.floor(-math.log10(1 - ari_adj if ari_adj < 1.0 else 0.9999))
#     #         print('delta_k', delta_k)
#     #         current_k += delta_k
#     # 
#     #         last_triple_res = list(current_triple_res)
#     
#     def test(self):
#         self.threshold = 0.5
#         self.iter = 6
#         self.bert_model = Bert_Model(self.p, self.side_info)
#         self.bert_model.load_state(self.iter - 1)
# 
#         folder1 = 'multi_view/context_view_' + str(self.iter)
#         print('folder:', folder1)
#         folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/'
#         if not os.path.exists(folder_to_make):
#             os.makedirs(folder_to_make)
#         folder2 = 'multi_view/semantic_view_' + str(self.iter)
#         folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
#         if not os.path.exists(folder_to_make):
#             os.makedirs(folder_to_make)
#         print('self.p.input:', self.p.input)
# 
#         fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cls_seq_embed' + str(
#             self.threshold)
#         fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_triple_List' + str(
#             self.threshold)
#         fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cluster_seq' + str(
#             self.threshold)
#         fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res' + str(
#             self.threshold)
#         fname5 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ambi_name2triple_id' + str(
#             self.threshold)
#         fname6 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq' + str(
#             self.threshold)
#         fname7 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq' + str(
#             self.threshold)
#         fname8 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq_embedding' + str(
#             self.threshold)
#         fname9 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq_embedding' + str(
#             self.threshold)
#         fname10 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_sub_list' + str(
#             self.threshold)
#         fname11 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_ent_list' + str(
#             self.threshold)
#         fname12 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res_sub' + str(
#             self.threshold)
# 
#         self.cluster_res_sub = pickle.load(open(fname12, 'rb'))
#         self.cluster_res = pickle.load(open(fname4, 'rb'))
#         self.side_info.new_sub_list = pickle.load(open(fname10, 'rb'))
#         self.ambi_name2triple_id = pickle.load(open(fname5, 'rb'))
#         self.new_trp_List = pickle.load(open(fname2, 'rb'))
#         self.cluster_first_stage_res = [0 for i in range(len(self.side_info.trpIds))]
#         name_cls_seq_embed = pickle.load(open(fname1, 'rb'))
#         self.clust_bert_embedding = numpy.array(
#             [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)
#         # cluster_result(self.p, self.side_info, self.clust_bert_embedding, None,
#         #                ('k', 4050),
#         #                self.true_ent2clust,
#         #                self.true_clust2ent, self.ambi_name2triple_id, mode='name-seq')
#         for i, trp_id in enumerate(self.cluster_res):
#             for id in trp_id:
#                 self.cluster_first_stage_res[id] = i
#         # first stage cluster result
#         # cluster_test_triple(self.p, self.side_info, self.cluster_first_stage_res, self.true_ent2clust,
#         #                     self.true_clust2ent,
#         #                     print_or_not=True)
#         name_cluster_seq_embed = pickle.load(open(fname3, 'rb'))
# 
#         # self.cluster_bert_embedding = numpy.array(
#         #     [sub_v for v in name_cluster_seq_embed.values() for sub_v in v.values()]).squeeze(1)
# 
#         # self.clust_bert_embedding = pickle.load(open(fname1, 'rb'))
#         self.cls_param = ('k', 4050)
#         # self.cls_param = ('k', 2050)
# 
#         val = sum(len(v) for v in self.side_info.ent2triple_id_list.values())
#         if not checkFile(fname6) or not checkFile(fname9) or not checkFile(fname11):
#             self.obj_seq, self.rel_seq = {}, {}
#             self.new_obj_list = []
#             for name in self.side_info.obj_list:
#                 if name not in self.side_info.sub_list:
#                     obj_triple_id_list = self.side_info.ent2triple_id_list[name]
#                     val_list = []
#                     val_list.append(name)
#                     for id in obj_triple_id_list:
#                         sub_id, rel_id, obj_id = self.side_info.trpIds[id]
#                         sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
#                                         self.side_info.ent_list[obj_id]
#                         val_list.append('[TRI]')
#                         val_list.append(self.side_info.triple_List[id])
# 
#                     self.obj_seq[name] = ' '.join((' '.join(val_list)).split()[0:512])
#                     self.new_obj_list.append(name)
#             pickle.dump(self.obj_seq, open(fname6, 'wb'))
#             self.obj_seq_embedding = self.bert_model.encode_list(list(self.obj_seq.values()))
#             pickle.dump(self.obj_seq_embedding, open(fname9, 'wb'))
# 
#             self.new_ent_List = self.side_info.new_sub_list + self.new_obj_list
#             pickle.dump(self.new_ent_List, open(fname11, 'wb'))
# 
#             for rel in self.side_info.rel_list:
#                 obj_triple_id_list = self.side_info.rel2triple_id_list[rel]
#                 val_list = []
#                 val_list.append(rel)
#                 for id in obj_triple_id_list:
#                     sub_id, rel_id, obj_id = self.side_info.trpIds[id]
#                     sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
#                                     self.side_info.ent_list[obj_id]
#                     val_list.append('[TRI]')
#                     val_list.append(self.side_info.triple_List[id])
# 
#                 self.rel_seq[rel] = ' '.join((' '.join(val_list)).split()[0:512])
#             pickle.dump(self.rel_seq, open(fname7, 'wb'))
#             self.rel_seq_embedding = self.bert_model.encode_list(list(self.rel_seq.values()))
#             pickle.dump(self.rel_seq_embedding, open(fname8, 'wb'))
# 
#         else:
#             self.obj_seq_embedding = pickle.load(open(fname9, 'rb'))
#             self.rel_seq_embedding = pickle.load(open(fname8, 'rb'))
#             self.new_ent_List = pickle.load(open(fname11, 'rb'))
# 
#         print()
#         # whitening
# 
#         self.ent_seq_embedding = np.concatenate([self.clust_bert_embedding, self.obj_seq_embedding], axis=0)
#         self.new_trpIds = []
# 
#         for trp in self.new_trp_List:
#             if trp[0] in self.side_info.new_sub_list and trp[2] in self.new_ent_List:
#                 trpid = (self.side_info.new_sub_list.index(trp[0]), self.side_info.rel_list.index(trp[1]),
#                          self.new_ent_List.index(trp[2]))
#                 self.new_trpIds.append(trpid)
# 
#         folder3 = 'multi_view/relation_view_' + str(self.iter)
#         print('folder:', folder3)
#         folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder3 + '/'
#         if not os.path.exists(folder_to_make):
#             os.makedirs(folder_to_make)
# 
#         clean_ent_list, clean_rel_list, clean_sub_list = [], [], []
#         self.new_trp_List = pickle.load(open(fname2, 'rb'))
#         for rel in self.side_info.rel_list: clean_rel_list.append(rel.split('|')[0])
# 
#         # print('clean_ent_list:', type(clean_ent_list), len(clean_ent_list))
#         print('clean_rel_list:', type(clean_rel_list), len(clean_rel_list))
# 
#         self.crawl_ent_list = []
#         num = 0
#         for cls in self.cluster_res:
#             if cls:
#                 num += 1
#                 trp = self.side_info.trpIds[cls[0]]
#                 sub = self.side_info.ent_list[trp[0]]
#                 self.crawl_ent_list.append(sub)
# 
#         self.crawl_ent_list += self.new_ent_List[len(self.cluster_res):]
#         ''' Intialize embeddings '''
# 
#         # model = gensim.models.KeyedVectors.load_word2vec_format(self.p.embed_loc, binary=False)
#         # self.E_init = getEmbeddings(model, self.new_ent_List, self.p.embed_dims)
#         # pickle.dump(self.E_init, open('../file/' + self.p.dataset + '_' + self.p.split  + '/1E_init_new_ent', 'wb'))
# 
#         if self.p.embed_init == 'crawl':
#             fname1, fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder3 + '/1E_init', '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder3 + '/1R_init'
#             if not checkFile(fname1) or not checkFile(fname2):
#                 print('generate pre-trained embeddings')
# 
#                 model = gensim.models.KeyedVectors.load_word2vec_format(self.p.embed_loc, binary=False)
#                 self.E_init = getEmbeddings(model, self.crawl_ent_list, self.p.embed_dims)
#                 self.R_init = getEmbeddings(model, clean_rel_list, self.p.embed_dims)
# 
#                 pickle.dump(self.E_init, open(fname1, 'wb'))
#                 pickle.dump(self.R_init, open(fname2, 'wb'))
#             else:
#                 print('load init embeddings')
#                 self.E_init = pickle.load(open(fname1, 'rb'))
#                 self.R_init = pickle.load(open(fname2, 'rb'))
# 
#         self.crawl_sub_init = self.E_init[0:len(self.cluster_res)]
#         # k_crawl = findkbydb(np.array(self.crawl_sub_init), self.p.dataset)
# 
#         # cluster_result(self.p, self.side_info, self.crawl_sub_init, None,
#         #                self.cls_param, self.true_ent2clust,
#         #                self.true_clust2ent, self.cluster_res, mode='crawl')
# 
#         if self.p.use_Embedding_model:
#             fname1, fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder3 + '/entity_embedding', '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder3 + '/relation_embedding'
#             if not checkFile(fname1) or not checkFile(fname2):
#                 print('generate TransE embeddings', fname1)
#                 entity_embedding, relation_embedding = self.E_init, self.R_init
#                 print('self.training_time', 'use pre-trained crawl embeddings ... ')
# 
#                 TEM = Train_Embedding_Model(self.p, self.side_info, entity_embedding, relation_embedding)
#                 self.entity_embedding, self.relation_embedding = TEM.train(self.new_trpIds, self.crawl_ent_list)
# 
#                 pickle.dump(self.entity_embedding, open(fname1, 'wb'))
#                 pickle.dump(self.relation_embedding, open(fname2, 'wb'))
# 
#             else:
#                 print('load TransE embeddings')
#                 self.entity_embedding = pickle.load(open(fname1, 'rb'))
#                 self.relation_embedding = pickle.load(open(fname2, 'rb'))
# 
#         self.name_seq_embedding = self.entity_embedding[0:len(self.cluster_res)]
#         # cluster_result(self.p, self.side_info, self.name_seq_embedding, None,
#                        # self.cls_param, self.true_ent2clust,
#                        # self.true_clust2ent, self.cluster_res_sub, mode='crawl')
# 
#         self.ent_embedding_unity = np.concatenate(
#             (self.clust_bert_embedding, self.name_seq_embedding),
#             axis=1)
# 
#         # cluster_result(self.p, self.side_info, self.clust_bert_embedding, None,
#         #                self.cls_param,
#         #                self.true_ent2clust,
#         #                self.true_clust2ent, self.cluster_res_sub, mode='name-seq')
#         # cluster_result(self.p, self.side_info, self.ent_embedding_unity, None,
#         #                self.cls_param, self.true_ent2clust,
#         #                self.true_clust2ent, self.cluster_res_sub, mode='unity')
# 
#         # 初始化动态合并的初始参数
#         current_cluster_res, last_cluster_res_sub, current_cluster_res_sub = [], [], []
#         # current_cluster_res_sub = self.cluster_res_sub
#         for i, cls in enumerate(self.cluster_res):
#             current_cluster_res_sub.append(self.cluster_res_sub[i])
#             last_cluster_res_sub.append(self.cluster_res_sub[i])
#             current_cluster_res.append(cls)
#         current_triple_res = [0 for j in range(len(self.side_info.trpIds))]
#         last_triple_res = [0 for j in range(len(self.side_info.trpIds))]
#         for i, trp_id in enumerate(current_cluster_res_sub):
#             if trp_id:
#                 for id in trp_id:
#                     current_triple_res[id] = i
#                     last_triple_res[id] = i
#         # 初始聚类结果
#         # self.clust_bert_embedding = np.array(self.clust_bert_embedding[i] for i, cls in enumerate(self.cluster_res_sub) if cls)
#         # self.name_seq_embedding = np.array(self.name_seq_embedding[i] for i, cls in enumerate(self.cluster_res_sub) if cls)
#         current_clust_bert_embedding = self.clust_bert_embedding  # 初始BERT嵌入
#         current_name_seq_embedding = self.name_seq_embedding  # 初始TransE嵌入
#         merge_entity_embedding, merge_relation_embedding = self.entity_embedding, self.relation_embedding
#         current_crawl_ent_list = self.crawl_ent_list
#         current_cls_num = len(self.cluster_res)
#         current_k = 1
#         # merge_TEM = Train_Embedding_Model(self.p, self.side_info, self.entity_embedding, self.relation_embedding)
#         # 动态合并，每次i均为0
#         num_dynamic_merges = 10
#         model = gensim.models.KeyedVectors.load_word2vec_format(self.p.embed_loc, binary=False)
# 
#         for merge_round in range(num_dynamic_merges):
#             print(f"\n===== 动态合并第 {merge_round + 1}/{num_dynamic_merges} 次 =====")
#             rel_seed, rel_seed_uni = get_seed_pair_list(
#                 current_name_seq_embedding,  # 当前TransE嵌入
#                 current_k  # i=0 -> i+1=1
#             )
#             sem_seed, sem_seed_uni = get_seed_pair_list(
#                 current_clust_bert_embedding,  # 当前BERT嵌入
#                 current_k  # i=0 -> i+1=1
#             )
# 
#             # 2. 计算交叉种子对
#             print(len(rel_seed_uni))
#             print(len(current_name_seq_embedding))
#             print(len(current_clust_bert_embedding))
#             print(len(sem_seed_uni))
#             intersection_seed = sorted(list(set(rel_seed_uni).intersection(set(sem_seed_uni))))
#             intersection_seed = intersection_seed[:len(intersection_seed)//2]
# 
#             # 4. 基于当前聚类结果进行合并
#             merge_cls_res, cls_m = merge_cls(intersection_seed, current_cluster_res)
#             merge_cls_res_sub, _ = merge_cls(intersection_seed, current_cluster_res_sub)
# 
#             print(f'第{merge_round + 1}次交叉种子对数量: ', len(intersection_seed))
#             merge_cls_res_acc = merge_acc(merge_cls_res, self.side_info, self.true_ent2clust)
#             print(f'第{merge_round + 1}次合并准确率: ', merge_cls_res_acc)
#             print(f'第{merge_round + 1}次合并后聚类数量: ', len(merge_cls_res))
#             print(f'第{merge_round + 1}次合并topk: ', current_k)
# 
#             intersection_seed_acc = seed_accuracy(
#                 intersection_seed,
#                 self.side_info,
#                 self.true_ent2clust,
#                 current_cluster_res  # 基于当前聚类结果评估
#             )
#             print(f'第{merge_round + 1}次交叉种子准确率: ', intersection_seed_acc)
#             current_cls_num = len(merge_cls_res)
#             # 6. 生成合并后的序列并编码为新的BERT嵌入
#             num = 0
#             merge_name_cls_seq = []
#             # merge_cls_res_sf = merge_cls_res.copy()
#             # shuffle(merge_cls_res_sf)
#             for i, cls in enumerate(merge_cls_res):
#                 val_list = []
#                 if cls:
#                     # for j in cls_m[i]:
#                     #     val_list.append(current_crawl_ent_list[j])
#                     #     val_list.append('[TRI]')
#                     # shuffle(cls)
#                     # trp = self.side_info.trpIds[cls[0]]
#                     # sub = self.side_info.ent_list[trp[0]]
#                     for id in cls:
#                         val_list.append(self.side_info.triple_List[id])
#                         val_list.append('[TRI]')
#                     cls_seq = ' '.join((' '.join(val_list)).split())
#                     merge_name_cls_seq.append(cls_seq)
#             merge_cls_seq_embed = self.bert_model.encode_list(merge_name_cls_seq)
#             current_cluster_res = merge_cls_res
#             current_cluster_res_sub = merge_cls_res_sub
#             for i, trp_id in enumerate(current_cluster_res_sub):
#                 for id in trp_id:
#                     current_triple_res[id] = i
#             current_clust_bert_embedding = merge_cls_seq_embed[0:len(merge_cls_res)]
# 
#             # 7. 更新TransE嵌入（如果启用）
#             if self.p.use_Embedding_model:
#                 # 准备合并后的实体列表用于TransE更新
#                 merge_crawl_ent_list = []
#                 for cls in merge_cls_res:
#                     if cls:  # 避免空聚类
#                         trp = self.side_info.trpIds[cls[0]]
#                         sub = self.side_info.ent_list[trp[0]]
#                         merge_crawl_ent_list.append(sub)
#                 merge_crawl_ent_list += self.new_ent_List[len(self.cluster_res):]
#                 current_crawl_ent_list = merge_crawl_ent_list
#                 merge_new_ent_list = process_duplicates(merge_crawl_ent_list)
#                 # 生成新的TransE嵌入保存路径（区分合并轮次）
#                 # folder_merge = f'multi_view/dynamic_merge_{merge_round + 1}_relation_view_{self.iter}'
#                 # folder_to_make_merge = f'../file/{self.p.dataset}_{self.p.split}/{folder_merge}/'
#                 # if not os.path.exists(folder_to_make_merge):
#                 #     os.makedirs(folder_to_make_merge)
#                 fname_merge_e = os.path.join(folder_to_make, 'entity_embedding_' + str(merge_round))
# 
#                 # 训练或加载新的TransE嵌入
#                 if not checkFile(fname_merge_e):
#                     merge_E_init = getEmbeddings(model, merge_crawl_ent_list, self.p.embed_dims)
#                     # merge_R_init = getEmbeddings(model, clean_rel_list, self.p.embed_dims)
# 
#                     print(f'第{merge_round + 1}次训练TransE嵌入...')
#                     # 生成当前合并结果对应的三元组ID
#                     num1, num2 = 0, 0
#                     merge_trpIds = [[0, 0, 0] for i in range(len(self.side_info.trpIds))]
#                     for i, trpid in enumerate(merge_trpIds):
#                         trp = self.side_info.trpIds[i]
#                         merge_trpIds[i][1] = trp[1]
#                         idx_1 = [j for j, sublist in enumerate(merge_cls_res_sub) if i in sublist]
#                         idx_2 = [j for j, sublist in enumerate(merge_cls_res) if i in sublist]
#                         idx = list(set(idx_2) - set(idx_1))
#                         merge_trpIds[i][0] = idx_1[0]
#                         obj = self.side_info.ent_list[trp[2]]
#                         if idx:
#                             merge_trpIds[i][2] = idx[0]
#                         elif obj in merge_crawl_ent_list:
#                             obj_id = merge_crawl_ent_list.index(obj)
#                             # if obj_id >= len(merge_cls_res):
#                             merge_trpIds[i][2] = obj_id
#                         # elif idx:
#                         #     merge_trpIds[i][2] = idx[0]
#                         else:
#                             num2 += 1
# 
#                     print('num2:', num2)
#                     merge_trpIds = [tuple(i) for i in merge_trpIds]
#                     merge_TEM = Train_Embedding_Model(self.p, self.side_info, merge_E_init,
#                                                         self.R_init)
#                     merge_entity_embedding, merge_relation_embedding = merge_TEM.train(merge_trpIds,
#                                                                                        merge_crawl_ent_list)
#                     pickle.dump(merge_entity_embedding, open(fname_merge_e, 'wb'))
# 
#                 else:
#                     print(f'第{merge_round + 1}次加载TransE嵌入...')
#                     merge_entity_embedding = pickle.load(open(fname_merge_e, 'rb'))
#                     
#                 current_name_seq_embedding = merge_entity_embedding[0:len(merge_cls_res)]  # 更新TransE嵌入
# 
#             # 8. 更新当前聚类结果和BERT嵌入，用于下一轮合并
# 
#             self.ent_embedding_unity = np.concatenate(
#                 (np.array(current_clust_bert_embedding), current_name_seq_embedding),
#                 axis=1)
#             print('name-seq')
#             if np.array(current_clust_bert_embedding) == current_name_seq_embedding:
#                 print('................................................................')
#             cluster_result(
#                 self.p,
#                 self.side_info,
#                 current_clust_bert_embedding,
#                 None,
#                 ('k', 4050),
#                 # 4050
#                 self.true_ent2clust,
#                 self.true_clust2ent,
#                 current_cluster_res_sub,
#                 mode='name-seq'
#             )
#             print('TransE')
#             cluster_result(
#                 self.p,
#                 self.side_info,
#                 current_name_seq_embedding,
#                 None,
#                 ('k', 4050),
#                 self.true_ent2clust,
#                 self.true_clust2ent,
#                 current_cluster_res_sub,
#                 mode='crawl'
#             )
# 
#             # 9. 评估当前合并结果
#             cluster_result(
#                 self.p,
#                 self.side_info,
#                 self.ent_embedding_unity,
#                 None,
#                 ('k', 4050),
#                 self.true_ent2clust,
#                 self.true_clust2ent,
#                 current_cluster_res_sub,
#                 mode='unity'
#             )
#             current_ari = round(adjusted_rand_score(last_triple_res, current_triple_res), 3)
#             print(str(merge_round))
#             print(f"ARI.{current_ari:.4f}:")
#             current_ari -= 1e-3
#             delta_k = math.floor(-math.log10(1 - current_ari))
#             print('delta_k', delta_k)
#             current_k += delta_k
#             last_cluster_res_sub = merge_cls_res_sub
#             last_ari = current_ari
#             for i, trp_id in enumerate(last_cluster_res_sub):
#                 for id in trp_id:
#                     last_triple_res[id] = i
# 
#             if merge_round > 0:
#                 change_rate = abs(current_ari - last_ari) / (last_ari + 1e-9)
#                 print(f"[收敛判定] 当前与上轮ARI: {current_ari:.4f}, 变化率: {change_rate:.2%}")
# 
#                 if change_rate <= 0.001:
#                     print(f"!!! 阶段二收敛 (变化率 < 1%)，停止于 iter = {merge_round}")
#                     break
#                 # last_ari = current_ari_val
# 
#     def get_seed(self, rate):
#         show_memory = False
#         if show_memory:
#             print('show_memory:', show_memory)
#             import tracemalloc
#             tracemalloc.start(25)  # 默认25个片段，这个本质还是多次采样
# 
#         clean_ent_list, clean_rel_list, clean_sub_list = [], [], []
#         for index in range(len(self.side_info.ent_list)):
#             clean_ent = self.side_info.ent_list[index].split('|')[0]
#             if clean_ent in self.side_info.sub_list:
#                 clean_sub_list.append(clean_ent)
#             clean_ent_list.append(clean_ent)
#         for rel in self.side_info.rel_list: clean_rel_list.append(rel.split('|')[0])
#         print('clean_ent_list:', type(clean_ent_list), len(clean_ent_list))
#         print('clean_rel_list:', type(clean_rel_list), len(clean_rel_list))
# 
#         folder1 = 'multi_view/context_view_' + str(self.iter)
#         print('folder:', folder1)
#         folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/'
#         if not os.path.exists(folder_to_make):
#             os.makedirs(folder_to_make)
#         folder2 = 'multi_view/semantic_view_' + str(self.iter)
#         folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
#         if not os.path.exists(folder_to_make):
#             os.makedirs(folder_to_make)
#         print('self.p.input:', self.p.input)
# 
#         self.trp_text_dict = {}
#         trp_ctxt_dict = {}
#         trp_only_ctxt_dict = {}
#         self.new_trp_List = []
#         for id in self.side_info.trpIds:
#             sub, rel, obj = self.side_info.ent_list[id[0]], self.side_info.rel_list[id[1]], self.side_info.ent_list[
#                 id[2]]
#             self.new_trp_List.append([sub, rel, obj])
#         for sub in self.side_info.sub_list:
#             self.trp_text_dict[sub] = {}
#             trp_ctxt_dict[sub] = {}
#             trp_only_ctxt_dict[sub] = {}
#             for i in self.side_info.sub2triple_id_list[sub]:
#                 id = self.side_info.trpIds[i]
#                 sub_t, rel, obj = self.side_info.sub_list[id[0]], self.side_info.rel_list[id[1]], \
#                                   self.side_info.ent_list[
#                                       id[2]]
#                 self.trp_text_dict[sub][i] = sub_t + ' ' + rel + ' ' + obj
#                 trp_only_ctxt_dict[sub][i] = self.side_info.sentence_List[i]
#                 trp_ctxt_dict[sub][i] = sub_t + ' ' + rel + ' ' + obj + '[SEP]' + self.side_info.sentence_List[i]
# 
#         # triple-view bert
#         self.ent_link_desc = pickle.load(open('../data/ent_link/name_ambi_ent_link', 'rb'))
#         if self.p.use_semantic and self.p.use_BERT:
#             fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/bert_tri_embedding'
#             fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/desc_embed_dict'
#             fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/bert_tri_ctxt_embed_dict'
#             if not checkFile(fname1):
#                 desc_embed_dict = self.bert_model.encode(self.ent_link_desc)
#                 bert_tri_embedding = self.bert_model.encode(self.trp_text_dict)
#                 bert_tri_ctxt_embed_dict = self.bert_model.encode(trp_ctxt_dict)
#                 pickle.dump(bert_tri_embedding, open(fname1, 'wb'))
#                 pickle.dump(desc_embed_dict, open(fname2, 'wb'))
#                 pickle.dump(bert_tri_ctxt_embed_dict, open(fname3, 'wb'))
#             else:
#                 print('load Bert embeddings')
#                 bert_tri_embedding = pickle.load(open(fname1, 'rb'))
#                 desc_embed_dict = pickle.load(open(fname2, 'rb'))
#                 bert_tri_ctxt_embed_dict = pickle.load(open(fname3, 'rb'))
# 
#         fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cls_seq_embed' + str(
#             self.threshold)
#         fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_triple_List' + str(
#             self.threshold)
#         fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cluster_seq' + str(
#             self.threshold)
#         fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res' + str(
#             self.threshold)
#         fname5 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ambi_name2triple_id' + str(
#             self.threshold)
#         fname6 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq' + str(
#             self.threshold)
#         fname7 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq' + str(
#             self.threshold)
#         fname8 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq_embedding' + str(
#             self.threshold)
#         fname9 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq_embedding' + str(
#             self.threshold)
#         fname10 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_sub_list' + str(
#             self.threshold)
#         fname11 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_ent_list' + str(
#             self.threshold)
#         fname12 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res_sub' + str(
#             self.threshold)
#         true_link_ratio_uni = 0
# 
#         tri_ctxt_list = [pair[1][0] for pair in sorted(
#             ((num, emb) for inner_dict in bert_tri_ctxt_embed_dict.values() for num, emb in inner_dict.items()),
#             key=lambda x: x[0]
#         )]
# 
#         if not checkFile(fname1) or not checkFile(fname5):
#             print(self.threshold)
#             self.cluster_res = []
#             self.cluster_res_sub = []
#             self.new_sub_list = []
#             self.ambi_name2triple_id = {}
#             self.name_cluster_seq = {}
#             single_num = 0
#             sub_obj_triple = 0
#             # both_ambi_trp = []
#             for name in self.side_info.sub_list:
#                 # cand_ent_embed = desc_embed_dict[name]
#                 self.name_cluster_seq[name] = {}
#                 triple_id_list = self.side_info.ent2triple_id_list[name]
#                 if len(triple_id_list) == 1:
#                     val_list = []
#                     val_list.append(name)
#                     single_num += 1
#                     triple_id = self.side_info.trpIds[triple_id_list[0]]
#                     self.cluster_res.append(triple_id_list)
#                     self.cluster_res_sub.append(triple_id_list)
#                     self.ambi_name2triple_id[name] = triple_id_list
#                     sub, rel, obj = self.side_info.ent_list[triple_id[0]], self.side_info.rel_list[triple_id[1]], \
#                                     self.side_info.ent_list[triple_id[2]]
#                     val_list.append('[TRI]')
#                     val_list.append(self.side_info.triple_List[triple_id_list[0]])
#                     self.new_sub_list.append(name)
#                     self.name_cluster_seq[name][name] = ''.join(val_list)
#                     # self.new_trp_List
#                 else:
#                     if len(list(self.ent_link_desc[name])) == 1:
#                         val_list = []
#                         val_list.append(name)
#                         self.cluster_res.append(triple_id_list)
#                         sub_cluster = [id for id in triple_id_list if id in self.side_info.sub2triple_id_list[name]]
#                         self.cluster_res_sub.append(sub_cluster)
#                         # if len(sub_cluster) > 3:
#                         #     cct_seq = concatenate_triples_all_permutations(sub_cluster, self.side_info.triple_List)
#                         self.ambi_name2triple_id[name] = triple_id_list
#                         for id in triple_id_list:
#                             sub_id, rel_id, obj_id = self.side_info.trpIds[id]
#                             sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
#                                             self.side_info.ent_list[obj_id]
#                             val_list.append('[TRI]')
#                             val_list.append(self.side_info.triple_List[id])
#                             if name == sub:
#                                 self.new_trp_List[id][0] = name
#                                 if name == obj:
#                                     self.new_trp_List[id][2] = name
#                                     sub_obj_triple += 1
#                             elif name == obj:
#                                 self.new_trp_List[id][2] = name
#                         self.new_sub_list.append(name)
#                         self.name_cluster_seq[name][name] = ' '.join(
#                             (' '.join(val_list)).split()[0:512])
# 
#                     else:
#                         # triple_list = []
#                         # for id in triple_id_list:
#                         #     triple_list.append(self.side_info.triple_List[id])
#                         name_tri_embed_list = [tri_ctxt_list[id] for id in triple_id_list]
#                         # name_tri_embed_list = [tri_ctxt_list[id] for id in triple_id_list]
#                         cluster_predict = cluster_result(self.p, self.side_info, name_tri_embed_list, None,
#                                                          ('threshold', self.threshold),
#                                                          self.true_ent2clust,
#                                                          self.true_clust2ent, None, mode='name-single')
#                         # name cluster result
#                         clusters = [[] for i in range(max(cluster_predict) + 1)]
#                         for i in range(len(cluster_predict)):
#                             clusters[cluster_predict[i]].append(triple_id_list[i])
#                         # sequence
#                         for i, cluster in enumerate(clusters):
#                             val_list = []
#                             val_list.append(name)
#                             self.cluster_res.append(cluster)
#                             sub_cluster = [id for id in cluster if id in self.side_info.sub2triple_id_list[name]]
#                             self.cluster_res_sub.append(sub_cluster)
#                             # if len(sub_cluster) > 3:
#                             #     cct_seq = concatenate_triples_all_permutations(sub_cluster, self.side_info.triple_List)
#                             self.ambi_name2triple_id[name + "  " + str(i)] = cluster
#                             for id in cluster:
#                                 sub_id, rel_id, obj_id = self.side_info.trpIds[id]
#                                 sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
#                                                 self.side_info.ent_list[obj_id]
#                                 val_list.append('[TRI]')
#                                 val_list.append(self.side_info.triple_List[id])
#                                 if name == sub:
#                                     self.new_trp_List[id][0] = name + "  " + str(i)
#                                     if name == obj:
#                                         self.new_trp_List[id][2] = name + "  " + str(i)
#                                         sub_obj_triple += 1
#                                 elif name == obj:
#                                     self.new_trp_List[id][2] = name + "  " + str(i)
#                             self.new_sub_list.append(name + "  " + str(i))
#                             self.name_cluster_seq[name][name + "  " + str(i)] = ' '.join(
#                                 (' '.join(val_list)).split()[0:512])
# 
#             print(single_num, sub_obj_triple)
#             pickle.dump(self.new_trp_List, open(fname2, 'wb'))
#             pickle.dump(self.name_cluster_seq, open(fname3, 'wb'))
#             pickle.dump(self.cluster_res, open(fname4, 'wb'))
#             pickle.dump(self.cluster_res_sub, open(fname12, 'wb'))
#             pickle.dump(self.ambi_name2triple_id, open(fname5, 'wb'))
# 
#             # name cluster seq bert
#             name_cls_seq_embed = self.bert_model.encode(self.name_cluster_seq)
#             pickle.dump(name_cls_seq_embed, open(fname1, 'wb'))
#             # new sub list
#             pickle.dump(self.new_sub_list, open(fname10, 'wb'))
# 
#         else:
#             print('load cluster Bert embeddings')
#             name_cls_seq_embed = pickle.load(open(fname1, 'rb'))
#             print('load new triple List')
#             self.new_trp_List = pickle.load(open(fname2, 'rb'))
#             print('load name cluster seq')
#             self.name_cluster_seq = pickle.load(open(fname3, 'rb'))
#             print('load name cluster result')
#             self.cluster_res = pickle.load(open(fname4, 'rb'))
# 
#             self.cluster_res_sub = pickle.load(open(fname12, 'rb'))
#             print('load ambi name2triple id')
#             self.ambi_name2triple_id = pickle.load(open(fname5, 'rb'))
#             print('load new sub_list')
#             self.new_sub_list = pickle.load(open(fname10, 'rb'))
#             print()
# 
#         self.cluster_first_stage_res = [0 for i in range(len(self.side_info.trpIds))]
#         for i, trp_id in enumerate(self.cluster_res):
#             for id in trp_id:
#                 self.cluster_first_stage_res[id] = i
#         # first stage cluster result
#         cluster_test_triple(self.p, self.side_info, self.cluster_first_stage_res, self.true_ent2clust,
#                             self.true_clust2ent,
#                             print_or_not=True)
# 
#         cluster_bert_embedding = numpy.array(
#             [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)
#         # cluster_result(self.p, self.side_info, cluster_bert_embedding, None,
#         #                ('k', len(self.true_clust2ent)),
#         #                self.true_ent2clust,
#         #                self.true_clust2ent, self.ambi_name2triple_id, mode='name-seq')
#         print('----------------------------------------')
# 
#         fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cls_link_res' + str(
#             self.threshold)
#         fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/tri_link_res' + str(
#             self.threshold)
#         fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ctxt_link_res' + str(
#             self.threshold)
#         fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/self.tri_link_res_kl' + str(
#             self.threshold)
# 
#         if not checkFile(fname3):
#             cls_link_res = get_sims_dict(name_cls_seq_embed, desc_embed_dict)
#             self.tri_link_res = get_sims_dict(bert_tri_embedding, desc_embed_dict)
#             self.ctxt_link_res = get_sims_dict(bert_tri_ctxt_embed_dict, desc_embed_dict)
#             pickle.dump(cls_link_res, open(fname1, 'wb'))
#             pickle.dump(self.tri_link_res, open(fname2, 'wb'))
#             pickle.dump(self.ctxt_link_res, open(fname3, 'wb'))
#         else:
#             cls_link_res = pickle.load(open(fname1, 'rb'))
#             self.tri_link_res = pickle.load(open(fname2, 'rb'))
#             self.ctxt_link_res = pickle.load(open(fname3, 'rb'))
# 
#         num = sum(len(i) for i in self.cluster_res_sub)
#         tri_cand_ent_num, most_occ_half_num, cls_len_num, only_one_cand_num, cls_num = 0, 0, 0, 0, 0
#         high_conf_cls = dict()
#         for k, v in cls_link_res.items():
#             high_conf_cls[k] = v
#         high_conf_trient, high_conf_npent = [], set()
#         high_conf_np = set()
# 
#         cls_link_conf = {}
#         for k, v in cls_link_res.items():
#             if len(v) > 1:
#                 cls_link_conf[k] = sigmoid((v[0][1] - v[1][1]) / v[0][1])
#             else:
#                 cls_link_conf[k] = 0.5
#         sorted_items = sorted(
#             [(k, v, idx) for idx, (k, v) in enumerate(cls_link_conf.items())],
#             key=lambda x: x[1],
#             reverse=True
#         )
# 
#         num = 0
#         filter_sorted_items = []
#         for t in sorted_items:
#             v = cls_link_res[t[0]]
#             cls_link_ent = v[0][0]
#             cls_trps = self.cluster_res_sub[t[2]]
#             if len(v) > 1:
#                 if len(cls_trps) >= 3:
#                     num += 1
#                     if get_vote_result_wrong(self.ctxt_link_res, cls_trps) == cls_link_ent:
#                         filter_sorted_items.append(t)
# 
#         # filter_cls = {item[0]}
#         final_sorted_items = filter_sorted_items[0:int(len(filter_sorted_items) * rate)]
#         for t in final_sorted_items:
#             # if occ_num < max_num:
#             v = cls_link_res[t[0]]
#             if len(v) == 0:
#                 print()
#             cls_link_ent = v[0][0]
#             cls_trps = self.cluster_res_sub[t[2]]
#             tri_link_ent = [self.ctxt_link_res[cls_trp_id][0][0] for cls_trp_id in cls_trps]
#             # tri_link_uni = set(tri_link_ent)
#             if len(cls_trps) >= 3:
#                 ent_cnt = Counter(tri_link_ent)
#                 if len(list(ent_cnt.keys())) > 3:
#                     tri_cand_ent_num += 1
#                 ratio = list(ent_cnt.values())[0] / len(tri_link_ent)
#                 if ratio > 0.5:
#                     most_occ_half_num += 1
#                 # if len(cls_trps) >= 3:
#                 if len(v) > 1:
#                     # if v[0][1] > 0.7:
#                     tri_link_ent_ = [self.ctxt_link_res[cls_trp_id] for cls_trp_id in cls_trps]
#                     for tri_link in tri_link_ent_:
#                         if len(v) != len(tri_link):
#                             print('..........................................................')
#                     # if ratio > 0.5 and len(list(ent_cnt.keys())) <= 3:
#                     # most_occ_half_num += 1
#                     # ent_cand_list = [pair[0] for pair in self.ctxt_link_res[cls_trps[0]]]
#                     if get_vote_result(self.ctxt_link_res, cls_link_ent, cls_trps) >= 0.5:
#                         # if list(ent_cnt.keys())[0] == cls_link_ent:
#                         for i in cls_trps:
#                             id = self.side_info.trpIds[i]
#                             # if self.ctxt_link_res[i][0][0] == cls_link_ent and self.ctxt_link_res[i][0][1] > 0.7:
#                             if self.ctxt_link_res[i][0][0] == cls_link_ent:
#                                 high_conf_trient.append((cls_link_ent, i))
#                                 high_conf_np.add(self.side_info.id2sub[id[0]])
#                                 high_conf_npent.add((t[0], cls_link_ent, i))
#                     else:
#                         del high_conf_cls[t[0]]
#                 else:
#                     # print(self.ent_link_desc[])
#                     only_one_cand_num += 1
#                     # if v[0][1] > 0.7:
#                     tri_link_ent = [self.ctxt_link_res[cls_trp_id][0][0] for cls_trp_id in cls_trps]
#                     ent_cnt = Counter(tri_link_ent)
#                     # print()
#                     # print(self.ent_link_desc[cls_link_ent])
#                     for i in cls_trps:
#                         # if occ_num < max_num:
#                         id = self.side_info.trpIds[i]
#                         # if self.ctxt_link_res[i][0][1] > 0.7:
#                         high_conf_trient.append((cls_link_ent, i))
#                         high_conf_np.add(self.side_info.id2sub[id[0]])
#                         high_conf_npent.add((t[0], cls_link_ent, i))
#             else:
#                 cls_len_num += 1
#                 del high_conf_cls[t[0]]
# 
#         # high_conf_npent = high_conf_npent[0:max_num]
# 
#         tri_cand_ent_num /= len(self.cluster_res)
#         most_occ_half_num /= len(self.cluster_res)
#         cls_len_num /= len(self.cluster_res)
#         only_one_cand_num /= len(self.cluster_res)
# 
#         print('candidate ent num > 3 ratio:', tri_cand_ent_num)
#         print('most occurrence link ent ratio > 0.5:', most_occ_half_num)
#         print('cls occ len < 3:', cls_len_num)
#         print('only one cand:', only_one_cand_num)
# 
#         true_link_ratio = 0
#         for trient in high_conf_trient:
#             wiki_link = self.side_info.triples[trient[1]]['subject_wiki_link']
#             if wiki_link == trient[0]:
#                 true_link_ratio += 1
#         true_link_ratio /= len(high_conf_trient)
#         true_link_ratio_uni = 0
#         for tri, ent in self.ctxt_link_res.items():
#             wiki_link = self.side_info.triples[tri]['subject_wiki_link']
#             if wiki_link == ent[0][0]:
#                 true_link_ratio_uni += 1
# 
#         true_link_ratio_uni /= len(self.ctxt_link_res)
#         print('tri link res acc:', true_link_ratio_uni)
#         print('high conf cluster num:', len(final_sorted_items))
#         print('high conf triple num:', len(high_conf_trient))
#         print('high conf np num: ', len(high_conf_np))
#         print('clusters num: ', len(self.cluster_res))
#         print('high conf link res acc: ', true_link_ratio)
#         # print(true_link_ratio_uni)
#         print()
# 
#         self.high_tri_id = [tp[1] for tp in high_conf_trient]
#         self.seed_list_cano, self.seed_list_link = [], []
#         for ent_tri in high_conf_trient:
#             np_id = self.side_info.trpIds[ent_tri[1]][0]
#             np = self.side_info.sub_list[np_id]
#             seed_pair = (np, ent_tri[0], ent_tri[1])
#             self.seed_list_link.append(seed_pair)
# 
#         self.seed_list_cano = group_by_ent(list(high_conf_npent))
#         print()
# 
#     def enhance(self):
#         tri_same_cls_id = dict()
#         for i, cls_id in enumerate(self.cluster_first_stage_res):
#             same_cls_id = self.cluster_res_sub[cls_id].copy()
#             if i in same_cls_id:
#                 same_cls_id.remove(i)
#             # same_cls_id = [id for id in same_cls_id  if id in self.high_tri_id]
#             tri_same_cls_id[i] = same_cls_id
#         self.bert_model.fine_tune(self.seed_list_cano, self.seed_list_link, self.side_info.triple_List,
#                                   self.ent_link_desc, tri_same_cls_id, self.ctxt_link_res, self.iter, self.high_tri_id)
# 
#     def fit(self, rate=0.1):
#         """阶段一：迭代微调训练。停止条件：ARI 变化率 < 1%"""
#         # print(">>> [Stage 1] 开始第一阶段微调训练")
#         # self.bert_model = Bert_Model(self.p, self.side_info)
#         #
#         # last_tri_assignments = None
#         # last_ari = 0.0
#         # max_epochs = 10
#         #
#         # for i in range(max_epochs):
#         #     self.iter = i
#         #     print(f'\n--- 训练 Epoch {i} ---')
#         #
#         #     # 运行 get_seed 更新 self.cluster_res_sub 等
#         #     self.get_seed(rate)
#         #
#         #     # 获取当前聚类分配（基于 sub 聚类）
#         #     current_tri_assignments = self.get_tri_assignments(self.cluster_res_sub)
#         #
#         #     # 计算收敛条件
#         #     if last_tri_assignments is not None and i>0:
#         #         current_ari = adjusted_rand_score(last_tri_assignments, current_tri_assignments)
#         #         change_rate = abs(current_ari - last_ari) / (last_ari + 1e-9)
#         #         print(f"[收敛判定] 当前与上轮ARI: {current_ari:.4f}, 变化率: {change_rate:.2%}")
#         #
#         #         if change_rate <= 0.01:
#         #             print(f"!!! 阶段一收敛 (变化率 < 1%)，停止于 iter = {i}")
#         #             break
#         #         last_ari = current_ari
#         #
#         #     last_tri_assignments = current_tri_assignments
#         #     self.enhance()
# 
#         # 第一阶段结束，进入第二阶段
#         self.test_sec()



















import gensim, itertools, pickle, time, numpy
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, homogeneity_completeness_v_measure
from test_performance import *
from train_embedding_model import Train_Embedding_Model, pair2triples
from model_Bert import *
from metrics import *
import os, math
import collections

def get_seed_pair_list_strict(embedding, k):
    sub_len = len(embedding)
    topks = getTopk(embedding, k)
    seed_pair_list_uni = set()
    seed_pair_list = set()
    for i in range(sub_len):
        for j in range(k):
            pair = (i, topks[i][j])
            if i < topks[i][j]:
                pair_uni = (i, topks[i][j])
            else:
                pair_uni = (topks[i][j], i)
            seed_pair_list.add(pair)
            seed_pair_list_uni.add(pair_uni)

        for sub in range(i + 1, sub_len):
            seed_pair = (i, sub)

    res_set = set()
    for t in seed_pair_list:
        a, b = t
        target = (b, a)
        if target in seed_pair_list:
            if a < b:
                res_set.add(t)

    seed_pair_both = sorted(list(res_set))
    seed_pair_list = sorted(list(seed_pair_list))
    seed_pair_list_uni = sorted(list(seed_pair_list_uni))

    return seed_pair_both, seed_pair_list_uni

def get_seed_pair_list(embedding, k):
    sub_len = len(embedding)
    topks = getTopk(embedding, k)
    seed_pair_list_uni = set()
    seed_pair_list = set()
    for i in range(sub_len):
        for j in range(k):
            pair = (i, topks[i][j])
            if i < topks[i][j]:
                pair_uni = (i, topks[i][j])
            else:
                pair_uni = (topks[i][j], i)
            seed_pair_list.add(pair)
            seed_pair_list_uni.add(pair_uni)

        for sub in range(i + 1, sub_len):
            seed_pair = (i, sub)

    seed_pair_list = sorted(list(seed_pair_list))
    seed_pair_list_uni = sorted(list(seed_pair_list_uni))

    return seed_pair_list, seed_pair_list_uni

class Embeddings(object):
    def __init__(self, params, side_info, true_ent2clust, true_clust2ent, sub_uni2triple_dict=None, triple_list=None):
        self.p = params
        self.side_info = side_info
        self.true_ent2clust, self.true_clust2ent = true_ent2clust, true_clust2ent
        self.sub_uni2triple_dict = sub_uni2triple_dict
        self.triples_list = triple_list
        self.bert_model = None
        self.iter = 0
        self.threshold = 0.5
        # 修正：显式初始化这些属性，防止在 run_test 中引用报错
        self.clust_bert_embedding = None
        self.entity_embedding = None
        self.new_trp_List = []

    def get_tri_assignments(self, cluster_list):
        """辅助函数：将聚类列表转换为扁平的ID分配数组，用于计算ARI"""
        assignments = [0] * len(self.side_info.trpIds)
        for idx, trp_id_list in enumerate(cluster_list):
            for tid in trp_id_list:
                assignments[tid] = idx
        return assignments

    def test_sec(self):
        """阶段二：整合了 obj_seq/rel_seq 构建、TransE 初始化及动态合并逻辑"""
        print(f"\n>>> [Stage 2] 开始动态合并测试 (基准 iter: {self.iter})")

        # self.threshold = 0.4
        # self.iter = 5
        # self.bert_model = Bert_Model(self.p, self.side_info)
        # self.bert_model.load_state(self.iter - 1)
        #
        # folder1 = 'multi_view/context_view_' + str(self.iter)
        # print('folder:', folder1)
        # folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/'
        # if not os.path.exists(folder_to_make):
        #     os.makedirs(folder_to_make)
        # folder2 = 'multi_view/semantic_view_' + str(self.iter)
        # folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
        # if not os.path.exists(folder_to_make):
        #     os.makedirs(folder_to_make)
        # print('self.p.input:', self.p.input)
        #
        # fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cls_seq_embed' + str(
        #     self.threshold)
        # fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_triple_List' + str(
        #     self.threshold)
        # fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cluster_seq' + str(
        #     self.threshold)
        # fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res' + str(
        #     self.threshold)
        # fname5 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ambi_name2triple_id' + str(
        #     self.threshold)
        # fname6 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq' + str(
        #     self.threshold)
        # fname7 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq' + str(
        #     self.threshold)
        # fname8 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq_embedding' + str(
        #     self.threshold)
        # fname9 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq_embedding' + str(
        #     self.threshold)
        # fname10 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_sub_list' + str(
        #     self.threshold)
        # fname11 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_ent_list' + str(
        #     self.threshold)
        # fname12 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res_sub' + str(
        #     self.threshold)
        #
        # self.cluster_res_sub = pickle.load(open(fname12, 'rb'))
        # self.cluster_res = pickle.load(open(fname4, 'rb'))
        # self.new_sub_list = pickle.load(open(fname10, 'rb'))
        # self.ambi_name2triple_id = pickle.load(open(fname5, 'rb'))
        # self.new_trp_List = pickle.load(open(fname2, 'rb'))
        # self.cluster_first_stage_res = [0 for i in range(len(self.side_info.trpIds))]
        # name_cls_seq_embed = pickle.load(open(fname1, 'rb'))
        # self.clust_bert_embedding = numpy.array(
        #     [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)
        # # cluster_result(self.p, self.side_info, self.clust_bert_embedding, None,
        # #                ('k', 2050),
        # #                self.true_ent2clust,
        # #                self.true_clust2ent, self.ambi_name2triple_id, mode='name-seq')
        # for i, trp_id in enumerate(self.cluster_res):
        #     for id in trp_id:
        #         self.cluster_first_stage_res[id] = i
        # # first stage cluster result
        # # cluster_test_triple(self.p, self.side_info, self.cluster_first_stage_res, self.true_ent2clust,
        # #                     self.true_clust2ent,
        # #                     print_or_not=True)
        # name_cluster_seq_embed = pickle.load(open(fname3, 'rb'))
        # self.clust_bert_embedding = pickle.load(open(fname1, 'rb'))










        self.cls_param = ('k', 4050)

        # 1. 基础环境准备
        folder2 = 'multi_view/semantic_view_' + str(self.iter)
        folder_path = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
        if not os.path.exists(folder_path): os.makedirs(folder_path)

        # 加载初始聚类嵌入 (从第一阶段最后的输出加载)
        fname_base_embed = folder_path + 'name_cls_seq_embed' + str(self.threshold)
        if os.path.exists(fname_base_embed):
            name_cls_seq_embed = pickle.load(open(fname_base_embed, 'rb'))
            self.clust_bert_embedding = np.array(
                [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)

        # 2. 构建 obj_seq, rel_seq (处理非 Subject 实体)
        fname_obj_emb = folder_path + 'obj_seq_embedding' + str(self.threshold)
        fname_ent_list = folder_path + 'new_ent_list' + str(self.threshold)
        fname_rel_emb = folder_path + 'rel_seq_embedding' + str(self.threshold)
        if not os.path.exists(fname_obj_emb) or not os.path.exists(fname_rel_emb):
            print("正在构建对象/关系序列...")
            self.obj_seq, self.rel_seq = {}, {}
            new_obj_list = []
            for name in self.side_info.obj_list:
                if name not in self.side_info.sub_list:
                    tids = self.side_info.ent2triple_id_list[name]
                    val_list = [name]
                    for tid in tids: val_list.extend(['[TRI]', self.side_info.triple_List[tid]])
                    self.obj_seq[name] = ' '.join((' '.join(val_list)).split()[0:512])
                    new_obj_list.append(name)

            self.obj_seq_embedding = self.bert_model.encode_list(list(self.obj_seq.values()))
            self.new_ent_List = self.new_sub_list + new_obj_list
            pickle.dump(self.obj_seq_embedding, open(fname_obj_emb, 'wb'))
            pickle.dump(self.new_ent_List, open(fname_ent_list, 'wb'))

            for rel in self.side_info.rel_list:
                obj_triple_id_list = self.side_info.rel2triple_id_list[rel]
                val_list = []
                val_list.append(rel)
                for id in obj_triple_id_list:
                    sub_id, rel_id, obj_id = self.side_info.trpIds[id]
                    sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
                                    self.side_info.ent_list[obj_id]
                    val_list.append('[TRI]')
                    val_list.append(self.side_info.triple_List[id])

                self.rel_seq[rel] = ' '.join((' '.join(val_list)).split()[0:512])
            self.rel_seq_embedding = self.bert_model.encode_list(list(self.rel_seq.values()))
            pickle.dump(self.rel_seq_embedding, open(fname_rel_emb, 'wb'))

        else:
            self.obj_seq_embedding = pickle.load(open(fname_obj_emb, 'rb'))
            self.new_ent_List = pickle.load(open(fname_ent_list, 'rb'))
            self.rel_seq_embedding = pickle.load(open(fname_rel_emb, 'rb'))

        # 3. 初始化 TransE 及 crawl_ent_list
        self.crawl_ent_list = []
        for cls in self.cluster_res:
            if cls:
                trp_id = self.side_info.trpIds[cls[0]]
                self.crawl_ent_list.append(self.side_info.ent_list[trp_id[0]])
        self.crawl_ent_list += self.new_ent_List[len(self.cluster_res):]

        model_w2v = gensim.models.KeyedVectors.load_word2vec_format(self.p.embed_loc, binary=False)
        clean_rel_list = [rel.split('|')[0] for rel in self.side_info.rel_list]
        E_init = getEmbeddings(model_w2v, self.crawl_ent_list, self.p.embed_dims)
        R_init = getEmbeddings(model_w2v, clean_rel_list, self.p.embed_dims)
        self.R_init = R_init

        # 定义嵌入训练模型
        TEM = Train_Embedding_Model(self.p, self.side_info, E_init, R_init)

        # 初始 TransE 训练
        new_trpIds = []
        for trp in self.new_trp_List:
            if trp[0] in self.new_sub_list and trp[2] in self.new_ent_List:
                new_trpIds.append((self.new_sub_list.index(trp[0]),
                                   self.side_info.rel_list.index(trp[1]),
                                   self.new_ent_List.index(trp[2])))
        self.entity_embedding, self.relation_embedding = TEM.train(new_trpIds, self.crawl_ent_list)
        self.name_seq_embedding = self.entity_embedding[0:len(self.cluster_res)]
        # cluster_result(self.p, self.side_info, self.name_seq_embedding, None,
        #                self.cls_param, self.true_ent2clust,
        #                self.true_clust2ent, self.cluster_res, mode='crawl')

        self.ent_embedding_unity = np.concatenate(
            (np.array(self.clust_bert_embedding), self.name_seq_embedding),
            axis=1)
        cluster_result(self.p, self.side_info, self.ent_embedding_unity, None,
                       self.cls_param, self.true_ent2clust,
                       self.true_clust2ent, self.cluster_res, mode='unity')
        # 4. 动态合并循环
        current_cluster_res = [list(c) for c in self.cluster_res]
        current_cluster_res_sub = [list(c) for c in self.cluster_res_sub]
        current_clust_bert_embedding = self.clust_bert_embedding
        current_name_seq_embedding = self.entity_embedding[0:len(self.cluster_res)]
        current_crawl_ent_list = list(self.crawl_ent_list)

        last_triple_res = [0] * len(self.side_info.trpIds)
        for i, trp_group in enumerate(current_cluster_res_sub):
            for tid in trp_group:
                last_triple_res[tid] = i

        current_k = 1
        num_dynamic_merges = 10

        for r in range(num_dynamic_merges):
            print(f"\n===== 动态合并轮次 {r + 1} (k={current_k}) =====")

            # --- (A) 获取种子 ---
            # rel_seed, _ = get_seed_pair_list(current_name_seq_embedding, current_k)
            # sem_seed, _ = get_seed_pair_list(current_clust_bert_embedding, current_k)
            _, rel_seed = get_seed_pair_list(current_name_seq_embedding, current_k)
            _, sem_seed = get_seed_pair_list(current_clust_bert_embedding, current_k)
            intersection_seed = list(set(rel_seed).intersection(set(sem_seed)))[::2]

            print("intersection_seed len", len(intersection_seed))
            # --- (B) 执行合并 ---
            merge_cls_res, cls_m = merge_cls(intersection_seed, current_cluster_res)
            merge_cls_res_sub, _ = merge_cls(intersection_seed, current_cluster_res_sub)

            current_cluster_res = merge_cls_res
            current_cluster_res_sub = merge_cls_res_sub

            # --- (C) 更新 BERT 嵌入 ---
            merge_seqs = []
            for i in range(len(current_cluster_res)):
                tmp = []
                if current_cluster_res[i]:
                    for old_idx in cls_m[i]:
                        tmp.append(current_crawl_ent_list[old_idx])
                        tmp.append('[TRI]')
                        for tid in current_cluster_res[i]:
                            tmp.append(self.side_info.triple_List[tid])
                            tmp.append('[TRI]')
                    merge_seqs.append(' '.join((' '.join(tmp)).split()))

            if merge_seqs:
                current_clust_bert_embedding = self.bert_model.encode_list(merge_seqs)

            # --- (D) 更新 TransE 嵌入 ---
            merge_crawl_ent_list = []
            for cls in current_cluster_res:
                if cls:
                    trp = self.side_info.trpIds[cls[0]]
                    sub = self.side_info.ent_list[trp[0]]
                    merge_crawl_ent_list.append(sub)

            merge_crawl_ent_list += self.new_ent_List[len(self.cluster_res):]
            current_crawl_ent_list = merge_crawl_ent_list

            idx_1_map = collections.defaultdict(list)
            idx_2_map = collections.defaultdict(list)

            for cls_idx, trp_list in enumerate(current_cluster_res_sub):
                for tid in trp_list: idx_1_map[tid].append(cls_idx)

            for cls_idx, trp_list in enumerate(current_cluster_res):
                for tid in trp_list: idx_2_map[tid].append(cls_idx)

            merge_trpIds = [[0, 0, 0] for _ in range(len(self.side_info.trpIds))]

            for i in range(len(self.side_info.trpIds)):
                trp = self.side_info.trpIds[i]
                merge_trpIds[i][1] = trp[1]

                idx_1 = idx_1_map[i]
                if idx_1: merge_trpIds[i][0] = idx_1[0]

                idx_2 = idx_2_map[i]
                idx_pure_obj = list(set(idx_2) - set(idx_1))

                if idx_pure_obj:
                    merge_trpIds[i][2] = idx_pure_obj[0]
                else:
                    obj_name = self.side_info.ent_list[trp[2]]
                    if obj_name in merge_crawl_ent_list:
                        merge_trpIds[i][2] = merge_crawl_ent_list.index(obj_name)

            merge_trpIds = [tuple(t) for t in merge_trpIds]

            merge_E_init = getEmbeddings(model_w2v, merge_crawl_ent_list, self.p.embed_dims)

            print(f'第{r + 1}次训练TransE嵌入...')
            merge_TEM = Train_Embedding_Model(self.p, self.side_info, merge_E_init, self.R_init)

            self.entity_embedding, self.relation_embedding = merge_TEM.train(merge_trpIds, merge_crawl_ent_list)
            current_name_seq_embedding = self.entity_embedding[0:len(current_cluster_res)]

            # =========================================================
            # --- (E) 评估与 cluster_result 调用  ---
            # =========================================================

            # 1. 拼接 BERT 和 TransE 嵌入
            self.ent_embedding_unity = np.concatenate(
                (np.array(current_clust_bert_embedding), current_name_seq_embedding),
                axis=1)

            # 2. 调用 cluster_result 进行测试
            print('name-seq')
            if np.array_equal(np.array(current_clust_bert_embedding), current_name_seq_embedding):
                print('................................................................')

            # 测试 BERT 嵌入
            cluster_result(
                self.p,
                self.side_info,
                current_clust_bert_embedding,
                None,
                ('k', 4050),
                self.true_ent2clust,
                self.true_clust2ent,
                current_cluster_res_sub,
                mode='name-seq'
            )

            # 测试 TransE 嵌入
            print('TransE')
            cluster_result(
                self.p,
                self.side_info,
                current_name_seq_embedding,
                None,
                ('k', 4050),
                self.true_ent2clust,
                self.true_clust2ent,
                current_cluster_res_sub,
                mode='crawl'
            )

            # 测试 联合 嵌入
            print('Unity')  # test_a 实际上这里没打印 'Unity'，但紧接着调用了 unity 模式
            cluster_result(
                self.p,
                self.side_info,
                self.ent_embedding_unity,
                None,
                ('k', 4050),
                self.true_ent2clust,
                self.true_clust2ent,
                current_cluster_res_sub,
                mode='unity'
            )

            # 3. 计算 ARI 并更新 k
            current_triple_res = [0] * len(self.side_info.trpIds)
            for i, trp_group in enumerate(current_cluster_res_sub):
                for tid in trp_group:
                    current_triple_res[tid] = i

            current_ari_val = adjusted_rand_score(last_triple_res, current_triple_res)
            if r > 0:
                change_rate = abs(current_ari_val - last_ari) / (last_ari + 1e-9)
                print(f"[收敛判定] 当前与上轮ARI: {current_ari_val:.4f}, 变化率: {change_rate:.2%}")

                if change_rate <= 0.001:
                    print(f"!!! 阶段二收敛 (变化率 < 1%)，停止于 iter = {r}")
                    break
                last_ari = current_ari_val
            else:
                # 兼容 r=0 时的初始化
                last_ari = current_ari_val

            # test_a 原有输出与 K 更新
            print(f"ARI.{current_ari_val:.4f}:")

            ari_adj = current_ari_val - 1e-3
            delta_k = math.floor(-math.log10(1 - ari_adj if ari_adj < 1.0 else 0.9999))
            print('delta_k', delta_k)
            current_k += delta_k

            last_triple_res = list(current_triple_res)

    def get_seed(self, rate):
        show_memory = False
        if show_memory:
            print('show_memory:', show_memory)
            import tracemalloc
            tracemalloc.start(25)  # 默认25个片段，这个本质还是多次采样

        clean_ent_list, clean_rel_list, clean_sub_list = [], [], []
        for index in range(len(self.side_info.ent_list)):
            clean_ent = self.side_info.ent_list[index].split('|')[0]
            if clean_ent in self.side_info.sub_list:
                clean_sub_list.append(clean_ent)
            clean_ent_list.append(clean_ent)
        for rel in self.side_info.rel_list: clean_rel_list.append(rel.split('|')[0])
        print('clean_ent_list:', type(clean_ent_list), len(clean_ent_list))
        print('clean_rel_list:', type(clean_rel_list), len(clean_rel_list))

        folder1 = 'multi_view/context_view_' + str(self.iter)
        print('folder:', folder1)
        folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/'
        if not os.path.exists(folder_to_make):
            os.makedirs(folder_to_make)
        folder2 = 'multi_view/semantic_view_' + str(self.iter)
        folder_to_make = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/'
        if not os.path.exists(folder_to_make):
            os.makedirs(folder_to_make)
        print('self.p.input:', self.p.input)

        self.trp_text_dict = {}
        trp_ctxt_dict = {}
        trp_only_ctxt_dict = {}
        self.new_trp_List = []
        for id in self.side_info.trpIds:
            sub, rel, obj = self.side_info.ent_list[id[0]], self.side_info.rel_list[id[1]], self.side_info.ent_list[
                id[2]]
            self.new_trp_List.append([sub, rel, obj])
        for sub in self.side_info.sub_list:
            self.trp_text_dict[sub] = {}
            trp_ctxt_dict[sub] = {}
            trp_only_ctxt_dict[sub] = {}
            for i in self.side_info.sub2triple_id_list[sub]:
                id = self.side_info.trpIds[i]
                sub_t, rel, obj = self.side_info.sub_list[id[0]], self.side_info.rel_list[id[1]], \
                                  self.side_info.ent_list[
                                      id[2]]
                self.trp_text_dict[sub][i] = sub_t + ' ' + rel + ' ' + obj
                trp_only_ctxt_dict[sub][i] = self.side_info.sentence_List[i]
                trp_ctxt_dict[sub][i] = sub_t + ' ' + rel + ' ' + obj + '[SEP]' + self.side_info.sentence_List[i]

        # triple-view bert
        self.ent_link_desc = pickle.load(open('../data/ent_link/' + self.p.dataset + '_ent_link', 'rb'))
        if self.p.use_semantic and self.p.use_BERT:
            fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/bert_tri_embedding'
            fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/desc_embed_dict'
            fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder1 + '/bert_tri_ctxt_embed_dict'
            if not checkFile(fname1):
                desc_embed_dict = self.bert_model.encode(self.ent_link_desc)
                bert_tri_embedding = self.bert_model.encode(self.trp_text_dict)
                bert_tri_ctxt_embed_dict = self.bert_model.encode(trp_ctxt_dict)
                pickle.dump(bert_tri_embedding, open(fname1, 'wb'))
                pickle.dump(desc_embed_dict, open(fname2, 'wb'))
                pickle.dump(bert_tri_ctxt_embed_dict, open(fname3, 'wb'))
            else:
                print('load Bert embeddings')
                bert_tri_embedding = pickle.load(open(fname1, 'rb'))
                desc_embed_dict = pickle.load(open(fname2, 'rb'))
                bert_tri_ctxt_embed_dict = pickle.load(open(fname3, 'rb'))

        fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cls_seq_embed' + str(
            self.threshold)
        fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_triple_List' + str(
            self.threshold)
        fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/name_cluster_seq' + str(
            self.threshold)
        fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res' + str(
            self.threshold)
        fname5 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ambi_name2triple_id' + str(
            self.threshold)
        fname6 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq' + str(
            self.threshold)
        fname7 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq' + str(
            self.threshold)
        fname8 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/rel_seq_embedding' + str(
            self.threshold)
        fname9 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/obj_seq_embedding' + str(
            self.threshold)
        fname10 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_sub_list' + str(
            self.threshold)
        fname11 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/new_ent_list' + str(
            self.threshold)
        fname12 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cluster_res_sub' + str(
            self.threshold)
        true_link_ratio_uni = 0

        tri_ctxt_list = [pair[1][0] for pair in sorted(
            ((num, emb) for inner_dict in bert_tri_ctxt_embed_dict.values() for num, emb in inner_dict.items()),
            key=lambda x: x[0]
        )]

        if not checkFile(fname1) or not checkFile(fname5):
            print(self.threshold)
            self.cluster_res = []
            self.cluster_res_sub = []
            self.new_sub_list = []
            self.ambi_name2triple_id = {}
            self.name_cluster_seq = {}
            single_num = 0
            sub_obj_triple = 0
            # both_ambi_trp = []
            for name in self.side_info.sub_list:
                # cand_ent_embed = desc_embed_dict[name]
                self.name_cluster_seq[name] = {}
                triple_id_list = self.side_info.ent2triple_id_list[name]
                if len(triple_id_list) == 1:
                    val_list = []
                    val_list.append(name)
                    single_num += 1
                    triple_id = self.side_info.trpIds[triple_id_list[0]]
                    self.cluster_res.append(triple_id_list)
                    self.cluster_res_sub.append(triple_id_list)
                    self.ambi_name2triple_id[name] = triple_id_list
                    sub, rel, obj = self.side_info.ent_list[triple_id[0]], self.side_info.rel_list[triple_id[1]], \
                                    self.side_info.ent_list[triple_id[2]]
                    val_list.append('[TRI]')
                    val_list.append(self.side_info.triple_List[triple_id_list[0]])
                    self.new_sub_list.append(name)
                    self.name_cluster_seq[name][name] = ''.join(val_list)
                    # self.new_trp_List
                else:
                    # if len(list(self.ent_link_desc[name])) == 1:
                    #     val_list = []
                    #     val_list.append(name)
                    #     self.cluster_res.append(triple_id_list)
                    #     sub_cluster = [id for id in triple_id_list if id in self.side_info.sub2triple_id_list[name]]
                    #     self.cluster_res_sub.append(sub_cluster)
                    #     # if len(sub_cluster) > 3:
                    #     #     cct_seq = concatenate_triples_all_permutations(sub_cluster, self.side_info.triple_List)
                    #     self.ambi_name2triple_id[name] = triple_id_list
                    #     for id in triple_id_list:
                    #         sub_id, rel_id, obj_id = self.side_info.trpIds[id]
                    #         sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
                    #                         self.side_info.ent_list[obj_id]
                    #         val_list.append('[TRI]')
                    #         val_list.append(self.side_info.triple_List[id])
                    #         if name == sub:
                    #             self.new_trp_List[id][0] = name
                    #             if name == obj:
                    #                 self.new_trp_List[id][2] = name
                    #                 sub_obj_triple += 1
                    #         elif name == obj:
                    #             self.new_trp_List[id][2] = name
                    #     self.new_sub_list.append(name)
                    #     self.name_cluster_seq[name][name] = ' '.join(
                    #         (' '.join(val_list)).split()[0:512])
                    #
                    # else:
                        # triple_list = []
                        # for id in triple_id_list:
                        #     triple_list.append(self.side_info.triple_List[id])
                        name_tri_embed_list = [tri_ctxt_list[id] for id in triple_id_list]
                        # name_tri_embed_list = [tri_ctxt_list[id] for id in triple_id_list]
                        cluster_predict = cluster_result(self.p, self.side_info, name_tri_embed_list, None,
                                                         ('threshold', self.threshold),
                                                         self.true_ent2clust,
                                                         self.true_clust2ent, None, mode='name-single')
                        # name cluster result
                        clusters = [[] for i in range(max(cluster_predict) + 1)]
                        for i in range(len(cluster_predict)):
                            clusters[cluster_predict[i]].append(triple_id_list[i])
                        # sequence
                        for i, cluster in enumerate(clusters):
                            val_list = []
                            val_list.append(name)
                            self.cluster_res.append(cluster)
                            sub_cluster = [id for id in cluster if id in self.side_info.sub2triple_id_list[name]]
                            self.cluster_res_sub.append(sub_cluster)
                            # if len(sub_cluster) > 3:
                            #     cct_seq = concatenate_triples_all_permutations(sub_cluster, self.side_info.triple_List)
                            self.ambi_name2triple_id[name + "  " + str(i)] = cluster
                            for id in cluster:
                                sub_id, rel_id, obj_id = self.side_info.trpIds[id]
                                sub, rel, obj = self.side_info.ent_list[sub_id], self.side_info.rel_list[rel_id], \
                                                self.side_info.ent_list[obj_id]
                                val_list.append('[TRI]')
                                val_list.append(self.side_info.triple_List[id])
                                if name == sub:
                                    self.new_trp_List[id][0] = name + "  " + str(i)
                                    if name == obj:
                                        self.new_trp_List[id][2] = name + "  " + str(i)
                                        sub_obj_triple += 1
                                elif name == obj:
                                    self.new_trp_List[id][2] = name + "  " + str(i)
                            self.new_sub_list.append(name + "  " + str(i))
                            self.name_cluster_seq[name][name + "  " + str(i)] = ' '.join(
                                (' '.join(val_list)).split()[0:512])

            print(single_num, sub_obj_triple)
            pickle.dump(self.new_trp_List, open(fname2, 'wb'))
            pickle.dump(self.name_cluster_seq, open(fname3, 'wb'))
            pickle.dump(self.cluster_res, open(fname4, 'wb'))
            pickle.dump(self.cluster_res_sub, open(fname12, 'wb'))
            pickle.dump(self.ambi_name2triple_id, open(fname5, 'wb'))

            # name cluster seq bert
            name_cls_seq_embed = self.bert_model.encode(self.name_cluster_seq)
            pickle.dump(name_cls_seq_embed, open(fname1, 'wb'))
            # new sub list
            pickle.dump(self.new_sub_list, open(fname10, 'wb'))

        else:
            print('load cluster Bert embeddings')
            name_cls_seq_embed = pickle.load(open(fname1, 'rb'))
            print('load new triple List')
            self.new_trp_List = pickle.load(open(fname2, 'rb'))
            print('load name cluster seq')
            self.name_cluster_seq = pickle.load(open(fname3, 'rb'))
            print('load name cluster result')
            self.cluster_res = pickle.load(open(fname4, 'rb'))

            self.cluster_res_sub = pickle.load(open(fname12, 'rb'))
            print('load ambi name2triple id')
            self.ambi_name2triple_id = pickle.load(open(fname5, 'rb'))
            print('load new sub_list')
            self.new_sub_list = pickle.load(open(fname10, 'rb'))
            print()

        self.cluster_first_stage_res = [0 for i in range(len(self.side_info.trpIds))]
        for i, trp_id in enumerate(self.cluster_res):
            for id in trp_id:
                self.cluster_first_stage_res[id] = i
        # first stage cluster result
        cluster_test_triple(self.p, self.side_info, self.cluster_first_stage_res, self.true_ent2clust,
                            self.true_clust2ent,
                            print_or_not=True)

        cluster_bert_embedding = numpy.array(
            [sub_v for v in name_cls_seq_embed.values() for sub_v in v.values()]).squeeze(1)
        # cluster_result(self.p, self.side_info, cluster_bert_embedding, None,
        #                ('k', len(self.true_clust2ent)),
        #                self.true_ent2clust,
        #                self.true_clust2ent, self.ambi_name2triple_id, mode='name-seq')
        print('----------------------------------------')

        fname1 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/cls_link_res' + str(
            self.threshold)
        fname2 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/tri_link_res' + str(
            self.threshold)
        fname3 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/ctxt_link_res' + str(
            self.threshold)
        fname4 = '../file/' + self.p.dataset + '_' + self.p.split + '/' + folder2 + '/self.tri_link_res_kl' + str(
            self.threshold)

        if not checkFile(fname3):
            cls_link_res = get_sims_dict(name_cls_seq_embed, desc_embed_dict)
            self.tri_link_res = get_sims_dict(bert_tri_embedding, desc_embed_dict)
            self.ctxt_link_res = get_sims_dict(bert_tri_ctxt_embed_dict, desc_embed_dict)
            pickle.dump(cls_link_res, open(fname1, 'wb'))
            pickle.dump(self.tri_link_res, open(fname2, 'wb'))
            pickle.dump(self.ctxt_link_res, open(fname3, 'wb'))
        else:
            cls_link_res = pickle.load(open(fname1, 'rb'))
            self.tri_link_res = pickle.load(open(fname2, 'rb'))
            self.ctxt_link_res = pickle.load(open(fname3, 'rb'))

        num = sum(len(i) for i in self.cluster_res_sub)
        tri_cand_ent_num, most_occ_half_num, cls_len_num, only_one_cand_num, cls_num = 0, 0, 0, 0, 0
        high_conf_cls = dict()
        for k, v in cls_link_res.items():
            high_conf_cls[k] = v
        high_conf_trient, high_conf_npent = [], set()
        high_conf_np = set()

        cls_link_conf = {}
        for k, v in cls_link_res.items():
            if len(v) > 1:
                cls_link_conf[k] = sigmoid((v[0][1] - v[1][1]) / v[0][1])
            else:
                cls_link_conf[k] = 0.5
        sorted_items = sorted(
            [(k, v, idx) for idx, (k, v) in enumerate(cls_link_conf.items())],
            key=lambda x: x[1],
            reverse=True
        )

        num = 0
        filter_sorted_items = []
        for t in sorted_items:
            v = cls_link_res[t[0]]
            cls_link_ent = v[0][0]
            cls_trps = self.cluster_res_sub[t[2]]
            if len(v) > 1:
                if len(cls_trps) >= 3:
                    num += 1
                    if get_vote_result_wrong(self.ctxt_link_res, cls_trps) == cls_link_ent:
                        filter_sorted_items.append(t)

        # filter_cls = {item[0]}
        final_sorted_items = filter_sorted_items[0:int(len(filter_sorted_items) * rate)]
        for t in final_sorted_items:
            # if occ_num < max_num:
            v = cls_link_res[t[0]]
            if len(v) == 0:
                print()
            cls_link_ent = v[0][0]
            cls_trps = self.cluster_res_sub[t[2]]
            tri_link_ent = [self.ctxt_link_res[cls_trp_id][0][0] for cls_trp_id in cls_trps]
            # tri_link_uni = set(tri_link_ent)
            if len(cls_trps) >= 3:
                ent_cnt = Counter(tri_link_ent)
                if len(list(ent_cnt.keys())) > 3:
                    tri_cand_ent_num += 1
                ratio = list(ent_cnt.values())[0] / len(tri_link_ent)
                if ratio > 0.5:
                    most_occ_half_num += 1
                # if len(cls_trps) >= 3:
                if len(v) > 1:
                    # if v[0][1] > 0.7:
                    tri_link_ent_ = [self.ctxt_link_res[cls_trp_id] for cls_trp_id in cls_trps]
                    for tri_link in tri_link_ent_:
                        if len(v) != len(tri_link):
                            print('..........................................................')
                    # if ratio > 0.5 and len(list(ent_cnt.keys())) <= 3:
                    # most_occ_half_num += 1
                    # ent_cand_list = [pair[0] for pair in self.ctxt_link_res[cls_trps[0]]]
                    if get_vote_result(self.ctxt_link_res, cls_link_ent, cls_trps) >= 0.5:
                        # if list(ent_cnt.keys())[0] == cls_link_ent:
                        for i in cls_trps:
                            id = self.side_info.trpIds[i]
                            # if self.ctxt_link_res[i][0][0] == cls_link_ent and self.ctxt_link_res[i][0][1] > 0.7:
                            if self.ctxt_link_res[i][0][0] == cls_link_ent:
                                high_conf_trient.append((cls_link_ent, i))
                                high_conf_np.add(self.side_info.id2sub[id[0]])
                                high_conf_npent.add((t[0], cls_link_ent, i))
                    else:
                        del high_conf_cls[t[0]]
                else:
                    # print(self.ent_link_desc[])
                    only_one_cand_num += 1
                    # if v[0][1] > 0.7:
                    tri_link_ent = [self.ctxt_link_res[cls_trp_id][0][0] for cls_trp_id in cls_trps]
                    ent_cnt = Counter(tri_link_ent)
                    # print()
                    # print(self.ent_link_desc[cls_link_ent])
                    for i in cls_trps:
                        # if occ_num < max_num:
                        id = self.side_info.trpIds[i]
                        # if self.ctxt_link_res[i][0][1] > 0.7:
                        high_conf_trient.append((cls_link_ent, i))
                        high_conf_np.add(self.side_info.id2sub[id[0]])
                        high_conf_npent.add((t[0], cls_link_ent, i))
            else:
                cls_len_num += 1
                del high_conf_cls[t[0]]

        # high_conf_npent = high_conf_npent[0:max_num]

        tri_cand_ent_num /= len(self.cluster_res)
        most_occ_half_num /= len(self.cluster_res)
        cls_len_num /= len(self.cluster_res)
        only_one_cand_num /= len(self.cluster_res)

        print('candidate ent num > 3 ratio:', tri_cand_ent_num)
        print('most occurrence link ent ratio > 0.5:', most_occ_half_num)
        print('cls occ len < 3:', cls_len_num)
        print('only one cand:', only_one_cand_num)

        true_link_ratio = 0
        for trient in high_conf_trient:
            wiki_link = self.side_info.triples[trient[1]]['subject_wiki_link']
            if wiki_link == trient[0]:
                true_link_ratio += 1
        true_link_ratio /= len(high_conf_trient)
        true_link_ratio_uni = 0
        for tri, ent in self.ctxt_link_res.items():
            wiki_link = self.side_info.triples[tri]['subject_wiki_link']
            if wiki_link == ent[0][0]:
                true_link_ratio_uni += 1

        true_link_ratio_uni /= len(self.ctxt_link_res)
        print('tri link res acc:', true_link_ratio_uni)
        print('high conf cluster num:', len(final_sorted_items))
        print('high conf triple num:', len(high_conf_trient))
        print('high conf np num: ', len(high_conf_np))
        print('clusters num: ', len(self.cluster_res))
        print('high conf link res acc: ', true_link_ratio)
        # print(true_link_ratio_uni)
        print()

        self.high_tri_id = [tp[1] for tp in high_conf_trient]
        self.seed_list_cano, self.seed_list_link = [], []
        for ent_tri in high_conf_trient:
            np_id = self.side_info.trpIds[ent_tri[1]][0]
            np = self.side_info.sub_list[np_id]
            seed_pair = (np, ent_tri[0], ent_tri[1])
            self.seed_list_link.append(seed_pair)

        self.seed_list_cano = group_by_ent(list(high_conf_npent))
        print()

    def enhance(self):
        tri_same_cls_id = dict()
        for i, cls_id in enumerate(self.cluster_first_stage_res):
            same_cls_id = self.cluster_res[cls_id].copy()
            if i in same_cls_id:
                same_cls_id.remove(i)
            # same_cls_id = [id for id in same_cls_id  if id in self.high_tri_id]
            tri_same_cls_id[i] = same_cls_id
        self.bert_model.fine_tune(self.seed_list_cano, self.seed_list_link, self.side_info.triple_List,
                                  self.ent_link_desc, tri_same_cls_id, self.ctxt_link_res, self.iter, self.high_tri_id)

    def fit(self, rate=0.1):
        """阶段一：迭代微调训练。停止条件：ARI 变化率 < 1%"""
        print(">>> [Stage 1] 开始第一阶段微调训练")
        self.bert_model = Bert_Model(self.p, self.side_info)

        last_tri_assignments = None
        last_ari = 0.0
        max_epochs = 10

        for i in range(max_epochs):
            self.iter = i
            print(f'\n--- 训练 Epoch {i} ---')

            # 运行 get_seed 更新 self.cluster_res_sub 等
            self.get_seed(rate)

            # 获取当前聚类分配（基于 sub 聚类）
            current_tri_assignments = self.get_tri_assignments(self.cluster_res_sub)

            # 计算收敛条件
            if last_tri_assignments is not None and i>0:
                current_ari = adjusted_rand_score(last_tri_assignments, current_tri_assignments)
                change_rate = abs(current_ari - last_ari) / (last_ari + 1e-9)
                print(f"[收敛判定] 当前与上轮ARI: {current_ari:.4f}, 变化率: {change_rate:.2%}")

                if change_rate <= 0.01:
                    print(f"!!! 阶段一收敛 (变化率 < 1%)，停止于 iter = {i}")
                    break
                last_ari = current_ari

            last_tri_assignments = current_tri_assignments
            self.enhance()

        # 第一阶段结束，进入第二阶段
        self.test_sec()
