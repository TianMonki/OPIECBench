#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy

from transformers import logging

logging.set_verbosity_warning()
import time
from random import sample
import torch
import torch.nn as nn
from torch import optim
import math
from transformers import BertTokenizer, BertModel

device = torch.device(f"cuda:1" if torch.cuda.is_available() else "cpu")

class InfoNCELoss(nn.Module):
    def __init__(self, temperature=0.07):
        super(InfoNCELoss, self).__init__()
        self.temperature = temperature
        self.cosine_similarity = nn.CosineSimilarity(dim=-1)

    def forward(self, outputs, labels):
        # batch_len = outputs.shape[0]
        # outputs = outputs.view(batch_len, -1, outputs.shape[-1])  # (batch_size, 2 + neg, hidden_dim)
        # 取正样本
        outputs_pos = outputs[:, 0, :] # (batch_size, hidden_dim)
        # 取所有样本（包括正负样本）
        outputs_all = outputs[:, 1:, :]  # (batch_size, neg_samples, hidden_dim)

        # 计算相似度
        pos_sim = self.cosine_similarity(outputs_pos.unsqueeze(1), outputs_all) / self.temperature
        # labels = torch.zeros(batch_len, dtype=torch.long).to(device)  # 正样本标签为0

        # 计算InfoNCE损失
        loss = nn.functional.cross_entropy(pos_sim, labels)

        return loss

class BertEmbeddingModel(nn.Module):
    def __init__(self, max_length, target_dim):
        super(BertEmbeddingModel, self).__init__()
        self.max_length = max_length
        self.target_dim = target_dim
        self.tokenizer = BertTokenizer.from_pretrained('../plm/unsup-simcse-bert-base-uncased')
        self.bert = BertModel.from_pretrained('../plm/unsup-simcse-bert-base-uncased')
        self.bert = self.bert.to(device)
        self.tokenizer.add_tokens(['[TRI]'])
        self.bert.resize_token_embeddings(len(self.tokenizer))
        self.dense = nn.Linear(768, target_dim).to(device)

    def forward(self, sample):
        batch_tokenized = self.tokenizer.batch_encode_plus(sample, return_tensors='pt', truncation=True, padding=True,
                                                           max_length=self.max_length)
        # input_ids = torch.tensor(batch_tokenized['input_ids']).to(device)
        inputs = {k: v.to(device) for k, v in batch_tokenized.items()}
        # outputs = self.dense(self.bert(**inputs).last_hidden_state[:, 0, :])
        outputs = self.bert(**inputs).last_hidden_state[:, 0, :]
        # embedding = outputs.detach().cpu().numpy()
        return outputs

        # attention_mask = torch.tensor(batch_tokenized['attention_mask']).to(device)
        # bert_output = self.bert(input_ids, attention_mask=attention_mask)
        # bert_cls_hidden_state = bert_output[0][:, 0, :]
        # # linear_output = self.dense(bert_cls_hidden_state)
        # # return bert_cls_hidden_state, linear_output
        # return bert_cls_hidden_state

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = self.bert(**inputs)[0][:, 0, :]
        # outputs = self.dense(outputs)
        embedding = outputs.detach().cpu().numpy()
        return embedding


class Bert_Model(object):
    def __init__(self, params, side_info):
        self.p = params
        self.side_info = side_info
        self.batch_size = 4
        self.negative_sample_size = 5
        self.epochs = 10
        # self.lr = 0.005
        self.lr = 1e-3
        self.max_length = 512
        self.bert_embedding_model = BertEmbeddingModel(self.max_length, target_dim=768).to(device)

    def encode_list(self, input):
        linear_outputs = []

        train_triples = input
        batch_count = math.ceil(len(train_triples) / self.batch_size)
        print('batch_count:', batch_count)
        batch_triple = []
        for i in range(batch_count):
            batch_triple.append(train_triples[i * self.batch_size:(i + 1) * self.batch_size])

        with torch.no_grad():
            for i in range(batch_count):
                # bert_cls_hidden_state, linear_output = bert_embedding_model(batch_triple[i])
                # for op in linear_output.cpu().numpy():
                #     linear_outputs.append(op)
                linear_output = self.bert_embedding_model(batch_triple[i])
                for op in linear_output.cpu().numpy():
                    linear_outputs.append(op)
        print("Primary Context View Embedding")
        return linear_outputs

    def encode(self, input_dict):
        output_dict = copy.deepcopy(input_dict)
        with torch.no_grad():
            for key, val in input_dict.items():
                for sub_k, sub_v in val.items():
                    output_dict[key][sub_k] = self.bert_embedding_model.get_embedding(sub_v)
        return output_dict

    def encode_op_list(self, input_dict):
        output_dict = dict()
        with torch.no_grad():
            for key, val in input_dict.items():
                output_dict[key] = []
                for sub_v in val:
                    embed_list = []
                    for ss_v in sub_v:
                        embed = self.bert_embedding_model.get_embedding(ss_v)
                        embed_list.append(embed)
                    output_dict[key].append(embed_list)
        return output_dict

    def load_state(self, iter):
        self.bert_embedding_model.load_state_dict(torch.load('../file/' + self.p.dataset + '_test/multi_view/semantic_view_' + str(iter) +'/biencoder.pth'))

    # def fine_tune
    def fine_tune(self, seed_list_cano, seed_pair_lk, triple_list, ent_link_desc, tri_same_cls_id, tri_link_res, iter, high_tri_id):
        new_ent_link_des = {}
        for outer_key, inner_dict in ent_link_desc.items():
            new_ent_link_des.update(inner_dict)
        samples = []

        seed_set = set(seed_list_cano)
        high_indices = set(high_tri_id)

        for seed_pair in seed_list_cano:
            np1, np2, ent, id1, id2 = seed_pair
            cct_tri = triple_list[id1]
            cct_tri_pos = triple_list[id2]
            samples.append(cct_tri)
            samples.append(cct_tri_pos)
            all_tri_sample = high_indices - {id1, id2}
            negative_sample_part = set(tri_same_cls_id[id1])
            if np1 != np2:
                negative_sample_part.update(tri_same_cls_id[id2])
            # available_samples = all_tri_sample & negative_sample_part
            available_samples = negative_sample_part - high_indices
            valid_samples = []
            for ns in available_samples:
                if (np1, np2, ent, id1, ns) not in seed_set and tri_link_res[ns][0][0] != tri_link_res[id1][0][0]:
                    valid_samples.append(ns)
            if len(valid_samples) >= self.negative_sample_size:
                negative_sample = sample(valid_samples, self.negative_sample_size)
                negative_sample_list = negative_sample
            else:
                negative_sample_list = list(valid_samples)
                remain = self.negative_sample_size - len(negative_sample_list)
                other_samples = []
                for ns in (all_tri_sample - set(valid_samples)):
                    if (np1, np2, ent, id1, ns) not in seed_set and tri_link_res[ns][0][0] != tri_link_res[id1][0][0]:
                        other_samples.append(ns)
                addition_samples = sample(other_samples, remain)
                negative_sample_list.extend(addition_samples)

            for j in negative_sample_list:
                samples.append(triple_list[j])

        new_ent_keys = set(new_ent_link_des.keys())
        for seed_pair in seed_pair_lk:
            np, x, id = seed_pair
            cct_tri = triple_list[id]
            pos_ent_desc = ent_link_desc[np][x]
            samples.append(cct_tri)
            samples.append(pos_ent_desc)
            # negative_sample_list = []
            # negative_sample_num = 0
            cand_ent_desc = ent_link_desc[np]
            cand_keys = set(cand_ent_desc.keys())
            cand_neg = cand_keys - {x}
            if len(cand_neg) >= self.negative_sample_size:
                # while negative_sample_num < self.negative_sample_size:
                negative_sample = sample(list(cand_neg), self.negative_sample_size)
            else:
                remaining = self.negative_sample_size - len(cand_neg)
                other_keys = new_ent_keys - cand_keys
                addtion = sample(list(other_keys), remaining)
                negative_sample = list(cand_neg) + addtion
                # negative_sample_part = list(cand_ent_desc.keys())
                # negative_sample_part.remove(x)
                # negative_sample_num = self.negative_sample_size - len(negative_sample_part)
                # negative_sample = sample([i for i in list(new_ent_link_des.keys()) if i not in list(cand_ent_desc.keys())],
                #     negative_sample_num) + negative_sample_part
            for j in negative_sample:
                samples.append(new_ent_link_des[j])

        seed_len = len(seed_list_cano) + len(seed_pair_lk)
        batch_count = math.ceil(seed_len / self.batch_size)
        print('batch_count:', batch_count)

        batch_train_inputs, batch_train_targets = [], []
        for i in range(batch_count):
            batch_train_inputs.append(samples[i * self.batch_size * (2 + self.negative_sample_size):
                                              (i + 1) * self.batch_size * (2 + self.negative_sample_size)])
        optimizer = optim.SGD(self.bert_embedding_model.parameters(), lr=self.lr)
        criterion = InfoNCELoss()

        for epoch in range(self.epochs):
            avg_epoch_loss = 0
            for i in range(batch_count):
                inputs = batch_train_inputs[i]
                batch_len = int(len(inputs) / (2 + self.negative_sample_size))
                labels = torch.zeros(batch_len, dtype=torch.int64).to(device)
                outputs = self.bert_embedding_model(inputs)
                outputs = outputs.view(batch_len, (2 + self.negative_sample_size), 768)
                # outputs_pos = outputs[:, 0, :].unsqueeze(2)
                # outputs_neg = outputs[:, 1:, :]
                # logits = torch.matmul(outputs_neg, outputs_pos).squeeze(-1)
                # pos_logits = torch.matmul(outputs[:, 0, :].unsqueeze(1), outputs[:, 1, :].unsqueeze(2)).squeeze(-1)
                # neg_logits = torch.matmul(outputs[:, 0, :].unsqueeze(1), outputs[:, 2:, :].transpose(1, 2)).squeeze(1)
                # pos_logits = pos_logits
                # logits = torch.cat([pos_logits, neg_logits], dim=1)
                loss = criterion(outputs, labels)
                # early-stop

                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.bert_embedding_model.parameters(), 1.0)
                optimizer.step()
                avg_epoch_loss += loss.item()
                if i == (batch_count - 1):
                    real_time = time.strftime("%Y_%m_%d") + ' ' + time.strftime("%H:%M:%S")
                    print(real_time, "Epoch: %d, Loss: %.4f" % (epoch, avg_epoch_loss))

            # early_stopping(avg_epoch_loss)
            # if early_stopping.early_stop:
            #     break

        torch.save(self.bert_embedding_model.state_dict(),
                   '../file/' + self.p.dataset + '_test/multi_view/semantic_view_' + str(iter) +'/biencoder.pth')
