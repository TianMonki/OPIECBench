from helper import *
from utils import *
from metrics import *  # Evaluation metrics
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from tqdm import tqdm
import pickle

ave = True


# ave = False

def HAC_getClusters(params, embed1, embed2, cluster_threshold_real, mode, dim_is_bert=False):
    # if mode == 'crawl':
    #     embed_dim = 300
    # else:
    #     embed_dim = 768
    if mode == 'unity':
        embed_dim = 1068
    # else:
    #     embed_dim = 300
    elif mode == 'crawl':
        embed_dim = 300
    else:
        embed_dim = 768
    if mode == 'view-mean':
        dist1 = pdist(embed1, metric=params.metric)
        dist2 = pdist(embed2, metric=params.metric)
        dist = (dist1 + dist2) / 2
        if params.dataset == 'reverb45k':
            if not np.all(np.isfinite(dist)):
                for i in range(len(dist)):
                    if not np.isfinite(dist[i]):
                        dist[i] = 0
        clust_res = linkage(dist, method=params.linkage)
        if cluster_threshold_real[0] == 'threshold':
            labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='distance') - 1
        else:
            labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='maxclust') - 1

        return labels, None
    else:
        dist = pdist(embed1, metric=params.metric)
        if params.dataset == 'reverb45k':
            if not np.all(np.isfinite(dist)):
                for i in range(len(dist)):
                    if not np.isfinite(dist[i]):
                        dist[i] = 0
        clust_res = linkage(dist, method=params.linkage)
        if cluster_threshold_real[0] == 'threshold':
            labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='distance') - 1
        else:
            labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='maxclust') - 1
        clusters = [[] for i in range(max(labels) + 1)]
        for i in range(len(labels)):
            clusters[labels[i]].append(i)

        clusters_center = np.zeros((len(clusters), embed_dim), np.float32)
        for i in range(len(clusters)):
            cluster = clusters[i]
            if ave:
                clusters_center_embed = np.zeros(embed_dim, np.float32)
                for j in cluster:
                    embed_ = embed1[j]
                    clusters_center_embed += embed_
                clusters_center_embed_ = clusters_center_embed / len(cluster)
                clusters_center[i, :] = clusters_center_embed_
            else:
                sim_matrix = np.empty((len(cluster), len(cluster)), np.float32)
                for i in range(len(cluster)):
                    for j in range(len(cluster)):
                        if i == j:
                            sim_matrix[i, j] = 1
                        else:
                            if params.metric == 'cosine':
                                sim = cos_sim(embed1[i], embed1[j])
                            else:
                                sim = np.linalg.norm(embed1[i] - embed1[j])
                            sim_matrix[i, j] = sim
                            sim_matrix[j, i] = sim
                sim_sum = sim_matrix.sum(axis=1)
                max_num = cluster[int(np.argmax(sim_sum))]
                clusters_center[i, :] = embed1[max_num]
        # print('clusters_center:', type(clusters_center), clusters_center.shape)
        return labels, clusters_center


def cluster_test(params, side_info, name_seq_predict_list, true_ent2clust, true_clust2ent, ambi_name2triple_id, print_or_not=False):
    clust2ent = {}
    triples = side_info.triples
    cluster_predict_list = [0 for i in range(len(triples))]
    triple_ids = ambi_name2triple_id

    for i, seq_cls in enumerate(name_seq_predict_list):
        for trp_id in triple_ids[i]:
            cluster_predict_list[trp_id] = seq_cls

    for triple_index, cluster_id in enumerate(cluster_predict_list):
        if cluster_id in clust2ent.keys():
            clust2ent[cluster_id].append(triple_index)
        else:
            clust2ent[cluster_id] = [triple_index]
    cesi_clust2ent = {}
    for rep, cluster in clust2ent.items():
        # cesi_clust2ent[rep] = list(cluster)
        cesi_clust2ent[rep] = set(cluster)
    cesi_ent2clust = invertDic(cesi_clust2ent, 'm2os')

    cesi_ent2clust_u = {}
    if params.use_assume:
        for i in range(len(triples)):
            trp = triples[i]
            sub_u = trp['triple_unique'][0]
            cesi_ent2clust_u[sub_u] = set()
            cesi_ent2clust_u[sub_u].add(cluster_predict_list[i])
    cesi_clust2ent_u = invertDic(cesi_ent2clust_u, 'm2os')

    eval_results = evaluate(cesi_ent2clust_u, cesi_clust2ent_u, true_ent2clust, true_clust2ent)
    macro_prec, micro_prec, pair_prec = eval_results['macro_prec'], eval_results['micro_prec'], eval_results[
        'pair_prec']
    macro_recall, micro_recall, pair_recall = eval_results['macro_recall'], eval_results['micro_recall'], eval_results[
        'pair_recall']
    macro_f1, micro_f1, pair_f1 = eval_results['macro_f1'], eval_results['micro_f1'], eval_results['pair_f1']
    ave_prec = (macro_prec + micro_prec + pair_prec) / 3
    ave_recall = (macro_recall + micro_recall + pair_recall) / 3
    ave_f1 = (macro_f1 + micro_f1 + pair_f1) / 3
    model_clusters = len(cesi_clust2ent_u)
    model_Singletons = len([1 for _, clust in cesi_clust2ent_u.items() if len(clust) == 1])
    gold_clusters = len(true_clust2ent)
    gold_Singletons = len([1 for _, clust in true_clust2ent.items() if len(clust) == 1])

    if print_or_not:
        print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
              'pair_prec=', pair_prec)
        print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
              'pair_recall=', pair_recall)
        print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
        print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
        print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
        print()

    return ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, pair_recall, \
           macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons

def cluster_test_triple(params, side_info, cluster_predict_list, true_ent2clust, true_clust2ent, print_or_not=False):
    clust2ent = {}
    triples = side_info.triples

    for triple_index, cluster_id in enumerate(cluster_predict_list):
        if cluster_id in clust2ent.keys():
            clust2ent[cluster_id].append(triple_index)
        else:
            clust2ent[cluster_id] = [triple_index]
    cesi_clust2ent = {}
    for rep, cluster in clust2ent.items():
        # cesi_clust2ent[rep] = list(cluster)
        cesi_clust2ent[rep] = set(cluster)
    cesi_ent2clust = invertDic(cesi_clust2ent, 'm2os')

    cesi_ent2clust_u = {}
    if params.use_assume:
        for i in range(len(triples)):
            trp = triples[i]
            sub_u = trp['triple_unique'][0]
            cesi_ent2clust_u[sub_u] = set()
            cesi_ent2clust_u[sub_u].add(cluster_predict_list[i])
    cesi_clust2ent_u = invertDic(cesi_ent2clust_u, 'm2os')

    eval_results = evaluate(cesi_ent2clust_u, cesi_clust2ent_u, true_ent2clust, true_clust2ent)
    macro_prec, micro_prec, pair_prec = eval_results['macro_prec'], eval_results['micro_prec'], eval_results[
        'pair_prec']
    macro_recall, micro_recall, pair_recall = eval_results['macro_recall'], eval_results['micro_recall'], eval_results[
        'pair_recall']
    macro_f1, micro_f1, pair_f1 = eval_results['macro_f1'], eval_results['micro_f1'], eval_results['pair_f1']


    ave_prec = (macro_prec + micro_prec + pair_prec) / 3
    ave_recall = (macro_recall + micro_recall + pair_recall) / 3
    ave_f1 = (macro_f1 + micro_f1 + pair_f1) / 3
    model_clusters = len(cesi_clust2ent_u)
    model_Singletons = len([1 for _, clust in cesi_clust2ent_u.items() if len(clust) == 1])
    gold_clusters = len(true_clust2ent)
    gold_Singletons = len([1 for _, clust in true_clust2ent.items() if len(clust) == 1])
    triple_nonsingle_rate = round(1 - (model_Singletons / len(true_ent2clust)), 4)
    vote_prec = votePrecision(cesi_clust2ent_u, true_ent2clust, len(true_ent2clust) - model_Singletons)
    if print_or_not:
        print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
              'pair_prec=', pair_prec)
        print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
              'pair_recall=', pair_recall)
        print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
        print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
        print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
        print('Triple nonsingle rate: ', triple_nonsingle_rate)
        print('vote prec: ', vote_prec)
        print()

    return ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, pair_recall, \
           macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons


def trans_embed(side_info, bert_embedding, clean_ent_list):
    semantic_view_embed = []
    for ent in clean_ent_list:
        id = side_info.ent2id[ent]
        if id in side_info.isSub:
            semantic_view_embed.append(bert_embedding[id])
    print('semantic_view_embed:', len(semantic_view_embed))
    return semantic_view_embed


def cluster_result(p, side_info, view_embed1, view_embed2, cluster_threshold_real, true_ent2clust, true_clust2ent,
                   ambi_name2triple_id, mode):
    labels, clusters_center = HAC_getClusters(p, view_embed1, view_embed2, cluster_threshold_real, mode, True)
    cluster_predict_list = list(labels)

    # fname = '../cluster_predict_list_white'
    # if not checkFile(fname):
    #     print('cluster_threshold_real:', cluster_threshold_real)
    #     labels, clusters_center = HAC_getClusters(p, view_embed1, view_embed2, cluster_threshold_real, mode, True)
    #
    #     cluster_predict_list = list(labels)
    #     pickle.dump(cluster_predict_list, open(fname, 'wb'))
    # else:
    #     cluster_predict_list = pickle.load(open(fname, 'rb'))

    if mode == 'name-single':
        pass
    elif mode == 'triple-view':
        ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, \
        pair_recall, macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons \
            = cluster_test_triple(p, side_info, cluster_predict_list, true_ent2clust,
                                  true_clust2ent)
        print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
              'pair_prec=', pair_prec)
        print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
              'pair_recall=', pair_recall)
        print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
        print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
        print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
        print()
    else:
        ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, \
        pair_recall, macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons \
            = cluster_test(p, side_info, cluster_predict_list, true_ent2clust,
                                  true_clust2ent, ambi_name2triple_id)
        print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
              'pair_prec=', pair_prec)
        print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
              'pair_recall=', pair_recall)
        print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
        print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
        print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
        print()
    # else:
    #     ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, \
    #     pair_recall, macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons \
    #         = cluster_test(p, side_info, cluster_predict_list, true_ent2clust,
    #                        true_clust2ent)
    #     print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
    #           'pair_prec=', pair_prec)
    #     print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
    #           'pair_recall=', pair_recall)
    #     print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
    #     print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
    #     print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
    #     print()

    return cluster_predict_list


def seed_accuracy(seed_pairs, side_info, true_ent2clust, cls2trp):

    true_ent2clust_withoutwiki = dict()
    for k, v in true_ent2clust.items():
        k = k.split('|')[0]
        true_ent2clust_withoutwiki[k] = v

    tot_num, num = 0, 0
    for seed_pair in seed_pairs:
        if seed_pair[0] == seed_pair[1]:
            print()
        trpids_0, trpids_1 = cls2trp[seed_pair[0]], cls2trp[seed_pair[1]]
        subs_0 = [side_info.id2sub[side_info.trpIds[id][0]] for id in trpids_0]
        subs_1 = [side_info.id2sub[side_info.trpIds[id][0]] for id in trpids_1]

        cls_0 = [list(true_ent2clust_withoutwiki[sub])[0] for sub in subs_0]
        cls_1 = [list(true_ent2clust_withoutwiki[sub])[0] for sub in subs_1]

        ent_0 = Counter(cls_0)
        ent_1 = Counter(cls_1)

        most_common_ele_0 = ent_0.most_common(1)
        most_common_ele_1 = ent_1.most_common(1)

        if most_common_ele_0[0][0] == most_common_ele_1[0][0]:
            num += 1

    seed_accuracy = num / len(seed_pairs)
    return seed_accuracy

def merge_acc(merge_cls_res, side_info, true_ent2clust):
    true_ent2clust_withoutwiki = dict()
    for k, v in true_ent2clust.items():
        k = k.split('|')[0]
        true_ent2clust_withoutwiki[k] = v

    tot_num, num = 0, 0
    for merge_cls in merge_cls_res:
        ents = []
        for id in merge_cls:
            sub = side_info.id2sub[side_info.trpIds[id][0]]
            cls = list(true_ent2clust_withoutwiki[sub])[0]
            ents.append(cls)
        cnt = Counter(ents)
        most_common_ele = cnt.most_common(1)
        num += most_common_ele[0][1]
        tot_num += len(ents)

    merge_accuracy = num / tot_num
    return merge_accuracy

def score_result(seed_scores, side_info, true_ent2clust, threshold):
    total_num = len(seed_scores.keys())
    true_pos = 0
    fal_pos = 0
    fal_neg = 0
    true_neg = 0
    true_ent2clust_withoutwiki = dict()
    for k, v in true_ent2clust.items():
        k = k.split('|')[0]
        true_ent2clust_withoutwiki[k] = v

    for key, val in seed_scores.items():
        sub0, sub1 = side_info.id2sub[key[0]], side_info.id2sub[key[1]]
        if sub0 in true_ent2clust_withoutwiki.keys() and sub1 in true_ent2clust_withoutwiki.keys():
            cluster0 = true_ent2clust_withoutwiki[sub0]
            cluster1 = true_ent2clust_withoutwiki[sub1]
        if cluster0 == cluster1:
            if val >= threshold:
                true_pos += 1
            else:
                fal_neg += 1
        else:
            if val >= threshold:
                fal_pos += 1
            else:
                true_neg += 1

    precision = true_pos / (true_pos + fal_pos)
    recall = true_pos / (true_pos + fal_neg)
    accuracy = (true_pos + true_neg) / total_num

    print("threshold : ", threshold, "precision : ", precision, "recall : ", recall, "accuracy : ", accuracy)

# from utils import *
# from utils import *
# from metrics import evaluate, votePrecision  # Evaluation metrics
# from scipy.cluster.hierarchy import linkage, fcluster
# from scipy.spatial.distance import pdist
# from tqdm import tqdm
# import pickle
#
# ave = True
#
#
# # ave = False
#
# def HAC_getClusters(params, embed1, embed2, cluster_threshold_real, mode, dim_is_bert=False):
#     embed_dim = 768
#     if mode == 'view-mean':
#         dist1 = pdist(embed1, metric=params.metric)
#         dist2 = pdist(embed2, metric=params.metric)
#         dist = (dist1 + dist2) / 2
#         if params.dataset == 'reverb45k':
#             if not np.all(np.isfinite(dist)):
#                 for i in range(len(dist)):
#                     if not np.isfinite(dist[i]):
#                         dist[i] = 0
#         clust_res = linkage(dist, method=params.linkage)
#         if cluster_threshold_real[0] == 'threshold':
#             labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='distance') - 1
#         else:
#             labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='maxclust') - 1
#
#         return labels, None
#     else:
#         dist = pdist(embed1, metric=params.metric)
#         if params.dataset == 'reverb45k':
#             if not np.all(np.isfinite(dist)):
#                 for i in range(len(dist)):
#                     if not np.isfinite(dist[i]):
#                         dist[i] = 0
#         clust_res = linkage(dist, method=params.linkage)
#         if cluster_threshold_real[0] == 'threshold':
#             labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='distance') - 1
#         else:
#             labels = fcluster(clust_res, t=cluster_threshold_real[1], criterion='maxclust') - 1
#         clusters = [[] for i in range(max(labels) + 1)]
#         for i in range(len(labels)):
#             clusters[labels[i]].append(i)
#
#         clusters_center = np.zeros((len(clusters), embed_dim), np.float32)
#         for i in range(len(clusters)):
#             cluster = clusters[i]
#             if ave:
#                 clusters_center_embed = np.zeros(embed_dim, np.float32)
#                 for j in cluster:
#                     embed_ = embed1[j]
#                     clusters_center_embed += embed_
#                 clusters_center_embed_ = clusters_center_embed / len(cluster)
#                 clusters_center[i, :] = clusters_center_embed_
#             else:
#                 sim_matrix = np.empty((len(cluster), len(cluster)), np.float32)
#                 for i in range(len(cluster)):
#                     for j in range(len(cluster)):
#                         if i == j:
#                             sim_matrix[i, j] = 1
#                         else:
#                             if params.metric == 'cosine':
#                                 sim = cos_sim(embed1[i], embed1[j])
#                             else:
#                                 sim = np.linalg.norm(embed1[i] - embed1[j])
#                             sim_matrix[i, j] = sim
#                             sim_matrix[j, i] = sim
#                 sim_sum = sim_matrix.sum(axis=1)
#                 max_num = cluster[int(np.argmax(sim_sum))]
#                 clusters_center[i, :] = embed1[max_num]
#         # print('clusters_center:', type(clusters_center), clusters_center.shape)
#         return labels, clusters_center
#
#
# def cluster_test(params, side_info, name_seq_predict_list, true_ent2clust, true_clust2ent, ambi_name2triple_id, print_or_not=False):
#     clust2ent = {}
#     triples = side_info.triples
#     cluster_predict_list = [0 for i in range(len(triples))]
#     triple_ids = list(ambi_name2triple_id.values())
#
#     for i, seq_cls in enumerate(name_seq_predict_list):
#         for trp_id in triple_ids[i]:
#             cluster_predict_list[trp_id] = seq_cls
#
#     for triple_index, cluster_id in enumerate(cluster_predict_list):
#         if cluster_id in clust2ent.keys():
#             clust2ent[cluster_id].append(triple_index)
#         else:
#             clust2ent[cluster_id] = [triple_index]
#     cesi_clust2ent = {}
#     for rep, cluster in clust2ent.items():
#         # cesi_clust2ent[rep] = list(cluster)
#         cesi_clust2ent[rep] = set(cluster)
#     cesi_ent2clust = invertDic(cesi_clust2ent, 'm2os')
#
#     cesi_ent2clust_u = {}
#     if params.use_assume:
#         for i in range(len(triples)):
#             trp = triples[i]
#             sub_u = trp['triple_unique'][0]
#             cesi_ent2clust_u[sub_u] = set()
#             cesi_ent2clust_u[sub_u].add(cluster_predict_list[i])
#     cesi_clust2ent_u = invertDic(cesi_ent2clust_u, 'm2os')
#
#     eval_results = evaluate(cesi_ent2clust_u, cesi_clust2ent_u, true_ent2clust, true_clust2ent)
#     macro_prec, micro_prec, pair_prec = eval_results['macro_prec'], eval_results['micro_prec'], eval_results[
#         'pair_prec']
#     macro_recall, micro_recall, pair_recall = eval_results['macro_recall'], eval_results['micro_recall'], eval_results[
#         'pair_recall']
#     macro_f1, micro_f1, pair_f1 = eval_results['macro_f1'], eval_results['micro_f1'], eval_results['pair_f1']
#     ave_prec = (macro_prec + micro_prec + pair_prec) / 3
#     ave_recall = (macro_recall + micro_recall + pair_recall) / 3
#     ave_f1 = (macro_f1 + micro_f1 + pair_f1) / 3
#     model_clusters = len(cesi_clust2ent_u)
#     model_Singletons = len([1 for _, clust in cesi_clust2ent_u.items() if len(clust) == 1])
#
#     gold_clusters = len(true_clust2ent)
#     gold_Singletons = len([1 for _, clust in true_clust2ent.items() if len(clust) == 1])
#
#     triple_nonsingle_rate = round(1 - (model_Singletons / len(true_ent2clust)), 4)
#     votePrecision(cesi_clust2ent_u, true_ent2clust, len(true_ent2clust) - model_Singletons)
#
#     if print_or_not:
#         print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
#               'pair_prec=', pair_prec)
#         print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
#               'pair_recall=', pair_recall)
#         print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
#         print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
#         print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
#         print('Triple nonsingle rate:', triple_nonsingle_rate)
#         print('vote prec: ', votePrecision)
#         print()
#
#     return ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, pair_recall, \
#            macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons
#
#
# def cluster_test_triple(params, side_info, cluster_predict_list, true_ent2clust, true_clust2ent, print_or_not=False):
#     clust2ent = {}
#     triples = side_info.triples
#
#     for triple_index, cluster_id in enumerate(cluster_predict_list):
#         if cluster_id in clust2ent.keys():
#             clust2ent[cluster_id].append(triple_index)
#         else:
#             clust2ent[cluster_id] = [triple_index]
#     cesi_clust2ent = {}
#     for rep, cluster in clust2ent.items():
#         # cesi_clust2ent[rep] = list(cluster)
#         cesi_clust2ent[rep] = set(cluster)
#     cesi_ent2clust = invertDic(cesi_clust2ent, 'm2os')
#
#     cesi_ent2clust_u = {}
#     if params.use_assume:
#         for i in range(len(triples)):
#             trp = triples[i]
#             sub_u = trp['triple_unique'][0]
#             cesi_ent2clust_u[sub_u] = set()
#             cesi_ent2clust_u[sub_u].add(cluster_predict_list[i])
#     cesi_clust2ent_u = invertDic(cesi_ent2clust_u, 'm2os')
#
#     eval_results = evaluate(cesi_ent2clust_u, cesi_clust2ent_u, true_ent2clust, true_clust2ent)
#     macro_prec, micro_prec, pair_prec = eval_results['macro_prec'], eval_results['micro_prec'], eval_results[
#         'pair_prec']
#     macro_recall, micro_recall, pair_recall = eval_results['macro_recall'], eval_results['micro_recall'], eval_results[
#         'pair_recall']
#     macro_f1, micro_f1, pair_f1 = eval_results['macro_f1'], eval_results['micro_f1'], eval_results['pair_f1']
#
#
#     ave_prec = (macro_prec + micro_prec + pair_prec) / 3
#     ave_recall = (macro_recall + micro_recall + pair_recall) / 3
#     ave_f1 = (macro_f1 + micro_f1 + pair_f1) / 3
#     model_clusters = len(cesi_clust2ent_u)
#     model_Singletons = len([1 for _, clust in cesi_clust2ent_u.items() if len(clust) == 1])
#     gold_clusters = len(true_clust2ent)
#     gold_Singletons = len([1 for _, clust in true_clust2ent.items() if len(clust) == 1])
#     triple_nonsingle_rate = round(1 - (model_Singletons / len(true_ent2clust)), 4)
#     vote_prec = votePrecision(cesi_clust2ent_u, true_ent2clust, len(true_ent2clust) - model_Singletons)
#     if print_or_not:
#         print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
#               'pair_prec=', pair_prec)
#         print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
#               'pair_recall=', pair_recall)
#         print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
#         print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
#         print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
#         print('Triple nonsingle rate: ', triple_nonsingle_rate)
#         print('vote prec: ', vote_prec)
#         print()
#
#     return ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, pair_recall, \
#            macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons
#
#
# def trans_embed(side_info, bert_embedding, clean_ent_list):
#     semantic_view_embed = []
#     for ent in clean_ent_list:
#         id = side_info.ent2id[ent]
#         if id in side_info.isSub:
#             semantic_view_embed.append(bert_embedding[id])
#     print('semantic_view_embed:', len(semantic_view_embed))
#     return semantic_view_embed
#
#
# def cluster_result(p, side_info, view_embed1, view_embed2, cluster_threshold_real, true_ent2clust, true_clust2ent,
#                    ambi_name2triple_id, mode):
#     # print(mode)
#     labels, clusters_center = HAC_getClusters(p, view_embed1, view_embed2, cluster_threshold_real, mode, True)
#     cluster_predict_list = list(labels)
#
#     # fname = '../cluster_predict_list_white'
#     # if not checkFile(fname):
#     #     print('cluster_threshold_real:', cluster_threshold_real)
#     #     labels, clusters_center = HAC_getClusters(p, view_embed1, view_embed2, cluster_threshold_real, mode, True)
#     #
#     #     cluster_predict_list = list(labels)
#     #     pickle.dump(cluster_predict_list, open(fname, 'wb'))
#     # else:
#     #     cluster_predict_list = pickle.load(open(fname, 'rb'))
#
#     if mode == 'name-single':
#         pass
#         # print()
#     elif mode == 'triple-view':
#         ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, \
#         pair_recall, macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons \
#             = cluster_test_triple(p, side_info, cluster_predict_list, true_ent2clust,
#                                   true_clust2ent)
#         print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
#               'pair_prec=', pair_prec)
#         print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
#               'pair_recall=', pair_recall)
#         print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
#         print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
#         print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
#         print()
#     else:
#         ave_prec, ave_recall, ave_f1, macro_prec, micro_prec, pair_prec, macro_recall, micro_recall, \
#         pair_recall, macro_f1, micro_f1, pair_f1, model_clusters, model_Singletons, gold_clusters, gold_Singletons \
#             = cluster_test(p, side_info, cluster_predict_list, true_ent2clust,
#                                   true_clust2ent, ambi_name2triple_id)
#         print('Ave-prec=', ave_prec, 'macro_prec=', macro_prec, 'micro_prec=', micro_prec,
#               'pair_prec=', pair_prec)
#         print('Ave-recall=', ave_recall, 'macro_recall=', macro_recall, 'micro_recall=', micro_recall,
#               'pair_recall=', pair_recall)
#         print('Ave-F1=', ave_f1, 'macro_f1=', macro_f1, 'micro_f1=', micro_f1, 'pair_f1=', pair_f1)
#         print('Model: #Clusters: %d, #Singletons %d' % (model_clusters, model_Singletons))
#         print('Gold: #Clusters: %d, #Singletons %d' % (gold_clusters, gold_Singletons))
#         # print()
#
#
#     return cluster_predict_list
#
#
# def seed_accuracy(seed_pairs, side_info, true_ent2clust):
#     total_num = len(seed_pairs)
#
#     true_ent2clust_withoutwiki = dict()
#     for k, v in true_ent2clust.items():
#         k = k.split('|')[0]
#         true_ent2clust_withoutwiki[k] = v
#
#     num = 0
#     for seed_pair in seed_pairs:
#         sub0, sub1 = seed_pair
#         sub0, sub1 = side_info.id2sub[sub0], side_info.id2sub[sub1]
#         if sub0 in true_ent2clust_withoutwiki.keys() and sub1 in true_ent2clust_withoutwiki.keys():
#             cluster0 = true_ent2clust_withoutwiki[sub0]
#             cluster1 = true_ent2clust_withoutwiki[sub1]
#             if cluster0 == cluster1:
#                 num += 1
#                 # print(sub0, sub1)
#
#     seed_accuracy = num / total_num
#     return seed_accuracy
#
#
# def score_result(seed_scores, side_info, true_ent2clust, threshold):
#     total_num = len(seed_scores.keys())
#     true_pos = 0
#     fal_pos = 0
#     fal_neg = 0
#     true_neg = 0
#     true_ent2clust_withoutwiki = dict()
#     for k, v in true_ent2clust.items():
#         k = k.split('|')[0]
#         true_ent2clust_withoutwiki[k] = v
#
#     for key, val in seed_scores.items():
#         sub0, sub1 = side_info.id2sub[key[0]], side_info.id2sub[key[1]]
#         if sub0 in true_ent2clust_withoutwiki.keys() and sub1 in true_ent2clust_withoutwiki.keys():
#             cluster0 = true_ent2clust_withoutwiki[sub0]
#             cluster1 = true_ent2clust_withoutwiki[sub1]
#         if cluster0 == cluster1:
#             if val >= threshold:
#                 true_pos += 1
#             else:
#                 fal_neg += 1
#         else:
#             if val >= threshold:
#                 fal_pos += 1
#             else:
#                 true_neg += 1
#
#     precision = true_pos / (true_pos + fal_pos)
#     recall = true_pos / (true_pos + fal_neg)
#     accuracy = (true_pos + true_neg) / total_num
#
#     print("threshold : ", threshold, "precision : ", precision, "recall : ", recall, "accuracy : ", accuracy)
