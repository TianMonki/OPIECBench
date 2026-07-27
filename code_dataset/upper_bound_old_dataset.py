cluster_list = []
ent2clust = ddict(set)
np2most_occ_ent = dict()
for trp in self.side_info.triples:
    sub_u = trp['triple_unique'][0]

    clean_sub_u = sub_u.split('|')[0]
    sub_wiki_link = trp['true_sub_link']
    if clean_sub_u not in np2most_occ_ent.keys():
        np2most_occ_ent[clean_sub_u] = []
    np2most_occ_ent[clean_sub_u].append(sub_wiki_link)
    # clean_sub_u = sub_u.split('|')[0]
    # sub_wiki_link = trp['subject_wiki_link']
    # if clean_sub_u not in np2most_occ_ent.keys():
    #     np2most_occ_ent[clean_sub_u] = []
    # np2most_occ_ent[clean_sub_u].append(sub_wiki_link)

for k, v in np2most_occ_ent.items():
    np2most_occ_ent[k] = most_occ_ent(v)

for trp in self.side_info.triples:
    sub_u = trp['triple_unique'][0]
    clean_sub_u = sub_u.split('|')[0]
    ent2clust[sub_u].add(np2most_occ_ent[clean_sub_u])

clust2ent = invertDic(ent2clust, 'm2os')
for key, value in clust2ent.items():
    cluster = []
    for ele in value:
        clean_ent = ele.split('|')[0]
        ent_id = self.side_info.ent2id[clean_ent]
        if ent_id not in cluster:
            cluster.append(ent_id)
    cluster_list.append(sorted(cluster))
clusters = []
for i in range(len(self.side_info.sub_list)):
    clusters.append(len(self.side_info.sub_list) + 1)
for i in cluster_list:
    for j in i:
        # if clusters[j] > i[0]:
        clusters[j] = i[0]
cluster_test(self.p, self.side_info, clusters, self.true_ent2clust,
             self.true_clust2ent,
             print_or_not=True)
print()
