"""
增强的依赖分析器 - 匹配数学审核的依赖检测
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class EnhancedDependencyAnalyzer:
    """增强的依赖分析器，匹配数学审核检测"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.dependencies = []
        self.dependency_weights = {
            "class_inheritance": 3.0,  # 最高权重
            "function_call_chain": 2.5,  # 高权重
            "import_statement": 2.0,  # 中高权重
            "method_call": 1.5,  # 中权重
            "attribute_access": 1.0,  # 低权重
            "internal_reference": 0.5  # 内部引用
        }
        
    def analyze_skill(self):
        """分析技能的所有依赖"""
        print(f"ENHANCED DEPENDENCY ANALYSIS - Matching Mathematical Audit")
        print(f"Target: {self.skill_path}")
        
        python_files = list(self.skill_path.rglob("*.py"))
        print(f"Found {len(python_files)} Python files")
        
        all_dependencies = []
        
        for file in python_files:
            relative_path = file.relative_to(self.skill_path)
            module_name = str(relative_path).replace("\\", "/").replace("/", ".").replace(".py", "")
            
            print(f"\nAnalyzing: {module_name}")
            
            # 分析文件的所有依赖类型
            file_deps = self._analyze_file_dependencies(file, module_name)
            all_dependencies.extend(file_deps)
            
            # 显示统计
            dep_types = {}
            for dep in file_deps:
                dep_type = dep[2]  # 依赖类型
                dep_types[dep_type] = dep_types.get(dep_type, 0) + 1
            
            if dep_types:
                print(f"  Dependency types: {dep_types}")
        
        self.dependencies = all_dependencies
        
        print(f"\n" + "=" * 70)
        print(f"ANALYSIS COMPLETE")
        print(f"Total dependencies found: {len(all_dependencies)}")
        
        return all_dependencies
    
    def _analyze_file_dependencies(self, file_path: Path, module_name: str) -> List[Tuple]:
        """分析文件的所有依赖类型"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 收集所有定义
            definitions = self._collect_definitions(tree)
            
            # 分析各种依赖
            dependencies.extend(self._analyze_imports(tree, module_name))
            dependencies.extend(self._analyze_class_inheritance(tree, module_name))
            dependencies.extend(self._analyze_function_calls(tree, module_name, definitions))
            dependencies.extend(self._analyze_method_calls(tree, module_name))
            dependencies.extend(self._analyze_attribute_access(tree, module_name))
            
        except Exception as e:
            print(f"  Error analyzing {file_path}: {e}")
        
        return dependencies
    
    def _collect_definitions(self, tree: ast.AST) -> Dict[str, str]:
        """收集所有定义（类、函数）"""
        definitions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                definitions[node.name] = "class"
            elif isinstance(node, ast.FunctionDef):
                definitions[node.name] = "function"
        
        return definitions
    
    def _analyze_imports(self, tree: ast.AST, module_name: str) -> List[Tuple]:
        """分析导入依赖"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append((module_name, alias.name, "import_statement", 1.0))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if module:
                        full_import = f"{module}.{alias.name}"
                        dependencies.append((module_name, full_import, "import_statement", 1.0))
                    else:
                        dependencies.append((module_name, alias.name, "import_statement", 1.0))
        
        return dependencies
    
    def _analyze_class_inheritance(self, tree: ast.AST, module_name: str) -> List[Tuple]:
        """分析类继承依赖"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查基类
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_name = base.id
                        dependencies.append((module_name, base_name, "class_inheritance", 1.0))
                    elif isinstance(base, ast.Attribute):
                        # 处理 module.Class 形式
                        base_name = self._get_attribute_name(base)
                        dependencies.append((module_name, base_name, "class_inheritance", 1.0))
        
        return dependencies
    
    def _analyze_function_calls(self, tree: ast.AST, module_name: str, definitions: Dict) -> List[Tuple]:
        """分析函数调用依赖"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 获取被调用的函数名
                func_name = self._get_function_name(node.func)
                if func_name and func_name in definitions and definitions[func_name] == "function":
                    dependencies.append((module_name, func_name, "function_call_chain", 1.0))
        
        return dependencies
    
    def _analyze_method_calls(self, tree: ast.AST, module_name: str) -> List[Tuple]:
        """分析方法调用依赖"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # 形式: obj.method()
                    attr_name = self._get_attribute_name(node.func)
                    if attr_name and "." in attr_name:  # 确保是方法调用
                        dependencies.append((module_name, attr_name, "method_call", 1.0))
        
        return dependencies
    
    def _analyze_attribute_access(self, tree: ast.AST, module_name: str) -> List[Tuple]:
        """分析属性访问依赖"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and not isinstance(node.ctx, ast.Store):
                # 属性访问（非赋值）
                attr_name = self._get_attribute_name(node)
                if attr_name and "." in attr_name:
                    dependencies.append((module_name, attr_name, "attribute_access", 1.0))
        
        return dependencies
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """获取属性名称"""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return ".".join(reversed(parts)) if parts else ""
    
    def _get_function_name(self, node: ast.expr) -> str:
        """获取函数名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        return ""
    
    def calculate_metrics(self):
        """计算依赖指标"""
        if not self.dependencies:
            return {"error": "No dependencies analyzed"}
        
        # 按类型统计
        type_counts = {}
        type_weights = {}
        
        for _, _, dep_type, _ in self.dependencies:
            type_counts[dep_type] = type_counts.get(dep_type, 0) + 1
            type_weights[dep_type] = type_weights.get(dep_type, 0) + self.dependency_weights.get(dep_type, 1.0)
        
        # 计算加权依赖密度
        total_weight = sum(type_weights.values())
        module_count = len(set(dep[0] for dep in self.dependencies))  # 唯一模块数
        
        if module_count == 0:
            weighted_density = 0
        else:
            weighted_density = total_weight / (module_count * module_count)
        
        # 计算置信度（模拟数学审核）
        confidence = 0.6 + min(0.4, weighted_density * 0.4)  # 限制最大增长
        
        metrics = {
            "total_dependencies": len(self.dependencies),
            "module_count": module_count,
            "dependency_types": type_counts,
            "weighted_dependencies": type_weights,
            "total_weight": total_weight,
            "weighted_density": weighted_density,
            "estimated_confidence": confidence,
            "current_audit_confidence": 0.700,  # 从审核结果
            "confidence_gap": confidence - 0.700,
            "optimization_target": 0.850
        }
        
        return metrics
    
    def identify_optimization_targets(self, metrics: Dict) -> List[Dict]:
        """识别优化目标"""
        targets = []
        
        type_counts = metrics.get("dependency_types", {})
        type_weights = metrics.get("weighted_dependencies", {})
        
        # 按权重排序依赖类型
        sorted_types = sorted(type_weights.items(), key=lambda x: x[1], reverse=True)
        
        for dep_type, weight in sorted_types[:3]:  # 前3个高权重类型
            count = type_counts.get(dep_type, 0)
            avg_weight = weight / count if count > 0 else 0
            
            target = {
                "dependency_type": dep_type,
                "count": count,
                "total_weight": weight,
                "average_weight": avg_weight,
                "optimization_strategy": self._get_optimization_strategy(dep_type),
                "estimated_impact": self._estimate_impact(dep_type, count),
                "priority": "high" if dep_type in ["class_inheritance", "function_call_chain"] else "medium"
            }
            
            targets.append(target)
        
        return targets
    
    def _get_optimization_strategy(self, dep_type: str) -> str:
        """获取优化策略"""
        strategies = {
            "class_inheritance": "Flatten class hierarchy, use composition over inheritance",
            "function_call_chain": "Reduce call depth, extract common patterns",
            "import_statement": "Consolidate imports, remove unused imports",
            "method_call": "Reduce internal method calls, simplify object interactions",
            "attribute_access": "Simplify attribute chains, use direct access",
            "internal_reference": "Reduce self-references, improve modularity"
        }
        
        return strategies.get(dep_type, "General dependency reduction")
    
    def _estimate_impact(self, dep_type: str, count: int) -> str:
        """估计优化影响"""
        if dep_type == "class_inheritance":
            return f"High impact: Reduce by {max(1, count // 2)} dependencies"
        elif dep_type == "function_call_chain":
            return f"High impact: Reduce by {max(1, count // 3)} dependencies"
        elif dep_type == "import_statement":
            return f"Medium impact: Reduce by {max(1, count // 4)} dependencies"
        else:
            return f"Low impact: Reduce by {max(1, count // 5)} dependencies"
    
    def generate_optimization_report(self):
        """生成优化报告"""
        print(f"\n" + "=" * 70)
        print(f"OPTIMIZATION TARGET IDENTIFICATION")
        print(f"=" * 70)
        
        # 计算指标
        metrics = self.calculate_metrics()
        
        print(f"\nDependency Metrics:")
        print(f"  Total dependencies: {metrics['total_dependencies']}")
        print(f"  Module count: {metrics['module_count']}")
        print(f"  Weighted density: {metrics['weighted_density']:.4f}")
        print(f"  Estimated confidence: {metrics['estimated_confidence']:.3f}")
        print(f"  Current audit confidence: {metrics['current_audit_confidence']:.3f}")
        print(f"  Confidence gap: {metrics['confidence_gap']:+.3f}")
        print(f"  Target confidence: {metrics['optimization_target']:.3f}")
        
        print(f"\nDependency Type Breakdown:")
        for dep_type, count in metrics['dependency_types'].items():
            weight = metrics['weighted_dependencies'].get(dep_type, 0)
            print(f"  {dep_type}: {count} dependencies, weight: {weight:.1f}")
        
        # 识别优化目标
        targets = self.identify_optimization_targets(metrics)
        
        print(f"\nTop Optimization Targets (by weight):")
        for i, target in enumerate(targets, 1):
            print(f"\n  {i}. {target['dependency_type'].upper()}")
            print(f"     Count: {target['count']}")
            print(f"     Total weight: {target['total_weight']:.1f}")
            print(f"     Priority: {target['priority'].upper()}")
            print(f"     Strategy: {target['optimization_strategy']}")
            print(f"     Estimated impact: {target['estimated_impact']}")
        
        # 保存报告
        report = {
            "analysis_time": "2026-03-31T09:56:00Z",
            "skill_path": str(self.skill_path),
            "metrics": metrics,
            "optimization_targets": targets,
            "principles_applied": [
                "理解优先于通过 - 基于对审核依赖检测的理解",
                "针对性优化 - 针对高权重依赖类型",
                "实证分析 - 基于实际代码分析"
            ]
        }
        
        report_file = "enhanced_dependency_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n" + "=" * 70)
        print(f"REPORT GENERATED: {report_file}")
        print(f"Ready for targeted optimization implementation")
        
        return report

def main():
    """主分析函数"""
    print("ENHANCED DEPENDENCY ANALYSIS FOR v2.0 OPTIMIZATION")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.9_optimized"
    
    analyzer = EnhancedDependencyAnalyzer(skill_path)
    
    # 分析依赖
    dependencies = analyzer.analyze_skill()
    
    # 生成优化报告
    report = analyzer.generate_optimization_report()
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE - READY FOR TARGETED OPTIMIZATION")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)