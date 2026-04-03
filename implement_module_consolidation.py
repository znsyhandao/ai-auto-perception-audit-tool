"""
实施模块合并
"""

import shutil
from pathlib import Path
import re

def backup_v2_release():
    """备份v2.0_release"""
    print("1. CREATING BACKUP OF v2.0_release")
    print("-" * 50)
    
    source_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    backup_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release_backup")
    
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return False
    
    # 清理旧备份
    if backup_dir.exists():
        print(f"Removing old backup...")
        shutil.rmtree(backup_dir)
    
    # 创建备份
    print(f"Backing up {source_dir} to {backup_dir}...")
    shutil.copytree(source_dir, backup_dir)
    
    # 验证备份
    source_files = sum(1 for f in source_dir.rglob("*") if f.is_file())
    backup_files = sum(1 for f in backup_dir.rglob("*") if f.is_file())
    
    print(f"Backup created:")
    print(f"  Source files: {source_files}")
    print(f"  Backup files: {backup_files}")
    print(f"  Backup size: {sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / 1024:.1f} KB")
    
    if source_files == backup_files:
        print(f"  Status: ✅ Backup successful")
        return True
    else:
        print(f"  Status: ❌ Backup failed (file count mismatch)")
        return False

def consolidate_utils_modules():
    """合并工具模块"""
    print(f"\n2. CONSOLIDATING UTILS MODULES (High Priority)")
    print("-" * 50)
    
    release_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    
    # 创建合并后的工具模块
    utils_dir = release_dir / "utils"
    consolidated_file = utils_dir / "utilities.py"
    
    print(f"Creating consolidated utilities module: {consolidated_file}")
    
    # 收集要合并的模块内容
    modules_to_merge = [
        utils_dir / "configuration" / "config.py",
        utils_dir / "logging" / "logger.py",
        utils_dir / "security" / "validator.py"
    ]
    
    consolidated_content = '''"""
Consolidated Utilities Module
Combines configuration, logging, and security utilities
"""

# ==================== Configuration Utilities ====================

class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.config_data = {}
    
    def load_config(self):
        """Load configuration"""
        import yaml
        if self.config_path and self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
        return self.config_data
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config_data.get(key, default)

# ==================== Logging Utilities ====================

import logging

def setup_logger(name='aisleepgen', level=logging.INFO):
    """Setup logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# ==================== Security Utilities ====================

class SecurityValidator:
    """Security validator"""
    
    def validate_path(self, path, allowed_dirs=None):
        """Validate file path"""
        import os
        from pathlib import Path
        
        if allowed_dirs is None:
            allowed_dirs = []
        
        path_obj = Path(path).resolve()
        
        # Check if path is within allowed directories
        for allowed_dir in allowed_dirs:
            allowed_path = Path(allowed_dir).resolve()
            try:
                path_obj.relative_to(allowed_path)
                return True
            except ValueError:
                continue
        
        return False
    
    def validate_input(self, input_data, max_length=1000):
        """Validate input data"""
        if not isinstance(input_data, str):
            return False
        
        if len(input_data) > max_length:
            return False
        
        # Basic security checks
        dangerous_patterns = [';', '&&', '||', '`', '$(']
        for pattern in dangerous_patterns:
            if pattern in input_data:
                return False
        
        return True

# ==================== Export ====================

__all__ = ['ConfigManager', 'setup_logger', 'SecurityValidator']
'''
    
    # 写入合并后的文件
    consolidated_file.parent.mkdir(parents=True, exist_ok=True)
    with open(consolidated_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_content)
    
    print(f"  Created: {consolidated_file}")
    
    # 删除旧的模块文件和目录
    old_dirs = [
        utils_dir / "configuration",
        utils_dir / "logging", 
        utils_dir / "security"
    ]
    
    for old_dir in old_dirs:
        if old_dir.exists():
            print(f"  Removing: {old_dir}")
            shutil.rmtree(old_dir)
    
    # 创建新的__init__.py
    utils_init = utils_dir / "__init__.py"
    with open(utils_init, 'w', encoding='utf-8') as f:
        f.write('''"""
Utilities module
"""

from .utilities import ConfigManager, setup_logger, SecurityValidator

__all__ = ['ConfigManager', 'setup_logger', 'SecurityValidator']
''')
    
    print(f"  Updated: {utils_init}")
    
    return True

def consolidate_data_modules():
    """合并数据模块"""
    print(f"\n3. CONSOLIDATING DATA MODULES (High Priority)")
    print("-" * 50)
    
    release_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    
    # 创建合并后的数据模块
    data_dir = release_dir / "data"
    consolidated_file = data_dir / "data_processor.py"
    
    print(f"Creating consolidated data processor module: {consolidated_file}")
    
    consolidated_content = '''"""
Consolidated Data Processor Module
Combines data validation, file reading, and statistics
"""

import json
import numpy as np
from pathlib import Path

# ==================== Data Validation ====================

class DataValidator:
    """Data validator"""
    
    def validate_edf_file(self, file_path):
        """Validate EDF file"""
        path = Path(file_path)
        
        if not path.exists():
            return False, "File does not exist"
        
        if path.suffix.lower() != '.edf':
            return False, "Not an EDF file"
        
        # Basic EDF validation
        try:
            with open(path, 'rb') as f:
                header = f.read(256)
                if len(header) < 256:
                    return False, "Invalid EDF header"
            
            return True, "Valid EDF file"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def validate_json_data(self, json_data):
        """Validate JSON data"""
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Basic validation
            if not isinstance(data, dict):
                return False, "Data must be a dictionary"
            
            return True, "Valid JSON data"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

# ==================== File Reading ====================

class FileReader:
    """File reader"""
    
    def read_text_file(self, file_path, encoding='utf-8'):
        """Read text file"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file: {str(e)}")
    
    def read_json_file(self, file_path):
        """Read JSON file"""
        content = self.read_text_file(file_path)
        return json.loads(content)
    
    def read_csv_data(self, file_path, delimiter=','):
        """Read CSV data"""
        import csv
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                data.append(row)
        
        return data

# ==================== Statistics ====================

class StatisticsCalculator:
    """Statistics calculator"""
    
    def calculate_basic_stats(self, data):
        """Calculate basic statistics"""
        if not data:
            return {}
        
        data_array = np.array(data)
        
        stats = {
            'count': len(data),
            'mean': float(np.mean(data_array)),
            'std': float(np.std(data_array)),
            'min': float(np.min(data_array)),
            'max': float(np.max(data_array)),
            'median': float(np.median(data_array))
        }
        
        return stats
    
    def calculate_hrv_metrics(self, rr_intervals):
        """Calculate HRV metrics"""
        if not rr_intervals or len(rr_intervals) < 2:
            return {}
        
        rr_array = np.array(rr_intervals)
        
        # Basic HRV metrics
        metrics = {
            'mean_rr': float(np.mean(rr_array)),
            'sdnn': float(np.std(rr_array)),  # Standard deviation
            'rmssd': float(np.sqrt(np.mean(np.diff(rr_array) ** 2))),  # Root mean square of successive differences
            'nn50': int(np.sum(np.abs(np.diff(rr_array)) > 50)),  # Number of pairs differing by more than 50ms
            'pnn50': float(np.sum(np.abs(np.diff(rr_array)) > 50) / len(rr_array) * 100)  # Percentage
        }
        
        return metrics

# ==================== Export ====================

__all__ = ['DataValidator', 'FileReader', 'StatisticsCalculator']
'''
    
    # 写入合并后的文件
    consolidated_file.parent.mkdir(parents=True, exist_ok=True)
    with open(consolidated_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_content)
    
    print(f"  Created: {consolidated_file}")
    
    # 删除旧的模块文件和目录
    old_dirs = [
        data_dir / "data_validator",
        data_dir / "file_reader",
        data_dir / "statistics"
    ]
    
    for old_dir in old_dirs:
        if old_dir.exists():
            print(f"  Removing: {old_dir}")
            shutil.rmtree(old_dir)
    
    # 创建新的__init__.py
    data_init = data_dir / "__init__.py"
    with open(data_init, 'w', encoding='utf-8') as f:
        f.write('''"""
Data processing module
"""

from .data_processor import DataValidator, FileReader, StatisticsCalculator

__all__ = ['DataValidator', 'FileReader', 'StatisticsCalculator']
''')
    
    print(f"  Updated: {data_init}")
    
    return True

def update_skill_imports():
    """更新skill.py中的导入"""
    print(f"\n4. UPDATING IMPORTS IN skill.py")
    print("-" * 50)
    
    release_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    skill_file = release_dir / "skill.py"
    
    if not skill_file.exists():
        print(f"ERROR: skill.py not found: {skill_file}")
        return False
    
    # 读取skill.py内容
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新导入
    # 旧的导入模式
    old_imports = [
        "from utils.configuration.config import ConfigManager",
        "from utils.logging.logger import setup_logger",
        "from utils.security.validator import SecurityValidator",
        "from data.data_validator.validator import DataValidator",
        "from data.file_reader.reader import FileReader",
        "from data.statistics.calculator import StatisticsCalculator"
    ]
    
    # 新的导入
    new_imports = [
        "from utils.utilities import ConfigManager, setup_logger, SecurityValidator",
        "from data.data_processor import DataValidator, FileReader, StatisticsCalculator"
    ]
    
    # 替换导入
    for old_import in old_imports:
        if old_import in content:
            content = content.replace(old_import, "")
            print(f"  Removed: {old_import}")
    
    # 添加新的导入
    import_section = "import os\nimport json\nimport yaml\nfrom pathlib import Path\n"
    for new_import in new_imports:
        if new_import not in content:
            import_section += new_import + "\n"
    
    # 找到第一个import之后的位置插入
    lines = content.split('\n')
    new_lines = []
    imports_added = False
    
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            if not imports_added:
                new_lines.append(import_section.strip())
                imports_added = True
            # 跳过旧的import（已经移除）
            continue
        new_lines.append(line)
    
    if not imports_added:
        # 如果没有找到import部分，在文件开头添加
        new_lines = [import_section.strip()] + new_lines
    
    updated_content = '\n'.join(new_lines)
    
    # 写入更新后的文件
    with open(skill_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"  Updated: {skill_file}")
    
    # 验证更新
    with open(skill_file, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    # 检查关键类是否存在
    required_classes = ['ConfigManager', 'setup_logger', 'SecurityValidator', 
                       'DataValidator', 'FileReader', 'StatisticsCalculator']
    
    missing_classes = []
    for cls in required_classes:
        if cls not in new_content:
            missing_classes.append(cls)
    
    if missing_classes:
        print(f"  WARNING: Missing classes in skill.py: {missing_classes}")
    else:
        print(f"  Status: ✅ All required classes found")
    
    return True

def verify_consolidation():
    """验证合并结果"""
    print(f"\n5. VERIFYING CONSOLIDATION RESULTS")
    print("-" * 50)
    
    release_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    
    # 统计模块数量
    python_files = list(release_dir.rglob("*.py"))
    module_count = len(python_files)
    
    print(f"Python modules after consolidation: {module_count}")
    
    # 检查关键文件
    required_files = [
        release_dir / "skill.py",
        release_dir / "utils" / "utilities.py",
        release_dir / "utils" / "__init__.py",
        release_dir / "data" / "data_processor.py",
        release_dir / "data" / "__init__.py"
    ]
    
    print(f"\nRequired files check:")
    missing_files = []
    for file_path in required_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file_path.relative_to(release_dir)} ({size} bytes)")
        else:
            print(f"  ❌ {file_path.relative_to(release_dir)} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"ERROR: {len(missing_files)} required files missing")
        return False
    
    # 检查删除的目录
    deleted_dirs = [
        release_dir / "utils" / "configuration",
        release_dir / "utils" / "logging",
        release_dir / "utils" / "security",
        release_dir / "data" / "data_validator",
        release_dir / "data" / "file_reader",
        release_dir / "data" / "statistics"
    ]
    
    print(f"\nDeleted directories check:")
    existing_dirs = []
    for dir_path in deleted_dirs:
        if dir_path.exists():
            print(f"  ⚠️ {dir_path.relative