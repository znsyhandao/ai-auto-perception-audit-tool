#!/usr/bin/env python3
"""
创建测试文件
"""

import os
import sys

def create_test_files(test_dir):
    """创建测试文件"""
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"Created test directory: {test_dir}")
    
    # 1. 创建有问题的测试文件
    problematic_code = '''# test_problematic.py
# 包含各种问题的测试文件

import os
import sys
import pickle  # 危险导入
import marshal  # 危险导入

def infinite_loop():
    while True:  # 无限循环
        pass

def unreachable_code():
    return 42
    print("This is unreachable")  # 不可达代码

def dangerous_function():
    # 危险函数调用
    eval("print('dangerous')")
    exec("x = 1")
    os.system("dir")  # 系统命令
    
def sensitive_data():
    password = "secret123"  # 敏感数据
    api_key = "sk_test_123456"
    return password + api_key

def inefficient_algorithm():
    # 低效算法
    result = []
    for i in range(100):
        for j in range(100):
            for k in range(100):  # 三层嵌套循环
                result.append(i + j + k)
    return result

def unvalidated_input(user_input):
    # 未验证的输入
    return eval(user_input)  # 直接执行用户输入

def resource_leak():
    # 资源泄漏
    f = open("test.txt", "w")
    # 忘记关闭文件
    f.write("test")
    # 应该有关闭: f.close()

class TestClass:
    def __init__(self):
        self.data = "test"
    
    def complex_method(self):
        # 高复杂度方法
        if True:
            if False:
                for i in range(10):
                    while True:
                        try:
                            pass
                        except:
                            pass
        return self.data
'''
    
    test_file = os.path.join(test_dir, "test_problematic.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(problematic_code)
    print(f"Created problematic test file: {test_file}")
    
    # 2. 创建干净的测试文件
    clean_code = '''# test_clean.py
# 干净的测试文件

import json
import math

def calculate_statistics(data):
    """计算统计数据"""
    if not data:
        return {}
    
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = math.sqrt(variance)
    
    return {
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "count": len(data)
    }

def process_data_safely(data):
    """安全处理数据"""
    try:
        parsed = json.loads(data)
        return calculate_statistics(parsed.get("values", []))
    except Exception as e:
        return {"error": str(e)}

def main():
    """主函数"""
    test_data = '{"values": [1.0, 2.0, 3.0, 4.0, 5.0]}'
    result = process_data_safely(test_data)
    print("Result: {}".format(result))
    
    # 正确的资源管理
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
'''
    
    clean_file = os.path.join(test_dir, "test_clean.py")
    with open(clean_file, 'w', encoding='utf-8') as f:
        f.write(clean_code)
    print(f"Created clean test file: {clean_file}")
    
    # 3. 创建requirements.txt
    requirements = '''# requirements.txt
json==1.0.0
typing-extensions==4.0.0
'''
    
    req_file = os.path.join(test_dir, "requirements.txt")
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write(requirements)
    print(f"Created requirements.txt: {req_file}")
    
    return {
        'problematic': test_file,
        'clean': clean_file,
        'requirements': req_file
    }

if __name__ == "__main__":
    test_dir = "./test_data"
    files = create_test_files(test_dir)
    print(f"\nTest files created successfully!")
    print(f"Problematic file: {files['problematic']}")
    print(f"Clean file: {files['clean']}")
    print(f"Requirements file: {files['requirements']}")