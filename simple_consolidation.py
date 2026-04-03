"""
简化版模块合并
"""

import os
import shutil
from pathlib import Path

def main():
    print("SIMPLE MODULE CONSOLIDATION FOR v2.1")
    print("=" * 70)
    
    base_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    
    print("\n1. Current module count before consolidation:")
    py_files = list(base_dir.rglob("*.py"))
    print(f"   Python files: {len(py_files)}")
    
    print("\n2. Creating consolidated utilities module...")
    
    # 创建合并的utilities.py
    utils_dir = base_dir / "utils"
    utilities_file = utils_dir / "utilities.py"
    
    utilities_content = '''"""
Consolidated Utilities
"""
import yaml
import logging

class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.config_data = {}
    
    def load_config(self):
        if self.config_path and self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
        return self.config_data
    
    def get(self, key, default=None):
        return self.config_data.get(key, default)

def setup_logger(name='aisleepgen', level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

class SecurityValidator:
    def validate_path(self, path, allowed_dirs=None):
        from pathlib import Path
        path_obj = Path(path).resolve()
        if allowed_dirs:
            for allowed_dir in allowed_dirs:
                allowed_path = Path(allowed_dir).resolve()
                try:
                    path_obj.relative_to(allowed_path)
                    return True
                except ValueError:
                    continue
        return False
    
    def validate_input(self, input_data, max_length=1000):
        if not isinstance(input_data, str):
            return False
        if len(input_data) > max_length:
            return False
        dangerous = [';', '&&', '||', '`', '$(']
        for pattern in dangerous:
            if pattern in input_data:
                return False
        return True
'''
    
    utilities_file.parent.mkdir(parents=True, exist_ok=True)
    with open(utilities_file, 'w', encoding='utf-8') as f:
        f.write(utilities_content)
    
    print(f"   Created: {utilities_file}")
    
    # 删除旧的工具模块目录
    old_utils_dirs = ["configuration", "logging", "security"]
    for dir_name in old_utils_dirs:
        old_dir = utils_dir / dir_name
        if old_dir.exists():
            shutil.rmtree(old_dir)
            print(f"   Removed: {old_dir}")
    
    # 更新utils/__init__.py
    utils_init = utils_dir / "__init__.py"
    with open(utils_init, 'w', encoding='utf-8') as f:
        f.write('''"""
Utilities module
"""
from .utilities import ConfigManager, setup_logger, SecurityValidator
__all__ = ['ConfigManager', 'setup_logger', 'SecurityValidator']
''')
    
    print(f"   Updated: {utils_init}")
    
    print("\n3. Creating consolidated data processor module...")
    
    # 创建合并的data_processor.py
    data_dir = base_dir / "data"
    data_processor_file = data_dir / "data_processor.py"
    
    data_processor_content = '''"""
Consolidated Data Processor
"""
import json
import numpy as np
from pathlib import Path

class DataValidator:
    def validate_edf_file(self, file_path):
        path = Path(file_path)
        if not path.exists():
            return False, "File does not exist"
        if path.suffix.lower() != '.edf':
            return False, "Not an EDF file"
        try:
            with open(path, 'rb') as f:
                header = f.read(256)
                if len(header) < 256:
                    return False, "Invalid EDF header"
            return True, "Valid EDF file"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def validate_json_data(self, json_data):
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            if not isinstance(data, dict):
                return False, "Data must be a dictionary"
            return True, "Valid JSON data"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

class FileReader:
    def read_text_file(self, file_path, encoding='utf-8'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file: {str(e)}")
    
    def read_json_file(self, file_path):
        content = self.read_text_file(file_path)
        return json.loads(content)

class StatisticsCalculator:
    def calculate_basic_stats(self, data):
        if not data:
            return {}
        data_array = np.array(data)
        return {
            'count': len(data),
            'mean': float(np.mean(data_array)),
            'std': float(np.std(data_array)),
            'min': float(np.min(data_array)),
            'max': float(np.max(data_array)),
            'median': float(np.median(data_array))
        }
    
    def calculate_hrv_metrics(self, rr_intervals):
        if not rr_intervals or len(rr_intervals) < 2:
            return {}
        rr_array = np.array(rr_intervals)
        return {
            'mean_rr': float(np.mean(rr_array)),
            'sdnn': float(np.std(rr_array)),
            'rmssd': float(np.sqrt(np.mean(np.diff(rr_array) ** 2))),
            'nn50': int(np.sum(np.abs(np.diff(rr_array)) > 50)),
            'pnn50': float(np.sum(np.abs(np.diff(rr_array)) > 50) / len(rr_array) * 100)
        }
'''
    
    data_processor_file.parent.mkdir(parents=True, exist_ok=True)
    with open(data_processor_file, 'w', encoding='utf-8') as f:
        f.write(data_processor_content)
    
    print(f"   Created: {data_processor_file}")
    
    # 删除旧的数据模块目录
    old_data_dirs = ["data_validator", "file_reader", "statistics"]
    for dir_name in old_data_dirs:
        old_dir = data_dir / dir_name
        if old_dir.exists():
            shutil.rmtree(old_dir)
            print(f"   Removed: {old_dir}")
    
    # 更新data/__init__.py
    data_init = data_dir / "__init__.py"
    with open(data_init, 'w', encoding='utf-8') as f:
        f.write('''"""
Data processing module
"""
from .data_processor import DataValidator, FileReader, StatisticsCalculator
__all__ = ['DataValidator', 'FileReader', 'StatisticsCalculator']
''')
    
    print(f"   Updated: {data_init}")
    
    print("\n4. Updating skill.py imports...")
    
    skill_file = base_dir / "skill.py"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换导入
        old_imports = [
            "from utils.configuration.config import ConfigManager",
            "from utils.logging.logger import setup_logger", 
            "from utils.security.validator import SecurityValidator",
            "from data.data_validator.validator import DataValidator",
            "from data.file_reader.reader import FileReader",
            "from data.statistics.calculator import StatisticsCalculator"
        ]
        
        for old_import in old_imports:
            content = content.replace(old_import, "")
        
        # 添加新的导入
        new_imports = '''from utils.utilities import ConfigManager, setup_logger, SecurityValidator
from data.data_processor import DataValidator, FileReader, StatisticsCalculator'''
        
        # 在import部分插入
        lines = content.split('\n')
        new_lines = []
        imports_added = False
        
        for line in lines:
            if line.startswith('import ') or line.startswith('from '):
                if not imports_added:
                    new_lines.append(new_imports)
                    imports_added = True
                continue
            new_lines.append(line)
        
        if not imports_added:
            new_lines = [new_imports] + new_lines
        
        updated_content = '\n'.join(new_lines)
        
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"   Updated: {skill_file}")
    else:
        print(f"   ERROR: skill.py not found")
    
    print("\n5. Verification...")
    
    # 检查模块数量
    py_files_after = list(base_dir.rglob("*.py"))
    print(f"   Python files after consolidation: {len(py_files_after)}")
    print(f"   Reduction: {len(py_files) - len(py_files_after)} modules")
    
    # 检查关键文件
    required_files = [
        base_dir / "skill.py",
        base_dir / "utils" / "utilities.py",
        base_dir / "data" / "data_processor.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"   OK: {file_path.relative_to(base_dir)}")
        else:
            print(f"   MISSING: {file_path.relative_to(base_dir)}")
            all_exist = False
    
    if all_exist:
        print("\nCONSOLIDATION COMPLETE!")
        print(f"Modules reduced from {len(py_files)} to {len(py_files_after)}")
        print("Next: Run dependency analysis and mathematical audit")
    else:
        print("\nCONSOLIDATION INCOMPLETE - check missing files")
    
    return all_exist

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)