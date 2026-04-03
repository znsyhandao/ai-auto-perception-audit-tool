#!/usr/bin/env python3
"""查找编码有问题的文件"""

from pathlib import Path

skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")

# 检查所有文件
all_files = list(skill_path.rglob("*"))

bad_files = []

for file_path in all_files:
    if file_path.is_file():
        # 跳过二进制文件
        if file_path.suffix in ['.pyc', '.png', '.jpg', '.jpeg', '.gif', '.zip']:
            continue
        
        try:
            # 尝试读取
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)  # 只读前100字符
        except UnicodeDecodeError as e:
            bad_files.append((file_path, e))
        except Exception as e:
            # 可能是二进制文件
            pass

print(f"检查了 {len(all_files)} 个文件")
print(f"发现 {len(bad_files)} 个编码问题")

if bad_files:
    print("\n有问题的文件:")
    for file_path, error in bad_files:
        print(f"\n{file_path.relative_to(skill_path)}:")
        print(f"  错误: {error}")
        
        # 尝试用二进制读取看看是什么
        try:
            with open(file_path, 'rb') as f:
                first_bytes = f.read(20)
                print(f"  前20字节: {first_bytes}")
        except:
            pass