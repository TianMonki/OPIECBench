ent_link_dict_ps = copy.deepcopy(ent_link_dict)
ent_link_description_ps = copy.deepcopy(ent_link_description)

redirect_pairs = {}
keys_to_rm_all = []
k_to_rm_all_set = set()
no_des_ent = set()
for key in ent_link_description:
    redirect_pairs[key] = {}
    values = {}
    val = ent_link_description[key]
    keys_to_rm = []
    for sub_k, sub_v in val.items():
        if len(sub_v) == 0:
            no_des_ent.add(sub_k)
            del ent_link_description_ps[key][sub_k]
            # del ent_link_dict_ps[key][sub_k]
        else:
            # if sub_k == 'Academy Award for Writing Adapted Screenplay':
            #     print()
            if sub_v in values:
                redirect_pairs[key][sub_k] = values[sub_v]
                keys_to_rm.append(sub_k)
                keys_to_rm_all.append(sub_k)
                k_to_rm_all_set.add(sub_k)
            else:
                values[sub_v] = sub_k
    for rm_k in keys_to_rm:
        del ent_link_description_ps[key][rm_k]
        del ent_link_dict_ps[key][rm_k]