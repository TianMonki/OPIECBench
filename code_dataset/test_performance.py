from metrics import evaluate  # Evaluation metrics
from helper import *

ave = True


def upper_bound(uni_name, triples, true_clust2ent, true_ent2clust, clust2ent):
    cluster_list = []
    for key, value in clust2ent.items():
        cluster = []
        for ele in value:
            clean_ent = ele.split('|')[0]
            ent_id = uni_name.index(clean_ent)
            if ent_id not in cluster:
                cluster.append(ent_id)
        cluster_list.append(sorted(cluster))

    clusters = []
    for i in range(len(uni_name)):
        clusters.append(i)
    for i in cluster_list:
        for j in i:
            if clusters[j] > i[0]:
                clusters[j] = i[0]
    cluster_test(uni_name, triples, clusters, cluster_list, true_ent2clust, true_clust2ent, print_or_not=True)


def cluster_test(uni_name, triples, cluster_predict_list, cluster_list, true_ent2clust, true_clust2ent, print_or_not=False):
    sub_cluster_predict_list = []
    clust2ent = {}

    for eid in range(len(uni_name)):
        sub_cluster_predict_list.append(cluster_predict_list[eid])

    for sub_id, cluster_id in enumerate(sub_cluster_predict_list):
        if cluster_id in clust2ent.keys():
            clust2ent[cluster_id].append(sub_id)
        else:
            clust2ent[cluster_id] = [sub_id]
    cesi_clust2ent = {}
    for rep, cluster in clust2ent.items():
        # cesi_clust2ent[rep] = list(cluster)
        cesi_clust2ent[rep] = set(cluster)
    cesi_ent2clust = invertDic(cesi_clust2ent, 'm2os')

    cesi_ent2clust_u = {}
    for trp in triples:
        sub_u, sub = trp['triple_unique'][0], trp['triple_unique'][0].split('|')[0]
        cesi_ent2clust_u[sub_u] = cesi_ent2clust[uni_name.index(sub)]

    cesi_clust2ent_u = invertDic(cesi_ent2clust_u, 'm2os')
    no_uni_name = sum(len(cluster_name) for cluster_name in cluster_list)
    avg_cluster_name_num = no_uni_name / len(cesi_clust2ent_u.keys())
    print('avg_cluster_name_num : ', avg_cluster_name_num)

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
