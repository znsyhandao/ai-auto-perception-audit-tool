"""
v2.0针对性优化：分析当前依赖关系，设计优化方案
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class V2DependencyAnalyzer:
    """v2.0依赖关系分析器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.modules = {}
        self.dependencies = []
        self.dependency_graph = {}
        
    def analyze_all_dependencies(self):
        """分析所有依赖关系"""
        print(f"ANALYZING DEPENDENCIES FOR v2.0 OPTIMIZATION")
        print(f"Target: {self.skill_path}")
        
        # 查找所有Python文件
        python_files = list(self.skill_path.rglob("*.py"))
        print(f"Found {len(python_files)} Python files")
        
        total_dependencies = 0
        
        for file in python_files:
            relative_path = file.relative_to(self.skill_path)
            module_name = str(relative_path).replace("\\", "/").replace("/", ".").replace(".py", "")
            
            # 分析文件导入
            imports = self._analyze_file_imports(file, module_name)
            
            self.modules[module_name] = {
                "file": str(file),
                "imports": imports,
                "import_count": len(imports),
                "size_kb": file.stat().st_size / 1024
            }
            
            # 记录依赖关系
            for imp in imports:
                # 简化：假设导入的都是内部模块
                if imp and not imp.startswith(("os", "sys", "json", "math", "typing")):
                    self.dependencies.append((module_name, imp))
                    total_dependencies += 1
            
            self.dependency_graph[module_name] = imports
        
        print(f"Total dependencies found: {total_dependencies}")
        return self.dependencies
    
    def _analyze_file_imports(self, file_path: Path, module_name: str) -> List[str]:
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
                        if module:  # from module import something
                            full_import = f"{module}.{alias.name}"
                            imports.append(full_import)
                        else:  # from . import something
                            imports.append(alias.name)
        
        except Exception as e:
            print(f"  Error analyzing {file_path}: {e}")
        
        return imports
    
    def calculate_dependency_metrics(self):
        """计算依赖指标"""
        n = len(self.modules)
        if n == 0:
            return {"error": "No modules"}
        
        # 依赖密度
        dependency_density = len(self.dependencies) / (n * n) if n > 0 else 0
        
        # 模块导入统计
        import_counts = [data["import_count"] for data in self.modules.values()]
        avg_imports = sum(import_counts) / n if n > 0 else 0
        max_imports = max(import_counts) if import_counts else 0
        
        # 识别高导入模块
        high_import_modules = []
        for module, data in self.modules.items():
            if data["import_count"] > avg_imports * 2:  # 超过平均2倍
                high_import_modules.append({
                    "module": module,
                    "imports": data["import_count"],
                    "avg_ratio": data["import_count"] / avg_imports if avg_imports > 0 else 0
                })
        
        # 识别可能的循环依赖
        possible_cycles = self._find_possible_cycles()
        
        metrics = {
            "module_count": n,
            "dependency_count": len(self.dependencies),
            "dependency_density": dependency_density,
            "avg_imports_per_module": avg_imports,
            "max_imports": max_imports,
            "high_import_modules": high_import_modules,
            "possible_cycles": possible_cycles,
            "current_confidence": 0.6 + dependency_density * 0.4,
            "target_confidence": 0.850,
            "required_density_reduction": self._calculate_required_reduction(dependency_density)
        }
        
        return metrics
    
    def _find_possible_cycles(self) -> List[List[str]]:
        """查找可能的循环依赖"""
        cycles = []
        visited = set()
        
        def dfs(current, path):
            if current in path:
                # 找到循环
                cycle_start = path.index(current)
                cycle = path[cycle_start:] + [current]
                if len(cycle) > 2:  # 忽略自循环
                    cycles.append(cycle)
                return
            
            if current in visited:
                return
            
            visited.add(current)
            path.append(current)
            
            for dep in self.dependency_graph.get(current, []):
                if dep in self.dependency_graph:
                    dfs(dep, path.copy())
        
        for module in self.dependency_graph:
            dfs(module, [])
        
        return cycles[:5]  # 只返回前5个可能的循环
    
    def _calculate_required_reduction(self, current_density: float) -> Dict:
        """计算需要减少的依赖密度"""
        # 当前置信度: 0.6 + current_density * 0.4
        # 目标置信度: 0.850
        # 解方程: 0.6 + target_density * 0.4 = 0.850
        # target_density = (0.850 - 0.6) / 0.4 = 0.625
        
        target_density = (0.850 - 0.6) / 0.4  # 0.625
        
        current_confidence = 0.6 + current_density * 0.4
        required_reduction = current_density - target_density
        
        n = len(self.modules)
        current_dependencies = len(self.dependencies)
        target_dependencies = int(target_density * n * n)
        dependencies_to_remove = current_dependencies - target_dependencies
        
        return {
            "current_density": current_density,
            "target_density": target_density,
            "required_reduction": required_reduction,
            "current_dependencies": current_dependencies,
            "target_dependencies": target_dependencies,
            "dependencies_to_remove": max(0, dependencies_to_remove),
            "reduction_percentage": (required_reduction / current_density * 100) if current_density > 0 else 0
        }
    
    def generate_optimization_plan(self, metrics: Dict) -> Dict:
        """生成优化计划"""
        n = metrics["module_count"]
        current_density = metrics["dependency_density"]
        reduction_info = metrics["required_density_reduction"]
        
        plan = {
            "optimization_goal": "Increase matrix decomposition confidence from 0.700 to ≥0.850",
            "current_state": {
                "module_count": n,
                "dependency_count": metrics["dependency_count"],
                "dependency_density": current_density,
                "current_confidence": metrics["current_confidence"]
            },
            "target_state": {
                "target_confidence": 0.850,
                "target_density": reduction_info["target_density"],
                "target_dependencies": reduction_info["target_dependencies"]
            },
            "optimization_required": {
                "dependencies_to_remove": reduction_info["dependencies_to_remove"],
                "reduction_percentage": reduction_info["reduction_percentage"]
            },
            "optimization_strategies": [
                {
                    "strategy": "reduce_unnecessary_imports",
                    "description": "Remove imports that are not actually used",
                    "target": "All modules",
                    "estimated_impact": "10-20% dependency reduction",
                    "priority": "high"
                },
                {
                    "strategy": "consolidate_common_imports",
                    "description": "Create shared utility modules for common imports",
                    "target": "High-import modules",
                    "estimated_impact": "15-25% dependency reduction",
                    "priority": "high"
                },
                {
                    "strategy": "optimize_interface_design",
                    "description": "Redesign interfaces to reduce coupling",
                    "target": "Interface modules",
                    "estimated_impact": "20-30% dependency reduction",
                    "priority": "medium"
                },
                {
                    "strategy": "break_circular_dependencies",
                    "description": "Eliminate circular dependencies",
                    "target": "Cyclic modules",
                    "estimated_impact": "5-15% dependency reduction",
                    "priority": "medium"
                },
                {
                    "strategy": "create_dependency_hierarchy",
                    "description": "Establish clear dependency direction",
                    "target": "All modules",
                    "estimated_impact": "10-20% dependency reduction",
                    "priority": "medium"
                }
            ],
            "implementation_steps": [
                {
                    "step": 1,
                    "action": "analyze_import_usage",
                    "description": "Identify which imports are actually used",
                    "time_estimate": "30 minutes"
                },
                {
                    "step": 2,
                    "action": "remove_unused_imports",
                    "description": "Delete imports that are not used",
                    "time_estimate": "45 minutes"
                },
                {
                    "step": 3,
                    "action": "consolidate_utilities",
                    "description": "Create shared utility modules",
                    "time_estimate": "60 minutes"
                },
                {
                    "step": 4,
                    "action": "redesign_interfaces",
                    "description": "Optimize interface dependencies",
                    "time_estimate": "90 minutes"
                },
                {
                    "step": 5,
                    "action": "verify_optimization",
                    "description": "Run mathematical audit to verify improvement",
                    "time_estimate": "30 minutes"
                }
            ],
            "success_criteria": {
                "primary": "Matrix decomposition confidence ≥ 0.850",
                "secondary": [
                    "Dependency count reduced by ≥30%",
                    "No circular dependencies",
                    "Clear dependency hierarchy established"
                ]
            }
        }
        
        # 添加针对高导入模块的具体建议
        if metrics["high_import_modules"]:
            plan["targeted_optimizations"] = []
            for module_info in metrics["high_import_modules"][:3]:  # 前3个高导入模块
                plan["targeted_optimizations"].append({
                    "module": module_info["module"],
                    "current_imports": module_info["imports"],
                    "target_imports": int(module_info["imports"] * 0.5),  # 减少50%
                    "strategy": "extract_shared_functionality"
                })
        
        return plan
    
    def save_analysis_report(self, metrics: Dict, plan: Dict):
        """保存分析报告"""
        report = {
            "analysis_time": "2026-03-31T09:48:00Z",
            "skill_path": str(self.skill_path),
            "metrics": metrics,
            "optimization_plan": plan,
            "principles_applied": [
                "理解优先于通过 - 基于对矩阵分解算法的理解进行优化",
                "针对性优化 - 专门针对依赖密度进行优化",
                "透明规划 - 明确的优化目标和策略"
            ]
        }
        
        report_file = "v2_dependency_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nAnalysis report saved: {report_file}")
        return report_file

def main():
    """主分析函数"""
    print("=" * 70)
    print("v2.0 TARGETED OPTIMIZATION DESIGN")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.9_optimized"
    
    analyzer = V2DependencyAnalyzer(skill_path)
    
    print(f"\n1. Analyzing current dependency structure...")
    dependencies = analyzer.analyze_all_dependencies()
    print(f"   Dependencies analyzed: {len(dependencies)}")
    
    print(f"\n2. Calculating dependency metrics...")
    metrics = analyzer.calculate_dependency_metrics()
    
    print(f"   Module count: {metrics['module_count']}")
    print(f"   Dependency count: {metrics['dependency_count']}")
    print(f"   Dependency density: {metrics['dependency_density']:.4f}")
    print(f"   Current confidence: {metrics['current_confidence']:.3f}")
    print(f"   Target confidence: {metrics['target_confidence']:.3f}")
    
    reduction = metrics['required_density_reduction']
    print(f"\n3. Optimization requirements:")
    print(f"   Dependencies to remove: {reduction['dependencies_to_remove']}")
    print(f"   Density reduction needed: {reduction['required_reduction']:.4f}")
    print(f"   Reduction percentage: {reduction['reduction_percentage']:.1f}%")
    
    print(f"\n4. Generating optimization plan...")
    plan = analyzer.generate_optimization_plan(metrics)
    
    print(f"\n5. Optimization Strategies (priority order):")
    for i, strategy in enumerate(plan["optimization_strategies"][:3], 1):
        print(f"   {i}. [{strategy['priority'].upper()}] {strategy['strategy']}")
        print(f"      {strategy['description']}")
        print(f"      Estimated impact: {strategy['estimated_impact']}")
    
    print(f"\n6. Implementation Steps:")
    for step in plan["implementation_steps"]:
        print(f"   Step {step['step']}: {step['action']}")
        print(f"      {step['description']}")
        print(f"      Time: {step['time_estimate']}")
    
    print(f"\n7. Success Criteria:")
    print(f"   Primary: {plan['success_criteria']['primary']}")
    for i, criterion in enumerate(plan['success_criteria']['secondary'], 1):
        print(f"   Secondary {i}: {criterion}")
    
    # 保存报告
    report_file = analyzer.save_analysis_report(metrics, plan)
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE - READY FOR OPTIMIZATION")
    print("=" * 70)
    print(f"\nNext: Begin implementation of optimization strategies")
    print(f"Report: {report_file}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)