# Local pretrained language model

放置 Hugging Face 兼容的本地模型目录：

```text
plm/unsup-simcse-bert-base-uncased/
```

目录应同时包含 tokenizer 与 BERT 配置/权重文件。`code_main/model_Bert.py` 使用 `from_pretrained()` 从该本地目录加载，运行时不会自动下载。
