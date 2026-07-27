# Required experiment data

这里只放不可由一次模型运行重新生成的输入，不放 `file/` 或 `output/` 中的缓存、嵌入、检查点和结果。

```text
data/
├── name_ambi/
│   └── OPIEC_name_ambi_triples   # OPIEC-Poly, pickle
├── ent_multi/
│   └── OPIEC_ent_multi_triples   # OPIEC-Syno, pickle
└── ent_link/
    ├── name_ambi_ent_link         # OPIEC-Poly entity-link evidence, pickle
    └── ent_multi_ent_link         # OPIEC-Syno entity-link evidence, pickle
```

最终基准 pickle 是 triple 字典列表。主模型使用的字段包括 `triple`、`triple_unique`、`subject_wiki_link` 和 `src_sentences`。

实体链接文件应使用数据发布包中的原始 pickle。运行生成的缓存、嵌入、检查点和结果应保存在 `file/` 或 `output/`，不要放入此目录。
