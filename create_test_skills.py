"""
创建测试技能验证目录检测假设
"""

import os
import shutil
from pathlib import Path

def create_test_skill_a():
    """创建测试技能A：5个目录，每个1个文件"""
    print("CREATING TEST SKILL A: 5 directories, 1 file each")
    print("-" * 50)
    
    test_dir = Path("D:/openclaw/test_skills/skill_a")
    
    # 清理旧目录
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True)
    
    # 创建目录结构
    dirs = ["module1", "module2", "module3", "module4", "module5"]
    
    for dir_name in dirs:
        dir_path = test_dir / dir_name
        dir_path.mkdir()
        
        # 创建Python文件
        py_file = dir_path / f"{dir_name}.py"
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(f'''"""
Module {dir_name}
"""

def function_{dir_name}():
    """Function in {dir_name}"""
    return "Hello from {dir_name}"
''')
        
        # 创建__init__.py
        init_file = dir_path / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'''"""
{dir_name} module
"""

from .{dir_name} import function_{dir_name}

__all__ = ['function_{dir_name}']
''')
    
    # 创建主skill.py
    skill_file = test_dir / "skill.py"
    with open(skill_file, 'w', encoding='utf-8') as f:
        f.write('''"""
Test Skill A
5 directories, 1 file each
"""

from module1 import function_module1
from module2 import function_module2
from module3 import function_module3
from module4 import function_module4
from module5 import function_module5

def main():
    """Main function"""
    results = [
        function_module1(),
        function_module2(),
        function_module3(),
        function_module4(),
        function_module5()
    ]
    return results

if __name__ == "__main__":
    print(main())
''')
    
    # 创建配置文件
    config_file = test_dir / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('''skill_id: test_skill_a
version: 1.0.0
description: Test skill with 5 directories
''')
    
    # 统计
    py_files = list(test_dir.rglob("*.py"))
    dirs_with_py = len(set(p.parent for p in py_files))
    
    print(f"Created: {test_dir}")
    print(f"Python files: {len(py_files)}")
    print(f"Directories with Python: {dirs_with_py}")
    print(f"Main directories: {len(dirs)}")
    
    return test_dir

def create_test_skill_b():
    """创建测试技能B：2个目录，每个多个文件"""
    print("\nCREATING TEST SKILL B: 2 directories, multiple files each")
    print("-" * 50)
    
    test_dir = Path("D:/openclaw/test_skills/skill_b")
    
    # 清理旧目录
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True)
    
    # 创建目录结构 - 只有2个目录
    dirs = ["core", "utils"]
    
    for dir_name in dirs:
        dir_path = test_dir / dir_name
        dir_path.mkdir()
        
        # 创建多个Python文件
        for i in range(1, 4):
            py_file = dir_path / f"{dir_name}_file{i}.py"
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(f'''"""
{dir_name} file {i}
"""

class {dir_name.capitalize()}Class{i}:
    """Class in {dir_name}"""
    
    def method_{i}(self):
        """Method {i}"""
        return "Method {i} from {dir_name}"
''')
        
        # 创建__init__.py
        init_file = dir_path / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'''"""
{dir_name} module
"""

from .{dir_name}_file1 import {dir_name.capitalize()}Class1
from .{dir_name}_file2 import {dir_name.capitalize()}Class2
from .{dir_name}_file3 import {dir_name.capitalize()}Class3

__all__ = [
    '{dir_name.capitalize()}Class1',
    '{dir_name.capitalize()}Class2', 
    '{dir_name.capitalize()}Class3'
]
''')
    
    # 创建主skill.py
    skill_file = test_dir / "skill.py"
    with open(skill_file, 'w', encoding='utf-8') as f:
        f.write('''"""
Test Skill B
2 directories, multiple files each
"""

from core import CoreClass1, CoreClass2, CoreClass3
from utils import UtilsClass1, UtilsClass2, UtilsClass3

def main():
    """Main function"""
    core_obj = CoreClass1()
    utils_obj = UtilsClass1()
    
    return {
        'core': core_obj.method_1(),
        'utils': utils_obj.method_1()
    }

if __name__ == "__main__":
    print(main())
''')
    
    # 创建配置文件
    config_file = test_dir / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('''skill_id: test_skill_b
version: 1.0.0
description: Test skill with 2 directories
''')
    
    # 统计
    py_files = list(test_dir.rglob("*.py"))
    dirs_with_py = len(set(p.parent for p in py_files))
    
    print(f"Created: {test_dir}")
    print(f"Python files: {len(py_files)}")
    print(f"Directories with Python: {dirs_with_py}")
    print(f"Main directories: {len(dirs)}")
    
    return test_dir

def create_test_skill_c():
    """创建测试技能C：扁平结构，所有文件在根目录"""
    print("\nCREATING TEST SKILL C: Flat structure, all files in root")
    print("-" * 50)
    
    test_dir = Path("D:/openclaw/test_skills/skill_c")
    
    # 清理旧目录
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True)
    
    # 创建多个Python文件在根目录
    for i in range(1, 6):
        py_file = test_dir / f"module{i}.py"
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(f'''"""
Module {i}
"""

def function_{i}():
    """Function {i}"""
    return "Function {i}"
''')
    
    # 创建主skill.py
    skill_file = test_dir / "skill.py"
    with open(skill_file, 'w', encoding='utf-8') as f:
        f.write('''"""
Test Skill C
Flat structure, all files in root
"""

from module1 import function_1
from module2 import function_2
from module3 import function_3
from module4 import function_4
from module5 import function_5

def main():
    """Main function"""
    return [
        function_1(),
        function_2(),
        function_3(),
        function_4(),
        function_5()
    ]

if __name__ == "__main__":
    print(main())
''')
    
    # 创建配置文件
    config_file = test_dir / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('''skill_id: test_skill_c
version: 1.0.0
description: Test skill with flat structure
''')
    
    # 统计
    py_files = list(test_dir.rglob("*.py"))
    dirs_with_py = len(set(p.parent for p in py_files))
    
    print(f"Created: {test_dir}")
    print(f"Python files: {len(py_files)}")
    print(f"Directories with Python: {dirs_with_py}")
    print(f"Main directories: 1 (root only)")
    
    return test_dir

def main():
    """主创建函数"""
    print("CREATING TEST SKILLS FOR ALGORITHM VALIDATION")
    print("=" * 70)
    
    print("\nTest design:")
    print("Skill A: 5 directories, 1 file each (5 modules by directory)")
    print("Skill B: 2 directories, multiple files each (2 modules by directory)")
    print("Skill C: Flat structure, all files in root (1 module by directory)")
    
    print("\nHypothesis:")
    print("If algorithm counts directories as modules:")
    print("  Skill A: ~5 modules → lower density → lower confidence")
    print("  Skill B: ~2 modules → higher density → higher confidence")
    print("  Skill C: 1 module → highest density → highest confidence")
    
    skill_a = create_test_skill_a()
    skill_b = create_test_skill_b()
    skill_c = create_test_skill_c()
    
    print("\n" + "=" * 70)
    print("TEST SKILLS CREATED - READY FOR AUDIT")
    print("=" * 70)
    
    print("\nNext steps:")
    print("1. Run mathematical audit on all test skills")
    print("2. Compare matrix confidence results")
    print("3. Validate directory-based module hypothesis")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)