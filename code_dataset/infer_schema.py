import hashlib
import json
from collections import defaultdict


# 用于生成唯一的嵌套类型名
def get_unique_name(path):
    hash_suffix = hashlib.md5(path.encode()).hexdigest()[:8]
    return f"Nested_{hash_suffix}"


# 递归推断Avro类型，包括支持联合类型（union）和数组元素的多类型支持
def infer_avro_type(value, path="root"):
    if isinstance(value, dict):
        fields = []
        for key, val in value.items():
            sub_path = f"{path}_{key}"
            field_type = infer_avro_type(val, sub_path)
            fields.append({"name": key, "type": field_type})
        return {
            "type": "record",
            "name": get_unique_name(path),
            "fields": fields
        }

    elif isinstance(value, list):
        if not value:
            return {"type": "array", "items": "null"}

        # 获取数组中的所有类型
        item_types = set()
        for item in value:
            item_types.add(json.dumps(infer_avro_type(item, path + "_item"), sort_keys=True))  # 使用json.dumps生成一个可哈希的字符串

        if len(item_types) == 1:
            return {"type": "array", "items": json.loads(item_types.pop())}
        else:
            return {"type": "array", "items": [json.loads(item) for item in item_types]}

    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "long"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, str):
        return "string"
    elif value is None:
        return "null"
    else:
        return "string"


# 处理所有字典的合并逻辑
def merge_data(data):
    merged = defaultdict(lambda: None)
    for entry in data:
        for k, v in entry.items():
            if k not in merged or merged[k] is None:
                merged[k] = v
    return merged


# 生成Avro schema
def generate_avro_schema(data):
    merged_data = merge_data(data)
    avro_schema = {}

    for key, value in merged_data.items():
        avro_schema[key] = infer_avro_type(value, key)

    return avro_schema


# 保存为文件
def save_schema_to_file(schema, filename="schema.avsc"):
    with open(filename, "w") as f:
        json.dump(schema, f, indent=2)
