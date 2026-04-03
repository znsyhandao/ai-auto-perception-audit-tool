"""
合并深度分析服务文件
"""

import os

# 读取两个文件
with open("microservices/deep-analysis-service/main.py", "r", encoding="utf-8") as f:
    part1 = f.read()

with open("microservices/deep-analysis-service/main_continued.py", "r", encoding="utf-8") as f:
    part2 = f.read()

# 合并
full_content = part1 + part2

# 写入完整文件
with open("microservices/deep-analysis-service/main.py", "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"Merged file size: {len(full_content)} bytes")

# 删除临时文件
os.remove("microservices/deep-analysis-service/main_continued.py")

print("Files merged successfully!")