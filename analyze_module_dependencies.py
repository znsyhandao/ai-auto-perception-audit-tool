"""
深度分析模块依赖关系，识别矩阵分解问题根源
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class DependencyAnalyzer:
    """分析模块依赖关系"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.modules = {}
        self.dependency_matrix = {}
        self.import_graph = {}
    
    def analyze_all_modules(self):
        """分析所有模块"""
        print(f"Analyzing modules in: {self.skill_path}")
        
        # 查找所有Python文件
        python_files = list(self.skill_path.rglob("*.py"))
        print(f"Found {len(python_files)} Python files")
        
        for file in python_files:
            relative_path = file.relative_to(self.skill_path)
            module_name = str(relative_path).replace("\\", "/").replace("/", ".").replace(".py", "")
            
            print(f"  Analyzing: {module_name}")
            
            # 分析文件依赖
            imports = self._analyze_file_imports(file)
            self.modules[module_name] = {
                "file": str(file),
                "imports": imports,
                "size_kb": file.stat().st_size / 1024
            }
            
            # 构建依赖图
            self.import_graph[module_name] = imports
        
        return self.modules
    
    def _analyze_file_imports(self, file_path: Path) -> List[str]:
        """分析文件的导入语句"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        full_import = f"{module}.{alias.name}" if module else alias.name
                        imports.append(full_import)
        
        except Exception as e:
            print(f"    Error analyzing {file_path}: {e}")
        
        return imports
    
    def build_dependency_matrix(self):
        """构建依赖矩阵"""
        module_names = sorted(self.modules.keys())
        n = len(module_names)
        
        # 初始化矩阵
        matrix = [[0] * n for _ in range(n)]
        
        # 填充依赖关系
        for i, module_i in enumerate(module_names):
            for j, module_j in enumerate(module_names):
                if i == j:
                    matrix[i][j] = 0  # 不自依赖
                else:
                    # 检查module_i是否导入module_j
                    imports_i = self.modules[module_i]["imports"]
                    
                    # 简化检查：模块名是否在导入中
                    depends = 0
                    for imp in imports_i:
                        if module_j in imp or any(part in imp for part in module_j.split(".")):
                            depends = 1
                            break
                    
                    matrix[i][j] = depends
        
        self.dependency_matrix = {
            "modules": module_names,
            "matrix": matrix,
            "density": self._calculate_matrix_density(matrix)
        }
        
        return self.dependency_matrix
    
    def _calculate_matrix_density(self, matrix: List[List[int]]) -> float:
        """计算矩阵密度（依赖比例）"""
        n = len(matrix)
        if n == 0:
            return 0.0
        
        total_cells = n * n - n  # 排除对角线
        dependencies = sum(sum(row) for row in matrix)
        
        return dependencies / total_cells if total_cells > 0 else 0.0
    
    def analyze_problems(self):
        """分析依赖问题"""
        problems = []
        
        # 1. 检查循环依赖
        cycles = self._find_cycles()
        if cycles:
            problems.append({
                "type": "circular_dependency",
                "description": f"Found {len(cycles)} circular dependency cycles",
                "cycles": cycles[:3]  # 只显示前3个
            })
        
        # 2. 检查高耦合模块
        high_coupling = self._find_high_coupling_modules()
        if high_coupling:
            problems.append({
                "type": "high_coupling",
                "description": f"Found {len(high_coupling)} highly coupled modules",
                "modules": high_coupling
            })
        
        # 3. 检查模块大小不平衡
        size_issues = self._analyze_module_sizes()
        if size_issues:
            problems.append({
                "type": "size_imbalance",
                "description": "Module size imbalance detected",
                "issues": size_issues
            })
        
        return problems
    
    def _find_cycles(self) -> List[List[str]]:
        """查找循环依赖"""
        # 简化实现
        cycles = []
        visited = set()
        
        def dfs(module, path):
            if module in path:
                # 找到循环
                cycle_start = path.index(module)
                cycle = path[cycle_start:] + [module]
                if len(cycle) > 2:  # 忽略自循环
                    cycles.append(cycle)
                return
            
            if module in visited:
                return
            
            visited.add(module)
            path.append(module)
            
            for dep in self.import_graph.get(module, []):
                # 简化：只检查直接导入
                if dep in self.import_graph:
                    dfs(dep, path.copy())
        
        for module in self.import_graph:
            dfs(module, [])
        
        return cycles
    
    def _find_high_coupling_modules(self, threshold: float = 0.5) -> List[Dict]:
        """查找高耦合模块"""
        high_coupling = []
        
        for module, data in self.modules.items():
            import_count = len(data["imports"])
            total_modules = len(self.modules) - 1  # 排除自己
            
            if total_modules > 0:
                coupling_ratio = import_count / total_modules
                if coupling_ratio > threshold:
                    high_coupling.append({
                        "module": module,
                        "imports": import_count,
                        "coupling_ratio": coupling_ratio,
                        "imported_modules": data["imports"][:5]  # 只显示前5个
                    })
        
        return high_coupling
    
    def _analyze_module_sizes(self) -> Dict:
        """分析模块大小"""
        sizes = [data["size_kb"] for data in self.modules.values()]
        
        if not sizes:
            return {}
        
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)
        min_size = min(sizes)
        
        issues = {}
        
        # 检查过大模块
        large_modules = []
        for module, data in self.modules.items():
            if data["size_kb"] > avg_size * 3:  # 超过平均3倍
                large_modules.append({
                    "module": module,
                    "size_kb": data["size_kb"],
                    "ratio_to_avg": data["size_kb"] / avg_size
                })
        
        if large_modules:
            issues["large_modules"] = large_modules
        
        # 检查大小差异
        if max_size > 0:
            size_ratio = max_size / min_size if min_size > 0 else float('inf')
            if size_ratio > 10:  # 最大模块是最小模块的10倍以上
                issues["size_disparity"] = {
                    "max_size_kb": max_size,
                    "min_size_kb": min_size,
                    "ratio": size_ratio
                }
        
        return issues
    
    def generate_optimization_plan(self, problems: List[Dict]) -> Dict:
        """生成优化计划"""
        plan = {
            "optimization_goals": [
                "Reduce matrix decomposition confidence from 0.700 to ≥0.850",
                "Eliminate circular dependencies",
                "Reduce module coupling",
                "Balance module sizes"
            ],
            "steps": []
        }
        
        for problem in problems:
            if problem["type"] == "circular_dependency":
                plan["steps"].append({
                    "action": "break_circular_dependencies",
                    "description": "Break circular dependencies by introducing interfaces or dependency inversion",
                    "priority": "high",
                    "estimated_time": "30-60 minutes"
                })
            
            elif problem["type"] == "high_coupling":
                plan["steps"].append({
                    "action": "reduce_module_coupling",
                    "description": "Reduce coupling by extracting shared functionality to utility modules",
                    "priority": "high",
                    "estimated_time": "45-90 minutes"
                })
            
            elif problem["type"] == "size_imbalance":
                plan["steps"].append({
                    "action": "balance_module_sizes",
                    "description": "Split large modules and consolidate small ones",
                    "priority": "medium",
                    "estimated_time": "30-60 minutes"
                })
        
        # 添加通用优化步骤
        plan["steps"].extend([
            {
                "action": "introduce_dependency_injection",
                "description": "Use dependency injection to reduce hard-coded dependencies",
                "priority": "medium",
                "estimated_time": "30 minutes"
            },
            {
                "action": "create_interface_modules",
                "description": "Create interface modules to define clear boundaries",
                "priority": "medium",
                "estimated_time": "30 minutes"
            },
            {
                "action": "add_dependency_validation",
                "description": "Add dependency validation to prevent unwanted imports",
                "priority": "low",
                "estimated_time": "15 minutes"
            }
        ])
        
        return plan

def main():
    """主分析函数"""
    print("DEEP MODULE DEPENDENCY ANALYSIS")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.8_modular"
    
    analyzer = DependencyAnalyzer(skill_path)
    
    print(f"\n1. Analyzing module structure...")
    modules = analyzer.analyze_all_modules()
    print(f"   Modules analyzed: {len(modules)}")
    
    print(f"\n2. Building dependency matrix...")
    matrix_info = analyzer.build_dependency_matrix()
    print(f"   Matrix size: {len(matrix_info['modules'])}x{len(matrix_info['modules'])}")
    print(f"   Dependency density: {matrix_info['density']:.3f}")
    
    print(f"\n3. Identifying dependency problems...")
    problems = analyzer.analyze_problems()
    print(f"   Problems found: {len(problems)}")
    
    for problem in problems:
        print(f"   - {problem['type']}: {problem['description']}")
    
    print(f"\n4. Generating optimization plan...")
    plan = analyzer.generate_optimization_plan(problems)
    
    print(f"\n5. Optimization Plan Summary:")
    for i, goal in enumerate(plan["optimization_goals"], 1):
        print(f"   {i}. {goal}")
    
    print(f"\n6. Recommended Steps:")
    for i, step in enumerate(plan["steps"][:5], 1):  # 只显示前5个
        print(f"   {i}. [{step['priority'].upper()}] {step['action']}")
        print(f"      {step['description']}")
        print(f"      Estimated: {step['estimated_time']}")
    
    # 保存分析报告
    report = {
        "analysis_time": "2026-03-31T09:05:00Z",
        "skill_path": skill_path,
        "module_count": len(modules),
        "dependency_density": matrix_info["density"],
        "problems": problems,
        "optimization_plan": plan,
        "matrix_decomposition_issue": {
            "current_confidence": 0.700,
            "target_confidence": 0.850,
            "required_improvement": 0.150,
            "key_factors": [
                "Reduce dependency density",
                "Eliminate circular dependencies",
                "Create clear dependency hierarchy"
            ]
        }
    }
    
    report_file = "module_dependency_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n7. Analysis report saved: {report_file}")
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("Ready for deep optimization.")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)