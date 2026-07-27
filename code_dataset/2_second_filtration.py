# find_most_frequent_entity2np2triple

# filtration 2 entity frequency >= 2
# in filtration_frequency_triple_id is ok
# filtration_frequency_triple_id, filtration_frequency_entity, filtration_frequency_np has pass the first filtration
from avro.datafile import DataFileReader
from avro.io import DatumReader
import numpy as np
import pathlib
import pickle
import pdb
import time

all_file_num = 7789
filename0 = '../file/first_filtration/multi_entity_triple_id_dict'  # the first filtration
filename1 = '../file/second_filtration/np2entity_dict'
filename2 = '../file/second_filtration/entity2np_dict'
filename3 = '../file/second_filtration/np2triple_id_dict'
filename4 = '../file/second_filtration/entity2np_frequency_dict'
filename1_sub = '../file/second_filtration/sub2entity_dict'
filename2_sub = '../file/second_filtration/entity2sub_dict'
filename3_sub = '../file/second_filtration/sub2triple_id_dict'
filename4_sub = '../file/second_filtration/entity2sub_frequency_dict'
filename4_sub_entity = '../file/second_filtration/triple_id2sub_entity_dict'
filename1_obj = '../file/second_filtration/obj2entity_dict'
filename2_obj = '../file/second_filtration/entity2obj_dict'
filename3_obj = '../file/second_filtration/obj2triple_id_dict'
filename4_obj = '../file/second_filtration/entity2obj_frequency_dict'
filename4_obj_entity = '../file/second_filtration/triple_id2obj_entity_dict'
filename5 = '../file/second_filtration/descending_sorted_entity2np_frequency_dict'
filename6 = './file/second_filtration/sub2entity_dict'
filename7 = '../file/second_filtration/entity2sub_dict'
filename8 = '../file/second_filtration/sub2triple_id_dict'
filename9 = '../file/second_filtration/entity2sub_frequency_dict'
filename10 = '../file/second_filtration/descending_sorted_entity2sub_frequency_dict'

print('load multi_entity_triple_id dict')
multi_entity_triple_id_dict = pickle.load(open(filename0, 'rb'))
print('multi_entity_triple_id_dict:', type(multi_entity_triple_id_dict), len(multi_entity_triple_id_dict))  # <class 'dict'> 1985
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# open origin dataset system setting
all_triple_num, after_first_filtration_triple_num, all_frequency = 0, 0, 0
AVRO_SCHEMA_FILE = "../OPIEC-master/avroschema/TripleLinked.avsc"
AVRO_FILE_PART = "../OPIEC-Linked/OPIEC-Linked-triples/part-r-0"
# all_file_num = 7789
FILE_PART = str()
SUFFIX = ".avro"
np2entity_dict, entity2np_dict = dict(), dict()  # 假设已经通过了第一次过滤
np2triple_id_dict = dict()  # 假设已经通过了第一次过滤
entity2np_frequency_dict = dict()  # 假设已经通过了第一次过滤
sub2entity_dict, entity2sub_dict = dict(), dict()  # 假设已经通过了第一次过滤
sub2triple_id_dict = dict()  # 假设已经通过了第一次过滤
entity2sub_frequency_dict = dict()  # 假设已经通过了第一次过滤
obj2entity_dict, entity2obj_dict = dict(), dict()  # 假设已经通过了第一次过滤
obj2triple_id_dict = dict()  # 假设已经通过了第一次过滤
entity2obj_frequency_dict = dict()  # 假设已经通过了第一次过滤
triple_id2sub_entity_dict, triple_id2obj_entity_dict = dict(), dict()
# triple_id2sub_dict, triple_id2obj_dict, triple_id2np_dict = dict(), dict(), dict()
# filename1 = '../file/np2entity_dict'
# filename2 = '../file/entity2frequency_dict'

if not pathlib.Path(filename1).is_file() or not pathlib.Path(filename6).is_file():
    for FILE_NUM in range(all_file_num):
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
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print('FILE_NUM:', FILE_NUM, 'FILE_PART:', FILE_PART, 'AVRO_FILE:', AVRO_FILE)
        # AVRO_FILE = "OPIEC-Linked-triples/part-r-00000.avro"
        reader = DataFileReader(open(AVRO_FILE, "rb"), DatumReader())
        for triple in reader:
            all_triple_num += 1
            triple_id = triple['triple_id']
            if triple_id in multi_entity_triple_id_dict:  # filtration of 1 np to many entity
                continue
            else:
                after_first_filtration_triple_num += 1
                triple_list = [triple['subject'], triple['object']]
                for i in range(len(triple_list)):
                    NP = triple_list[i]
                    np_string = str()
                    if len(NP) > 1:   # start combine words to a np
                        for NP_word in NP:
                            word = NP_word['word']
                            np_string = np_string + word + ' '
                        np_string = np_string.strip()
                    else:   # start combine word to a np
                        NP_word = NP[0]
                        np_string = NP_word['word']
                    NP_word = NP[0]
                    wiki_link = NP_word['w_link']['wiki_link']

                    if len(wiki_link) > 0:
                        if np_string in np2entity_dict:
                            if wiki_link not in np2entity_dict[np_string]:
                                np2entity_dict[np_string].append(wiki_link)
                        else:
                            np2entity_dict.update({np_string: [wiki_link]})

                        if wiki_link in entity2np_dict:
                            if np_string not in entity2np_dict[wiki_link]:
                                entity2np_dict[wiki_link].append(np_string)
                        else:
                            entity2np_dict.update({wiki_link: [np_string]})

                        if np_string in np2triple_id_dict:
                            if triple_id not in np2triple_id_dict[np_string]:
                                np2triple_id_dict[np_string].append(triple_id)
                        else:
                            np2triple_id_dict.update({np_string: [triple_id]})

                        if wiki_link in entity2np_frequency_dict:
                            # entity2frequency_dict[wiki_link] += 1
                            entity2np_frequency_dict[wiki_link] = len(entity2np_dict[wiki_link])
                        else:
                            # entity2frequency_dict.update({wiki_link: 1})
                            entity2np_frequency_dict.update({wiki_link: len(entity2np_dict[wiki_link])})

                    if i == 0:
                        if len(wiki_link) > 0:
                            if np_string in sub2entity_dict:
                                if wiki_link not in sub2entity_dict[np_string]:
                                    sub2entity_dict[np_string].append(wiki_link)
                            else:
                                sub2entity_dict.update({np_string: [wiki_link]})

                            if wiki_link in entity2sub_dict:
                                if np_string not in entity2sub_dict[wiki_link]:
                                    entity2sub_dict[wiki_link].append(np_string)
                            else:
                                entity2sub_dict.update({wiki_link: [np_string]})

                            if np_string in sub2triple_id_dict:
                                if triple_id not in sub2triple_id_dict[np_string]:
                                    sub2triple_id_dict[np_string].append(triple_id)
                            else:
                                sub2triple_id_dict.update({np_string: [triple_id]})

                            if wiki_link in entity2sub_frequency_dict:
                                entity2sub_frequency_dict[wiki_link] = len(entity2sub_dict[wiki_link])
                            else:
                                entity2sub_frequency_dict.update({wiki_link: len(entity2sub_dict[wiki_link])})

                            if triple_id in triple_id2sub_entity_dict:
                                if wiki_link not in triple_id2sub_entity_dict[triple_id]:
                                    triple_id2sub_entity_dict[triple_id].append(wiki_link)
                            else:
                                triple_id2sub_entity_dict.update({triple_id: [wiki_link]})
                    else:
                        if len(wiki_link) > 0:
                            if np_string in obj2entity_dict:
                                if wiki_link not in obj2entity_dict[np_string]:
                                    obj2entity_dict[np_string].append(wiki_link)
                            else:
                                obj2entity_dict.update({np_string: [wiki_link]})

                            if wiki_link in entity2obj_dict:
                                if np_string not in entity2obj_dict[wiki_link]:
                                    entity2obj_dict[wiki_link].append(np_string)
                            else:
                                entity2obj_dict.update({wiki_link: [np_string]})

                            if np_string in obj2triple_id_dict:
                                if triple_id not in obj2triple_id_dict[np_string]:
                                    obj2triple_id_dict[np_string].append(triple_id)
                            else:
                                obj2triple_id_dict.update({np_string: [triple_id]})

                            if wiki_link in entity2obj_frequency_dict:
                                entity2obj_frequency_dict[wiki_link] = len(entity2obj_dict[wiki_link])
                            else:
                                entity2obj_frequency_dict.update({wiki_link: len(entity2obj_dict[wiki_link])})

                            if triple_id in triple_id2obj_entity_dict:
                                if wiki_link not in triple_id2obj_entity_dict[triple_id]:
                                    triple_id2obj_entity_dict[triple_id].append(wiki_link)
                            else:
                                triple_id2obj_entity_dict.update({triple_id: [wiki_link]})
        reader.close()
    pickle.dump(np2entity_dict, open(filename1, 'wb'))
    pickle.dump(entity2np_dict, open(filename2, 'wb'))
    pickle.dump(np2triple_id_dict, open(filename3, 'wb'))
    pickle.dump(entity2np_frequency_dict, open(filename4, 'wb'))
    pickle.dump(sub2entity_dict, open(filename1_sub, 'wb'))
    pickle.dump(obj2entity_dict, open(filename1_obj, 'wb'))
    pickle.dump(entity2sub_dict, open(filename2_sub, 'wb'))
    pickle.dump(entity2obj_dict, open(filename2_obj, 'wb'))
    pickle.dump(sub2triple_id_dict, open(filename3_sub, 'wb'))
    pickle.dump(obj2triple_id_dict, open(filename3_obj, 'wb'))
    pickle.dump(entity2sub_frequency_dict, open(filename4_sub, 'wb'))
    pickle.dump(entity2obj_frequency_dict, open(filename4_obj, 'wb'))
    pickle.dump(triple_id2sub_entity_dict, open(filename4_sub_entity, 'wb'))
    pickle.dump(triple_id2obj_entity_dict, open(filename4_obj_entity, 'wb'))
else:
    print('load np2entity_dict ... ')
    np2entity_dict = pickle.load(open(filename1, 'rb'))
    entity2np_dict = pickle.load(open(filename2, 'rb'))
    np2triple_id_dict = pickle.load(open(filename3, 'rb'))
    entity2np_frequency_dict = pickle.load(open(filename4, 'rb'))
    sub2entity_dict = pickle.load(open(filename1_sub, 'rb'))
    obj2entity_dict = pickle.load(open(filename1_obj, 'rb'))
    entity2sub_dict = pickle.load(open(filename2_sub, 'rb'))
    entity2obj_dict = pickle.load(open(filename2_obj, 'rb'))
    sub2triple_id_dict = pickle.load(open(filename3_sub, 'rb'))
    obj2triple_id_dict = pickle.load(open(filename3_obj, 'rb'))
    entity2sub_frequency_dict = pickle.load(open(filename4_sub, 'rb'))
    entity2obj_frequency_dict = pickle.load(open(filename4_obj, 'rb'))
    triple_id2sub_entity_dict = pickle.load(open(filename4_sub_entity, 'rb'))
    triple_id2obj_entity_dict = pickle.load(open(filename4_obj_entity, 'rb'))

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print('all_triple_num:', all_triple_num)  # demo 5875  5819752
print('after_first_filtration_triple_num:', after_first_filtration_triple_num)  # demo 5875  5817767
print('np2entity_dict:', type(np2entity_dict), len(np2entity_dict))  # demo 7735  2135408
print('entity2np_dict:', type(entity2np_dict), len(entity2np_dict))  # demo 7824  2256540
print('np2triple_id_dict:', type(np2triple_id_dict), len(np2triple_id_dict))  # demo 7735  2135408
print('entity2np_frequency_dict:', type(entity2np_frequency_dict), len(entity2np_frequency_dict))  # demo 7824  2256540
print('sub2entity_dict:', type(sub2entity_dict), len(sub2entity_dict))  # 1633143
print('entity2sub_dict:', type(entity2sub_dict), len(entity2sub_dict))  # 1743357
print('sub2triple_id_dict:', type(sub2triple_id_dict), len(sub2triple_id_dict))  # 1633143
print('entity2sub_frequency_dict:', type(entity2sub_frequency_dict), len(entity2sub_frequency_dict))  # 1743357
print('obj2entity_dict:', type(obj2entity_dict), len(obj2entity_dict))  # 927353
print('entity2obj_dict:', type(entity2obj_dict), len(entity2obj_dict))  # 1001949
print('obj2triple_id_dict:', type(obj2triple_id_dict), len(obj2triple_id_dict))  # 927353
print('entity2obj_frequency_dict:', type(entity2obj_frequency_dict), len(entity2obj_frequency_dict))  # 1001949
print('triple_id2sub_entity_dict:', type(triple_id2sub_entity_dict), len(triple_id2sub_entity_dict))  # 5749207
print('triple_id2obj_entity_dict:', type(triple_id2obj_entity_dict), len(triple_id2obj_entity_dict))  # 5680100

print("按值(value)排序:")
if not pathlib.Path(filename5).is_file() or not pathlib.Path(filename10).is_file():
    descending_sorted_entity2np_frequency_dict = sorted(entity2np_frequency_dict.items(), key=lambda kv: (kv[1], kv[0]),
                                                        reverse=True)
    descending_sorted_entity2sub_frequency_dict = sorted(entity2sub_frequency_dict.items(), key=lambda kv: (kv[1], kv[0]),
                                                         reverse=True)
    pickle.dump(descending_sorted_entity2np_frequency_dict, open(filename5, 'wb'))
    pickle.dump(descending_sorted_entity2sub_frequency_dict, open(filename10, 'wb'))
else:
    print('load descending_sorted_entity2np_frequency_dict ... ')
    descending_sorted_entity2np_frequency_dict = pickle.load(open(filename5, 'rb'))
    descending_sorted_entity2sub_frequency_dict = pickle.load(open(filename10, 'rb'))
print('descending_sorted_entity2np_frequency_dict:', type(descending_sorted_entity2np_frequency_dict),
      len(descending_sorted_entity2np_frequency_dict))  #  <class 'list'> 2256540
print('descending_sorted_entity2sub_frequency_dict:', type(descending_sorted_entity2sub_frequency_dict),
      len(descending_sorted_entity2sub_frequency_dict))  # <class 'list'> 1743357
print()

filename5_triple_id2sub_dict = '../file/second_filtration/triple_id2sub_dict'
if not pathlib.Path(filename5_triple_id2sub_dict).is_file():
    print('generate triple_id2sub_dict')
    triple_id2sub_dict = dict()
    for sub in sub2triple_id_dict.keys():
        triple_id_list = sub2triple_id_dict[sub]
        for triple_id in triple_id_list:
            if triple_id in triple_id2sub_dict:
                if sub not in triple_id2sub_dict[triple_id]:
                    triple_id2sub_dict[triple_id].append(sub)
            else:
                triple_id2sub_dict.update({triple_id: [sub]})
    pickle.dump(triple_id2sub_dict, open(filename5_triple_id2sub_dict, 'wb'))
else:
    print('load triple_id2sub_dict')
    triple_id2sub_dict = pickle.load(open(filename5_triple_id2sub_dict, 'rb'))


filename5_triple_id2obj_dict = '../file/second_filtration/triple_id2obj_dict'
if not pathlib.Path(filename5_triple_id2obj_dict).is_file():
    print('generate triple_id2obj')
    triple_id2obj_dict = dict()
    for obj in obj2triple_id_dict.keys():
        triple_id_list = obj2triple_id_dict[obj]
        for triple_id in triple_id_list:
            if triple_id in triple_id2obj_dict:
                if obj not in triple_id2obj_dict[triple_id]:
                    triple_id2obj_dict[triple_id].append(obj)
            else:
                triple_id2obj_dict.update({triple_id: [obj]})
    pickle.dump(triple_id2obj_dict, open(filename5_triple_id2obj_dict, 'wb'))
else:
    print('load triple_id2obj')
    triple_id2obj_dict = pickle.load(open(filename5_triple_id2obj_dict, 'rb'))

print('triple_id2sub_dict:', len(triple_id2sub_dict))  # 5749207
print('triple_id2obj_dict:', len(triple_id2obj_dict))  # 5680100

filename_final_dataset_OPIEC = '../file/final_dataset/OPIEC_53k_triple_id'
max_threshold, min_threshold = 30, 3
sub2triple_threshold, obj2triple_threshold = 3, 3
second_min_threshold = 3
max_sub2entity_num = 4
subject_max_triple_id = 500
save = True

if not pathlib.Path(filename_final_dataset_OPIEC).is_file():
    print('generate final dataset:', filename_final_dataset_OPIEC)
    triple_id_dict, subject_entity_dict, object_entity_dict, subject_dict, object_dict \
        = dict(), dict(), dict(), dict(), dict()
    for j in range(len(descending_sorted_entity2sub_frequency_dict)):
        sub_entity, frequency = descending_sorted_entity2sub_frequency_dict[j][0], \
                                descending_sorted_entity2sub_frequency_dict[j][1]
        if frequency > min_threshold and frequency < max_threshold:  # entity has many sub
            if sub_entity in entity2sub_dict:
                subject_list = entity2sub_dict[sub_entity]
                for subject in subject_list:
                    triple_id_list = sub2triple_id_dict[subject]
                    real_triple_id_list = []
                    for triple_id in triple_id_list:
                        triple_sub_entity_list = triple_id2sub_entity_dict[triple_id]
                        assert len(triple_sub_entity_list) == 1
                        triple_entity = triple_sub_entity_list[0]
                        if triple_entity == sub_entity:
                            real_triple_id_list.append(triple_id)
                    if len(real_triple_id_list) > sub2triple_threshold:  # sub has many triple
                        num = 0
                        triple_id_dict_length = 0
                        for triple_id in real_triple_id_list:

                            if triple_id in triple_id2obj_dict:
                                object_list = triple_id2obj_dict[triple_id]
                                assert len(object_list) == 1
                                object = object_list[0]
                                obj_triple_id_list = obj2triple_id_dict[object]
                                if len(obj_triple_id_list) > obj2triple_threshold:
                                    triple_id_dict_length += 1
                                    num += 1
                                    if triple_id not in triple_id_dict:
                                        triple_id_dict.update({triple_id: 1})
                                    else:
                                        triple_id_dict[triple_id] += 1

                                    if triple_id in triple_id2obj_entity_dict:
                                        object_entity_list = triple_id2obj_entity_dict[triple_id]
                                        assert len(object_entity_list) == 1
                                        object_entity = object_entity_list[0]

                                        if object not in object_dict:
                                            object_dict.update({object: [object_entity]})
                                        else:
                                            if object_entity not in object_dict[object]:
                                                object_dict[object].append(object_entity)

                                        object_entity_dict.update({object_entity: 1})
                            if triple_id_dict_length > subject_max_triple_id:
                                break
                        if num > 0:
                        # if not num < 0:
                            if subject not in subject_dict:
                                subject_dict.update({subject: [sub_entity]})
                            else:
                                if sub_entity not in subject_dict[subject]:
                                    subject_dict[subject].append(sub_entity)

                            if sub_entity not in subject_entity_dict:
                                subject_entity_dict.update({sub_entity: 1})

    triple_id_num = len(triple_id_dict)
    subject_num, object_num, np_num = 0, 0, 0
    real_subject_dict, real_object_dict = dict(), dict()
    sub_entity2sub_list_dict, obj_entity2obj_list_dict = dict(), dict()
    sub2triple_id_list_dict, obj2triple_id_list_dict = dict(), dict()
    sub_entity_min_num, sub_entity_ave_num, sub_entity_max_num = 100000, 0, 0
    num_of_sub_entity_min, num_of_obj_entity_min = 0, 0
    obj_entity_min_num, obj_entity_ave_num, obj_entity_max_num = 100000, 0, 0
    sub2triple_id_min_num, sub2triple_id_ave_num, sub2triple_id_max_num = 100000, 0, 0
    obj2triple_id_min_num, obj2triple_id_ave_num, obj2triple_id_max_num = 100000, 0, 0
    num_of_sub_triple_id_min, num_of_obj_triple_id_min = 0, 0

    # for k in triple_id_dict.keys():
    #     v = triple_id_dict[k]
    #     triple_id_num += v

    for triple_id in triple_id_dict:
        subject_list = triple_id2sub_dict[triple_id]
        object_list = triple_id2obj_dict[triple_id]
        sub_entity_list = triple_id2sub_entity_dict[triple_id]
        obj_entity_list = triple_id2obj_entity_dict[triple_id]
        for subject in subject_list:
            sub_entity_list_2 = sub2entity_dict[subject]
            if subject not in real_subject_dict:
                for sub_entity in sub_entity_list_2:
                    if sub_entity in sub_entity_list:
                        real_subject_dict.update({subject: [sub_entity]})
            else:
                for sub_entity in sub_entity_list_2:
                    if sub_entity in sub_entity_list:
                        if sub_entity not in real_subject_dict[subject]:
                            real_subject_dict[subject].append(sub_entity)

            for sub_entity in sub_entity_list:
                if sub_entity not in sub_entity2sub_list_dict:
                    sub_entity2sub_list_dict.update({sub_entity: [subject]})
                else:
                    if subject not in sub_entity2sub_list_dict[sub_entity]:
                        sub_entity2sub_list_dict[sub_entity].append(subject)

            if subject not in sub2triple_id_list_dict:
                sub2triple_id_list_dict.update({subject: [triple_id]})
            else:
                if triple_id not in sub2triple_id_list_dict[subject]:
                    sub2triple_id_list_dict[subject].append(triple_id)

        for object in object_list:
            obj_entity_list_2 = obj2entity_dict[object]
            if object not in real_object_dict:
                for obj_entity in obj_entity_list_2:
                    if obj_entity in obj_entity_list:
                        real_object_dict.update({object: [obj_entity]})
            else:
                for obj_entity in obj_entity_list_2:
                    if obj_entity in obj_entity_list:
                        if obj_entity not in real_object_dict[object]:
                            real_object_dict[object].append(obj_entity)
            for obj_entity in obj_entity_list:
                if obj_entity not in obj_entity2obj_list_dict:
                    obj_entity2obj_list_dict.update({obj_entity: [object]})
                else:
                    obj_entity2obj_list_dict[obj_entity].append(object)

            if object not in obj2triple_id_list_dict:
                obj2triple_id_list_dict.update({object: [triple_id]})
            else:
                if triple_id not in obj2triple_id_list_dict[object]:
                    obj2triple_id_list_dict[object].append(triple_id)

    for subject in real_subject_dict.keys():
        subject_num += len(real_subject_dict[subject])
    for object in real_object_dict.keys():
        object_num += len(real_object_dict[object])

    for sub_entity in sub_entity2sub_list_dict:
        sub_list = sub_entity2sub_list_dict[sub_entity]
        length = len(sub_list)
        if length < sub_entity_min_num:
            sub_entity_min_num = length
        if length > sub_entity_max_num:
            sub_entity_max_num = length

    for sub_entity in sub_entity2sub_list_dict:
        sub_list = sub_entity2sub_list_dict[sub_entity]
        length = len(sub_list)
        if length == sub_entity_min_num:
            num_of_sub_entity_min += 1

    for obj_entity in obj_entity2obj_list_dict:
        obj_list = obj_entity2obj_list_dict[obj_entity]
        length = len(obj_list)
        if length < obj_entity_min_num:
            obj_entity_min_num = length
        if length > obj_entity_max_num:
            obj_entity_max_num = length

    for obj_entity in obj_entity2obj_list_dict:
        obj_list = obj_entity2obj_list_dict[obj_entity]
        length = len(obj_list)
        if length == obj_entity_min_num:
            num_of_obj_entity_min += 1

    for subject in sub2triple_id_list_dict:
        subject_list = sub2triple_id_list_dict[subject]
        length = len(subject_list)
        if length < sub2triple_id_min_num:
            sub2triple_id_min_num = length
        if length > sub2triple_id_max_num:
            sub2triple_id_max_num = length

    for subject in sub2triple_id_list_dict:
        subject_list = sub2triple_id_list_dict[subject]
        length = len(subject_list)
        if length == sub2triple_id_min_num:
            num_of_sub_triple_id_min += 1

    for object in obj2triple_id_list_dict:
        object_list = obj2triple_id_list_dict[object]
        length = len(object_list)
        if length < obj2triple_id_min_num:
            obj2triple_id_min_num = length
        if length > obj2triple_id_max_num:
            obj2triple_id_max_num = length

    for object in obj2triple_id_list_dict:
        object_list = obj2triple_id_list_dict[object]
        length = len(object_list)
        if length == obj2triple_id_min_num:
            num_of_obj_triple_id_min += 1

    sub_entity_num = len(sub_entity2sub_list_dict)
    obj_entity_num = len(obj_entity2obj_list_dict)
    sub2triple_id_ave_num = triple_id_num / subject_num
    obj2triple_id_ave_num = triple_id_num / object_num
    sub_entity_ave_num = subject_num / sub_entity_num
    obj_entity_ave_num = object_num / obj_entity_num
    ratio_of_sub_entity_min = num_of_sub_entity_min / sub_entity_num
    ratio_of_obj_entity_min = num_of_obj_entity_min / obj_entity_num
    ratio_of_sub_triple_id_min = num_of_sub_triple_id_min / subject_num
    ratio_of_obj_triple_id_min = num_of_obj_triple_id_min / object_num

    print('first time check')
    print('max_threshold:', max_threshold, 'min_threshold:', min_threshold, 'sub2triple_threshold:',
          sub2triple_threshold, 'obj2triple_threshold:', obj2triple_threshold, 'second_min_threshold:',
          second_min_threshold, 'max_sub2entity_num:', max_sub2entity_num,
          'subject_max_triple_id:', subject_max_triple_id)
    print('triple_id num:', triple_id_num, 'subject_entity:', sub_entity_num, 'subject:', subject_num,
          'object_entity:', obj_entity_num, 'object:',
          object_num)  # entity_string only 1, if np_entity is different, then np is different
    print('different np subject_dict:', len(real_subject_dict), 'object_dict:', len(real_object_dict))
    print('sub_entity_min_num:', sub_entity_min_num, 'num_of_sub_entity_min:', num_of_sub_entity_min,
          'ratio_of_sub_entity_min:', ratio_of_sub_entity_min)
    print('obj_entity_min_num:', obj_entity_min_num, 'num_of_obj_entity_min:', num_of_obj_entity_min,
          'ratio_of_obj_entity_min:', ratio_of_obj_entity_min)
    print('sub_entity_ave_num:', sub_entity_ave_num, 'obj_entity_ave_num:', obj_entity_ave_num)
    print('sub_entity_max_num:', sub_entity_max_num, 'obj_entity_max_num:', obj_entity_max_num)
    print('sub2triple_id_min_num:', sub2triple_id_min_num, 'num_of_sub_triple_id_min:', num_of_sub_triple_id_min,
          'ratio_of_sub_triple_id_min:', ratio_of_sub_triple_id_min)
    print('obj2triple_id_min_num:', obj2triple_id_min_num, 'num_of_obj_triple_id_min:', num_of_obj_triple_id_min,
          'ratio_of_obj_triple_id_min:', ratio_of_obj_triple_id_min)
    print('sub2triple_id_ave_num:', sub2triple_id_ave_num, 'sub2triple_id_max_num:', sub2triple_id_max_num)
    print('obj2triple_id_ave_num:', obj2triple_id_ave_num, 'obj2triple_id_max_num:', obj2triple_id_max_num)

    # second time check : sub_entity at least has 3 subject
    ambiguous_subject_dict, ambiguous_triple_dict = dict(), dict()
    for subject in subject_dict.keys():
        subject_num += len(subject_dict[subject])
        length = len(subject_dict[subject])
        if length > max_sub2entity_num:
            if subject not in ambiguous_subject_dict:
                ambiguous_subject_dict.update({subject: 1})
            for triple_id in sub2triple_id_list_dict[subject]:
                if triple_id not in ambiguous_triple_dict:
                    ambiguous_triple_dict.update({triple_id: 1})

    ambiguous_sub2entity2freq_dict = dict()
    for triple_id in ambiguous_triple_dict:
        subject_list = triple_id2sub_dict[triple_id]
        triple_sub_entity_list = triple_id2sub_entity_dict[triple_id]
        for subject in subject_list:
            if subject in ambiguous_subject_dict:
                sub_entity_list = subject_dict[subject]
                for sub_entity in sub_entity_list:
                    for triple_sub_entity in triple_sub_entity_list:
                        if sub_entity == triple_sub_entity:
                            if subject not in ambiguous_sub2entity2freq_dict:
                                ambiguous_sub2entity2freq_dict.update({subject: {sub_entity: 1}})
                            else:
                                if sub_entity not in ambiguous_sub2entity2freq_dict[subject]:
                                    ambiguous_sub2entity2freq_dict[subject].update({sub_entity: 1})
                                else:
                                    ambiguous_sub2entity2freq_dict[subject][sub_entity] += 1
    # print('ambiguous_sub2entity2freq_dict:', len(ambiguous_sub2entity2freq_dict))
    old_ambiguous_sub2entity2freq_dict = ambiguous_sub2entity2freq_dict.copy()
    for subject in old_ambiguous_sub2entity2freq_dict:
        length = len(old_ambiguous_sub2entity2freq_dict[subject])
        while length > max_sub2entity_num:
            if subject in subject_dict:
                entity_freq_dict = ambiguous_sub2entity2freq_dict[subject]
                max_freq_num, max_freq_entity = 0, str()
                second_max_freq_num, second_max_freq_entity = 0, str()
                for entity in entity_freq_dict:
                    freq = entity_freq_dict[entity]
                    if freq > max_freq_num:
                        max_freq_num = freq
                        max_freq_entity = entity
                for entity in entity_freq_dict:
                    freq = entity_freq_dict[entity]
                    second_tf = ((freq < max_freq_num) or (freq == max_freq_num))
                    if freq > second_max_freq_num and second_tf:
                        second_max_freq_num = freq
                        second_max_freq_entity = entity
                assert max_freq_num == entity_freq_dict[max_freq_entity]
                assert second_max_freq_num == entity_freq_dict[second_max_freq_entity]

                if second_max_freq_entity in ambiguous_sub2entity2freq_dict[subject]:
                    ambiguous_sub2entity2freq_dict[subject].pop(second_max_freq_entity)

                if second_max_freq_entity in subject_dict[subject]:
                    subject_dict[subject].remove(second_max_freq_entity)  # del sub

                    triple_id_list = sub2triple_id_dict[subject]
                    for triple_id in triple_id_list:
                        triple_sub_entity_list = triple_id2sub_entity_dict[triple_id]
                        assert len(triple_sub_entity_list) == 1
                        triple_entity = triple_sub_entity_list[0]
                        if triple_entity == second_max_freq_entity:
                            # if triple_id in triple_id_dict and triple_id in ambiguous_triple_dict:
                            #     triple_id_dict[triple_id] -= 1
                            #     if triple_id_dict[triple_id] == 0:
                            #         triple_id_dict.pop(triple_id)  # del triple_id
                            if triple_id in triple_id_dict and triple_id in ambiguous_triple_dict:
                                triple_id_dict.pop(triple_id)  # del triple_id
            length -= 1
    # #########################################################################################################

    old_subject_entity_dict = subject_entity_dict.copy()
    for subject_entity in old_subject_entity_dict:
        old_subject_list = entity2sub_dict[subject_entity]
        new_subject_list = []
        for subject in old_subject_list:
            if subject in subject_dict:
                if subject_entity in subject_dict[subject]:
                    new_subject_list.append(subject)
                    # if not len(old_subject_dict[subject]) > max_sub2entity_num:  # subject has no more than 2 entities
                    #     new_subject_list.append(subject)
        if not len(new_subject_list) > second_min_threshold:  # check
            if subject_entity in subject_entity_dict:
                subject_entity_dict.pop(subject_entity)  # del sub_entity
            for subject in new_subject_list:
                if subject in subject_dict:
                    if subject_entity in subject_dict[subject]:
                        subject_dict[subject].remove(subject_entity)
                    if len(subject_dict[subject]) == 0:
                    # if len(subject_dict[subject]) == 0 or len(old_subject_dict[subject]) > max_sub2entity_num:
                        subject_dict.pop(subject)  # del sub

                triple_id_list = sub2triple_id_dict[subject]
                for triple_id in triple_id_list:
                    triple_sub_entity_list = triple_id2sub_entity_dict[triple_id]
                    assert len(triple_sub_entity_list) == 1
                    triple_entity = triple_sub_entity_list[0]
                    if triple_entity == subject_entity:
                        if triple_id in triple_id_dict:
                            # triple_id_dict[triple_id] -= 1
                            # if triple_id_dict[triple_id] == 0:
                            #     triple_id_dict.pop(triple_id)  # del triple_id
                            triple_id_dict.pop(triple_id)  # del triple_id
                        if triple_id in triple_id2obj_entity_dict:
                            object_entity_list = triple_id2obj_entity_dict[triple_id]
                            object_entity = object_entity_list[0]
                            if object_entity in object_entity_dict:
                                object_entity_dict.pop(object_entity)  # del obj_entity

                            if triple_id in triple_id2obj_dict:
                                object_list = triple_id2obj_dict[triple_id]
                                object = object_list[0]
                                if object in object_dict:
                                    if object_entity in object_dict[object]:
                                        object_dict[object].remove(object_entity)
                                    if len(object_dict[object]) == 0:
                                        object_dict.pop(object)  # del obj

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    subject_num, object_num, np_num = 0, 0, 0
    subject_dict, object_dict = dict(), dict()
    sub_entity2sub_list_dict, obj_entity2obj_list_dict = dict(), dict()
    sub2triple_id_list_dict, obj2triple_id_list_dict = dict(), dict()
    sub_entity_min_num, sub_entity_ave_num, sub_entity_max_num = 100000, 0, 0
    num_of_sub_entity_min, num_of_obj_entity_min = 0, 0
    obj_entity_min_num, obj_entity_ave_num, obj_entity_max_num = 100000, 0, 0
    sub2triple_id_min_num, sub2triple_id_ave_num, sub2triple_id_max_num = 100000, 0, 0
    obj2triple_id_min_num, obj2triple_id_ave_num, obj2triple_id_max_num = 100000, 0, 0
    num_of_sub_triple_id_min, num_of_obj_triple_id_min = 0, 0

    # for k in triple_id_dict.keys():
    #     v = triple_id_dict[k]
    #     triple_id_num += v
    triple_id_num = len(triple_id_dict)

    for triple_id in triple_id_dict:
        subject = triple_id2sub_dict[triple_id][0]
        object = triple_id2obj_dict[triple_id][0]
        sub_entity = triple_id2sub_entity_dict[triple_id][0]
        obj_entity = triple_id2obj_entity_dict[triple_id][0]
        if subject not in subject_dict:
            subject_dict.update({subject: [sub_entity]})
        else:
            if sub_entity not in subject_dict[subject]:
                 subject_dict[subject].append(sub_entity)

        if sub_entity not in sub_entity2sub_list_dict:
            sub_entity2sub_list_dict.update({sub_entity: [subject]})
        else:
            if subject not in sub_entity2sub_list_dict[sub_entity]:
                sub_entity2sub_list_dict[sub_entity].append(subject)

        if subject not in sub2triple_id_list_dict:
            sub2triple_id_list_dict.update({subject: [triple_id]})
        else:
            if triple_id not in sub2triple_id_list_dict[subject]:
                sub2triple_id_list_dict[subject].append(triple_id)

        if object not in object_dict:
            object_dict.update({object: [obj_entity]})
        else:
            if obj_entity not in object_dict[object]:
                object_dict[object].append(obj_entity)

        if obj_entity not in obj_entity2obj_list_dict:
            obj_entity2obj_list_dict.update({obj_entity: [object]})
        else:
            obj_entity2obj_list_dict[obj_entity].append(object)

        if object not in obj2triple_id_list_dict:
            obj2triple_id_list_dict.update({object: [triple_id]})
        else:
            if triple_id not in obj2triple_id_list_dict[object]:
                obj2triple_id_list_dict[object].append(triple_id)

    ambiguous_num, ambiguous_triple_num = 0, 0
    ambiguous_sub2entity_min_num, ambiguous_sub2entity_ave_num, ambiguous_sub2entity_max_num = 100, 0, 0
    ambiguous_subject_dict, ambiguous_triple_dict = dict(), dict()
    for subject in subject_dict.keys():
        subject_num += len(subject_dict[subject])

        length = len(subject_dict[subject])
        if length > 1:
            if length < ambiguous_sub2entity_min_num:
                ambiguous_sub2entity_min_num = length
            if length > ambiguous_sub2entity_max_num:
                ambiguous_sub2entity_max_num = length
            ambiguous_sub2entity_ave_num += length
            if subject not in ambiguous_subject_dict:
                ambiguous_subject_dict.update({subject: 1})
            for triple_id in sub2triple_id_list_dict[subject]:
                if triple_id not in ambiguous_triple_dict:
                    ambiguous_triple_dict.update({triple_id: 1})
    ambiguous_num = len(ambiguous_subject_dict)

    ambiguous_sub2entity2freq_dict = dict()
    for triple_id in ambiguous_triple_dict:
        subject_list = triple_id2sub_dict[triple_id]
        triple_sub_entity_list = triple_id2sub_entity_dict[triple_id]
        for subject in subject_list:
            if subject in ambiguous_subject_dict:
                sub_entity_list = subject_dict[subject]
                for sub_entity in sub_entity_list:
                    for triple_sub_entity in triple_sub_entity_list:
                        if sub_entity == triple_sub_entity:
                            if subject not in ambiguous_sub2entity2freq_dict:
                                ambiguous_sub2entity2freq_dict.update({subject: {sub_entity: 1}})
                            else:
                                if sub_entity not in ambiguous_sub2entity2freq_dict[subject]:
                                    ambiguous_sub2entity2freq_dict[subject].update({sub_entity: 1})
                                else:
                                    ambiguous_sub2entity2freq_dict[subject][sub_entity] += 1
    # print('ambiguous_sub2entity2freq_dict:', len(ambiguous_sub2entity2freq_dict))

    all_ambiguous_triple_num, assume_triple_num = 0, 0
    for subject in ambiguous_sub2entity2freq_dict:
        entity_freq_dict = ambiguous_sub2entity2freq_dict[subject]
        most_freq_num, most_freq_entity = 0, str()
        for entity in entity_freq_dict:
            freq = entity_freq_dict[entity]
            all_ambiguous_triple_num += freq
            if freq > most_freq_num:
                most_freq_num = freq
                most_freq_entity = entity
        assert most_freq_num == entity_freq_dict[most_freq_entity]
        assume_triple_num += most_freq_num

    for object in object_dict.keys():
        object_num += len(object_dict[object])

    for sub_entity in sub_entity2sub_list_dict:
        sub_list = sub_entity2sub_list_dict[sub_entity]
        length = len(sub_list)
        if length < sub_entity_min_num:
            sub_entity_min_num = length
        if length > sub_entity_max_num:
            sub_entity_max_num = length

    for sub_entity in sub_entity2sub_list_dict:
        sub_list = sub_entity2sub_list_dict[sub_entity]
        length = len(sub_list)
        if length == sub_entity_min_num:
            num_of_sub_entity_min += 1

    for obj_entity in obj_entity2obj_list_dict:
        obj_list = obj_entity2obj_list_dict[obj_entity]
        length = len(obj_list)
        if length < obj_entity_min_num:
            obj_entity_min_num = length
        if length > obj_entity_max_num:
            obj_entity_max_num = length

    for obj_entity in obj_entity2obj_list_dict:
        obj_list = obj_entity2obj_list_dict[obj_entity]
        length = len(obj_list)
        if length == obj_entity_min_num:
            num_of_obj_entity_min += 1

    for subject in sub2triple_id_list_dict:
        subject_list = sub2triple_id_list_dict[subject]
        length = len(subject_list)
        if length < sub2triple_id_min_num:
            sub2triple_id_min_num = length
        if length > sub2triple_id_max_num:
            sub2triple_id_max_num = length

    for subject in sub2triple_id_list_dict:
        subject_list = sub2triple_id_list_dict[subject]
        length = len(subject_list)
        if length == sub2triple_id_min_num:
            num_of_sub_triple_id_min += 1

    for object in obj2triple_id_list_dict:
        object_list = obj2triple_id_list_dict[object]
        length = len(object_list)
        if length < obj2triple_id_min_num:
            obj2triple_id_min_num = length
        if length > obj2triple_id_max_num:
            obj2triple_id_max_num = length

    for object in obj2triple_id_list_dict:
        object_list = obj2triple_id_list_dict[object]
        length = len(object_list)
        if length == obj2triple_id_min_num:
            num_of_obj_triple_id_min += 1

    sub_entity_num = len(sub_entity2sub_list_dict)
    obj_entity_num = len(obj_entity2obj_list_dict)
    sub2triple_id_ave_num = triple_id_num / subject_num
    obj2triple_id_ave_num = triple_id_num / object_num
    sub_entity_ave_num = subject_num / sub_entity_num
    obj_entity_ave_num = object_num / obj_entity_num
    ratio_of_sub_entity_min = num_of_sub_entity_min / sub_entity_num
    ratio_of_obj_entity_min = num_of_obj_entity_min / obj_entity_num
    ratio_of_sub_triple_id_min = num_of_sub_triple_id_min / subject_num
    ratio_of_obj_triple_id_min = num_of_obj_triple_id_min / object_num

    print('second time check')
    print('max_threshold:', max_threshold, 'min_threshold:', min_threshold, 'sub2triple_threshold:',
          sub2triple_threshold, 'obj2triple_threshold:', obj2triple_threshold, 'second_min_threshold:',
          second_min_threshold, 'max_sub2entity_num:', max_sub2entity_num,
          'subject_max_triple_id:', subject_max_triple_id)
    print('triple_id num:', triple_id_num, 'subject_entity:', sub_entity_num, 'subject:', subject_num,
          'object_entity:', obj_entity_num, 'object:',
          object_num)  # entity_string only 1, if np_entity is different, then np is different
    print('different np subject_dict:', len(subject_dict), 'object_dict:', len(object_dict))
    print('sub_entity_min_num:', sub_entity_min_num, 'num_of_sub_entity_min:', num_of_sub_entity_min,
          'ratio_of_sub_entity_min:', ratio_of_sub_entity_min)
    print('obj_entity_min_num:', obj_entity_min_num, 'num_of_obj_entity_min:', num_of_obj_entity_min,
          'ratio_of_obj_entity_min:', ratio_of_obj_entity_min)
    print('sub_entity_ave_num:', sub_entity_ave_num, 'obj_entity_ave_num:', obj_entity_ave_num)
    print('sub_entity_max_num:', sub_entity_max_num, 'obj_entity_max_num:', obj_entity_max_num)
    print('sub2triple_id_min_num:', sub2triple_id_min_num, 'num_of_sub_triple_id_min:', num_of_sub_triple_id_min,
          'ratio_of_sub_triple_id_min:', ratio_of_sub_triple_id_min)
    print('obj2triple_id_min_num:', obj2triple_id_min_num, 'num_of_obj_triple_id_min:', num_of_obj_triple_id_min,
          'ratio_of_obj_triple_id_min:', ratio_of_obj_triple_id_min)
    print('sub2triple_id_ave_num:', sub2triple_id_ave_num, 'sub2triple_id_max_num:', sub2triple_id_max_num)
    print('obj2triple_id_ave_num:', obj2triple_id_ave_num, 'obj2triple_id_max_num:', obj2triple_id_max_num)
    print()
    print('ambiguous_num:', ambiguous_num)  # 219
    print('subject_num:', len(subject_dict))  # 2313
    print('ambiguous rate:', ambiguous_num / len(subject_dict))  # 0.094
    print('ambiguous_sub2entity_all_num:', ambiguous_sub2entity_ave_num)  # 583
    print('ambiguous_sub2entity_min_num:', ambiguous_sub2entity_min_num)  # 2
    print('ambiguous_sub2entity_ave_num:', ambiguous_sub2entity_ave_num / ambiguous_num)  # 2.662
    print('ambiguous_sub2entity_max_num:', ambiguous_sub2entity_max_num)  # 10
    print('ambiguous_triple_num:', len(ambiguous_triple_dict))  # 21287
    print('triple_id_num', triple_id_num)  # 64889
    print('ambiguous triple rate:', len(ambiguous_triple_dict) / triple_id_num)  # 0.328
    print('all_ambiguous_triple_num:', all_ambiguous_triple_num)
    print('assume_triple_num:', assume_triple_num)
    print('assume precision upbound:', 1 - (all_ambiguous_triple_num - assume_triple_num) / triple_id_num)
    print()
    if save:
        pickle.dump(triple_id_dict, open(filename_final_dataset_OPIEC, 'wb'))
else:
    print('load final dataset :', filename_final_dataset_OPIEC)
    triple_id_dict = pickle.load(open(filename_final_dataset_OPIEC, 'rb'))
    print('triple_id_dict:', len(triple_id_dict))
    subject_num, object_num, np_num = 0, 0, 0
    subject_dict, object_dict = dict(), dict()
    sub_entity2sub_list_dict, obj_entity2obj_list_dict = dict(), dict()
    sub2triple_id_list_dict, obj2triple_id_list_dict = dict(), dict()
    sub_entity_min_num, sub_entity_ave_num, sub_entity_max_num = 100000, 0, 0
    num_of_sub_entity_min, num_of_obj_entity_min = 0, 0
    obj_entity_min_num, obj_entity_ave_num, obj_entity_max_num = 100000, 0, 0
    sub2triple_id_min_num, sub2triple_id_ave_num, sub2triple_id_max_num = 100000, 0, 0
    obj2triple_id_min_num, obj2triple_id_ave_num, obj2triple_id_max_num = 100000, 0, 0
    num_of_sub_triple_id_min, num_of_obj_triple_id_min = 0, 0

    # for k in triple_id_dict.keys():
    #     v = triple_id_dict[k]
    #     triple_id_num += v
    triple_id_num = len(triple_id_dict)

    for triple_id in triple_id_dict:
        subject = triple_id2sub_dict[triple_id][0]
        object = triple_id2obj_dict[triple_id][0]
        sub_entity = triple_id2sub_entity_dict[triple_id][0]
        obj_entity = triple_id2obj_entity_dict[triple_id][0]
        if subject not in subject_dict:
            subject_dict.update({subject: [sub_entity]})
        else:
            if sub_entity not in subject_dict[subject]:
                subject_dict[subject].append(sub_entity)

        if sub_entity not in sub_entity2sub_list_dict:
            sub_entity2sub_list_dict.update({sub_entity: [subject]})
        else:
            if subject not in sub_entity2sub_list_dict[sub_entity]:
                sub_entity2sub_list_dict[sub_entity].append(subject)

        if subject not in sub2triple_id_list_dict:
            sub2triple_id_list_dict.update({subject: [triple_id]})
        else:
            if triple_id not in sub2triple_id_list_dict[subject]:
                sub2triple_id_list_dict[subject].append(triple_id)

        if object not in object_dict:
            object_dict.update({object: [obj_entity]})
        else:
            if obj_entity not in object_dict[object]:
                object_dict[object].append(obj_entity)

        if obj_entity not in obj_entity2obj_list_dict:
            obj_entity2obj_list_dict.update({obj_entity: [object]})
        else:
            obj_entity2obj_list_dict[obj_entity].append(object)

        if object not in obj2triple_id_list_dict:
            obj2triple_id_list_dict.update({object: [triple_id]})
        else:
            if triple_id not in obj2triple_id_list_dict[object]:
                obj2triple_id_list_dict[object].append(triple_id)

    ambiguous_num, ambiguous_triple_num = 0, 0
    ambiguous_sub2entity_min_num, ambiguous_sub2entity_ave_num, ambiguous_sub2entity_max_num = 100, 0, 0
    ambiguous_subject_dict, ambiguous_triple_dict = dict(), dict()
    for subject in subject_dict.keys():
        subject_num += len(subject_dict[subject])

        length = len(subject_dict[subject])
        if length > 1:
            if length < ambiguous_sub2entity_min_num:
                ambiguous_sub2entity_min_num = length
            if length > ambiguous_sub2entity_max_num:
                ambiguous_sub2entity_max_num = length
            ambiguous_sub2entity_ave_num += length
            if subject not in ambiguous_subject_dict:
                ambiguous_subject_dict.update({subject: 1})
            for triple_id in sub2triple_id_list_dict[subject]:
                if triple_id not in ambiguous_triple_dict:
                    ambiguous_triple_dict.update({triple_id: 1})
    ambiguous_num = len(ambiguous_subject_dict)

    ambiguous_sub2entity2freq_dict = dict()
    for triple_id in ambiguous_triple_dict:
        subject_list = triple_id2sub_dict[triple_id]
        triple_sub_entity_list = triple_id2sub_entity_dict[triple_id]
        for subject in subject_list:
            if subject in ambiguous_subject_dict:
                sub_entity_list = subject_dict[subject]
                for sub_entity in sub_entity_list:
                    for triple_sub_entity in triple_sub_entity_list:
                        if sub_entity == triple_sub_entity:
                            if subject not in ambiguous_sub2entity2freq_dict:
                                ambiguous_sub2entity2freq_dict.update({subject: {sub_entity: 1}})
                            else:
                                if sub_entity not in ambiguous_sub2entity2freq_dict[subject]:
                                    ambiguous_sub2entity2freq_dict[subject].update({sub_entity: 1})
                                else:
                                    ambiguous_sub2entity2freq_dict[subject][sub_entity] += 1
    # print('ambiguous_sub2entity2freq_dict:', len(ambiguous_sub2entity2freq_dict))

    all_ambiguous_triple_num, assume_triple_num = 0, 0
    for subject in ambiguous_sub2entity2freq_dict:
        entity_freq_dict = ambiguous_sub2entity2freq_dict[subject]
        most_freq_num, most_freq_entity = 0, str()
        for entity in entity_freq_dict:
            freq = entity_freq_dict[entity]
            all_ambiguous_triple_num += freq
            if freq > most_freq_num:
                most_freq_num = freq
                most_freq_entity = entity
        assert most_freq_num == entity_freq_dict[most_freq_entity]
        assume_triple_num += most_freq_num

    for object in object_dict.keys():
        object_num += len(object_dict[object])

    for sub_entity in sub_entity2sub_list_dict:
        sub_list = sub_entity2sub_list_dict[sub_entity]
        length = len(sub_list)
        if length < sub_entity_min_num:
            sub_entity_min_num = length
        if length > sub_entity_max_num:
            sub_entity_max_num = length

    for sub_entity in sub_entity2sub_list_dict:
        sub_list = sub_entity2sub_list_dict[sub_entity]
        length = len(sub_list)
        if length == sub_entity_min_num:
            num_of_sub_entity_min += 1

    for obj_entity in obj_entity2obj_list_dict:
        obj_list = obj_entity2obj_list_dict[obj_entity]
        length = len(obj_list)
        if length < obj_entity_min_num:
            obj_entity_min_num = length
        if length > obj_entity_max_num:
            obj_entity_max_num = length

    for obj_entity in obj_entity2obj_list_dict:
        obj_list = obj_entity2obj_list_dict[obj_entity]
        length = len(obj_list)
        if length == obj_entity_min_num:
            num_of_obj_entity_min += 1

    for subject in sub2triple_id_list_dict:
        subject_list = sub2triple_id_list_dict[subject]
        length = len(subject_list)
        if length < sub2triple_id_min_num:
            sub2triple_id_min_num = length
        if length > sub2triple_id_max_num:
            sub2triple_id_max_num = length

    for subject in sub2triple_id_list_dict:
        subject_list = sub2triple_id_list_dict[subject]
        length = len(subject_list)
        if length == sub2triple_id_min_num:
            num_of_sub_triple_id_min += 1

    for object in obj2triple_id_list_dict:
        object_list = obj2triple_id_list_dict[object]
        length = len(object_list)
        if length < obj2triple_id_min_num:
            obj2triple_id_min_num = length
        if length > obj2triple_id_max_num:
            obj2triple_id_max_num = length

    for object in obj2triple_id_list_dict:
        object_list = obj2triple_id_list_dict[object]
        length = len(object_list)
        if length == obj2triple_id_min_num:
            num_of_obj_triple_id_min += 1

    sub_entity_num = len(sub_entity2sub_list_dict)
    obj_entity_num = len(obj_entity2obj_list_dict)
    sub2triple_id_ave_num = triple_id_num / subject_num
    obj2triple_id_ave_num = triple_id_num / object_num
    sub_entity_ave_num = subject_num / sub_entity_num
    obj_entity_ave_num = object_num / obj_entity_num
    ratio_of_sub_entity_min = num_of_sub_entity_min / sub_entity_num
    ratio_of_obj_entity_min = num_of_obj_entity_min / obj_entity_num
    ratio_of_sub_triple_id_min = num_of_sub_triple_id_min / subject_num
    ratio_of_obj_triple_id_min = num_of_obj_triple_id_min / object_num

    print('second time check')
    print('max_threshold:', max_threshold, 'min_threshold:', min_threshold, 'sub2triple_threshold:',
          sub2triple_threshold, 'obj2triple_threshold:', obj2triple_threshold, 'second_min_threshold:',
          second_min_threshold, 'subject_max_triple_id:', subject_max_triple_id)
    print('triple_id num:', triple_id_num, 'subject_entity:', sub_entity_num, 'subject:', subject_num,
          'object_entity:', obj_entity_num, 'object:',
          object_num)  # entity_string only 1, if np_entity is different, then np is different
    print('different np subject_dict:', len(subject_dict), 'object_dict:', len(object_dict))
    print('sub_entity_min_num:', sub_entity_min_num, 'num_of_sub_entity_min:', num_of_sub_entity_min,
          'ratio_of_sub_entity_min:', ratio_of_sub_entity_min)
    print('obj_entity_min_num:', obj_entity_min_num, 'num_of_obj_entity_min:', num_of_obj_entity_min,
          'ratio_of_obj_entity_min:', ratio_of_obj_entity_min)
    print('sub_entity_ave_num:', sub_entity_ave_num, 'obj_entity_ave_num:', obj_entity_ave_num)
    print('sub_entity_max_num:', sub_entity_max_num, 'obj_entity_max_num:', obj_entity_max_num)
    print('sub2triple_id_min_num:', sub2triple_id_min_num, 'num_of_sub_triple_id_min:', num_of_sub_triple_id_min,
          'ratio_of_sub_triple_id_min:', ratio_of_sub_triple_id_min)
    print('obj2triple_id_min_num:', obj2triple_id_min_num, 'num_of_obj_triple_id_min:', num_of_obj_triple_id_min,
          'ratio_of_obj_triple_id_min:', ratio_of_obj_triple_id_min)
    print('sub2triple_id_ave_num:', sub2triple_id_ave_num, 'sub2triple_id_max_num:', sub2triple_id_max_num)
    print('obj2triple_id_ave_num:', obj2triple_id_ave_num, 'obj2triple_id_max_num:', obj2triple_id_max_num)
    print()
    print('ambiguous_num:', ambiguous_num)  # 219
    print('subject_num:', len(subject_dict))  # 2313
    print('ambiguous rate:', ambiguous_num / len(subject_dict))  # 0.094
    print('ambiguous_sub2entity_all_num:', ambiguous_sub2entity_ave_num)  # 583
    print('ambiguous_sub2entity_min_num:', ambiguous_sub2entity_min_num)  # 2
    print('ambiguous_sub2entity_ave_num:', ambiguous_sub2entity_ave_num / ambiguous_num)  # 2.662
    print('ambiguous_sub2entity_max_num:', ambiguous_sub2entity_max_num)  # 10
    print('ambiguous_triple_num:', len(ambiguous_triple_dict))  # 21287
    print('triple_id_num', triple_id_num)  # 64889
    print('ambiguous triple rate:', len(ambiguous_triple_dict) / triple_id_num)  # 0.328
    print('all_ambiguous_triple_num:', all_ambiguous_triple_num)
    print('assume_triple_num:', assume_triple_num)
    print('assume precision upbound:', 1 - (all_ambiguous_triple_num - assume_triple_num) / triple_id_num)
    print()
exit()
