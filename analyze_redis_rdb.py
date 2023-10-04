import re
import sys
from collections import defaultdict
import csv


csv_file = "/var/lib/mysql-files/memory.csv"
items = []
with open(csv_file) as f:
    for row in csv.reader(f, skipinitialspace=True):
        items.append(row)

size_dict = defaultdict(dict)
user_id_pattern = r"(?<!\d|/|-|\.|,)\d{1,}(?:\.\d{,2})?(?!\d|/|-|\.|,|:)"
for row in items[1:]:
    key_name = row[2]
    size_in_bytes = row[3]

    pre_key = key_name
    user_id = ""
    re.findall(r"(?<!\d|/|-|\.|,)\d{1,}(?:\.\d{,2})?(?!\d|/|-|\.|,|:)", key_name)

    for num in re.findall(user_id_pattern, key_name):
        user_id = num
        break
    if user_id:
        pre_key = key_name.replace(user_id, "*")
    size_dict[pre_key]["count"] = size_dict[pre_key].get("count", 0) + 1
    size_dict[pre_key]["sizes"] = size_dict[pre_key].get("sizes", 0) + int(size_in_bytes)
    size_dict[pre_key]["max_size"] = max(size_dict[pre_key].get("max_size", 0), int(size_in_bytes))
    size_dict[pre_key]["min_size"] = min(size_dict[pre_key].get("min_size", sys.maxsize), int(size_in_bytes))


for item in sorted(size_dict.items(), key=lambda x:x[1]["sizes"]):
    print(item)
