# filtration 1 1 np to many entity
# not in multi_entity_triple_id_dict is ok
from avro.datafile import DataFileReader
from avro.io import DatumReader
import numpy as np
import pathlib
import pickle
import pdb
import time
import os

output_dir = '../file/first_filtration'
os.makedirs(output_dir, exist_ok=True)
triple_num = 0
AVRO_SCHEMA_FILE = "../OPIEC-master/avroschema/TripleLinked.avsc"
AVRO_FILE_PART = "../OPIEC-Linked/OPIEC-Linked-triples/part-r-0"
FILE_PART = str()
SUFFIX = ".avro"
multi_entity_triple_id_list = []
filename = output_dir + '/multi_entity_triple_id_list'
# if not pathlib.Path(filename).is_file():
if not pathlib.Path(filename).is_file():
    for FILE_NUM in range(7789):
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
            # for k in triple.keys():
            #     print('keys:', type(k), k)
            #     print('values:', type(triple[k]), triple[k])
            #     print()
            # exit()
            triple_num += 1
            triple_id = triple['triple_id']
            sub = triple['subject']
            rel = triple['relation']
            obj = triple['object']
            triple_list = [sub, obj]
            for i in range(len(triple_list)):
                NP = triple_list[i]
                entity_list = []
                for NP_word in NP:
                    wiki_link = NP_word['w_link']['wiki_link']
                    if len(wiki_link) > 0:
                        entity_list.append(wiki_link)
                if len(entity_list) == len(NP):  # every NP_word has a non-empty entity
                    unique_entity_list = np.unique(entity_list)
                    if len(unique_entity_list) > 1:
                        # print('triple_num:', triple_num)
                        # print('not same:', 'unique_entity_list:', unique_entity_list)
                        # print('entity_list:', entity_list)
                        multi_entity_triple_id_list.append(triple_id)
                        # exit()
        reader.close()
    pickle.dump(multi_entity_triple_id_list, open(filename, 'wb'))
else:
    print('load multi_entity_triple_id list')
    multi_entity_triple_id_list = pickle.load(open(filename, 'rb'))
print('ok! All is same ')
print('triple_num:', triple_num)  # 5819752
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print('multi_entity_triple_id_list:', type(multi_entity_triple_id_list), len(multi_entity_triple_id_list))  # 1997

filename = output_dir + '/multi_entity_triple_id_dict'
multi_entity_triple_id_dict = dict()
if not pathlib.Path(filename).is_file():
    for i in range(len(multi_entity_triple_id_list)):
        meti = multi_entity_triple_id_list[i]
        print('i:', i, 'meti:', type(meti), meti)
        if meti not in multi_entity_triple_id_dict.keys():
            multi_entity_triple_id_dict.update({meti: 1})
    pickle.dump(multi_entity_triple_id_dict, open(filename, 'wb'))
else:
    print('load multi_entity_triple_id dict')
    multi_entity_triple_id_dict = pickle.load(open(filename, 'rb'))

print('len(multi_entity_triple_id_dict)', len(multi_entity_triple_id_dict))  # 1985
print('len(multi_entity_triple_id_list)', len(multi_entity_triple_id_list))  # 1997
print('len(multi_entity_triple_id_list):', len(list(set(multi_entity_triple_id_list))))  # 1985
assert len(multi_entity_triple_id_dict) == len(list(set(multi_entity_triple_id_list)))
for i in multi_entity_triple_id_dict.keys():
    print('i:', i)
print('multi_entity_triple_id_dict:', type(multi_entity_triple_id_dict), len(multi_entity_triple_id_dict))  # <class 'dict'> 1985
print('triple_num:', triple_num)  # 5819752
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# for k in triple.keys():
#     print('keys:', type(k), k)
#     print('values:', type(triple[k]), triple[k])
#     print()
# use triple.keys() to see every field in the schema (it's a dictionary)
# pdb.set_trace()
