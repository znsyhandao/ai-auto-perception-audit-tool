"""
数学AI引擎 - 继续部分：傅里叶变换、矩阵分解、数学证明
"""

import numpy as np
import math
from typing import List, Dict, Any
import sympy as sp

class MathematicalAIEngineContinued:
    """数学AI引擎继续部分"""
    
    def _identify_pattern_type(self, frequencies: List[Dict]) -> str:
        """识别模式类型"""
        if not frequencies:
            return "random"
        
        # 提取主要频率
        significant_freqs = [f for f in frequencies if f["power"] > 0.05]
        
        if len(significant_freqs) == 0:
            return "random_noise"
        elif len(significant_freqs) == 1:
            freq = significant_freqs[0]["frequency"]
            if freq < 0.1:
                return "slow_periodic"
            else:
                return "fast_periodic"
        elif len(significant_freqs) == 2:
            return "harmonic"
        elif len(significant_freqs) <= 4:
            return "quasi_periodic"
        else:
            # 检查是否有基频和谐波关系
            if self._has_harmonic_relationship(significant_freqs):
                return "harmonic_complex"
            else:
                return "complex_aperiodic"
    
    def _has_harmonic_relationship(self, frequencies: List[Dict]) -> bool:
        """检查频率是否有谐波关系"""
        if len(frequencies) < 2:
            return False
        
        # 提取频率值
        freqs = [f["frequency"] for f in frequencies]
        base_freq = min(freqs)
        
        # 检查其他频率是否是基频的整数倍
        harmonic_count = 0
        for freq in freqs:
            ratio = freq / base_freq
            if abs(ratio - round(ratio)) < 0.1:  # 允许10%误差
                harmonic_count += 1
        
        return harmonic_count >= len(freqs) * 0.7  # 70%以上是谐波
    
    def _code_to_numeric_sequence(self, code_sequence: List[str]) -> List[float]:
        """将代码序列转换为数值序列"""
        # 使用字符串哈希和长度组合
        numeric = []
        for code in code_sequence:
            # 组合多个特征：长度、哈希、复杂性估计
            length_feature = len(code) / 100.0  # 归一化长度
            hash_feature = (hash(code) % 1000) / 1000.0  # 归一化哈希
            
            # 简单复杂性估计：行数、括号数等
            complexity_feature = self._estimate_code_complexity(code)
            
            # 组合特征
            combined = 0.4 * length_feature + 0.3 * hash_feature + 0.3 * complexity_feature
            numeric.append(combined)
        
        return numeric
    
    def _estimate_code_complexity(self, code: str) -> float:
        """估计代码复杂性"""
        # 简单实现：基于特殊字符计数
        special_chars = sum(1 for c in code if c in '{}[]()<>;:')
        length = len(code)
        
        if length == 0:
            return 0.0
        
        return min(1.0, special_chars / (length * 0.5))
    
    def _calculate_periodicity_score(self, frequencies: List[Dict]) -> float:
        """计算周期性分数"""
        if not frequencies:
            return 0.0
        
        # 基于主要频率的功率计算
        total_power = sum(f["power"] for f in frequencies)
        if total_power == 0:
            return 0.0
        
        # 周期性代码通常有少数几个显著频率
        top_freqs = sorted(frequencies, key=lambda x: x["power"], reverse=True)[:3]
        top_power = sum(f["power"] for f in top_freqs)
        
        periodicity = top_power / total_power
        
        # 调整分数：完全周期性接近1，完全随机接近0
        return periodicity
    
    def _calculate_complexity_score(self, frequencies: List[Dict]) -> float:
        """计算复杂度分数"""
        if not frequencies:
            return 0.0
        
        # 基于频率数量和分布计算复杂度
        freq_count = len(frequencies)
        power_distribution = [f["power"] for f in frequencies]
        
        # 计算熵（分布越均匀，熵越高，复杂度越高）
        if sum(power_distribution) == 0:
            return 0.0
        
        # 归一化
        normalized = [p / sum(power_distribution) for p in power_distribution]
        
        # 计算香农熵
        entropy = 0.0
        for p in normalized:
            if p > 0:
                entropy -= p * math.log2(p)
        
        # 最大可能熵
        max_entropy = math.log2(freq_count) if freq_count > 0 else 0
        
        if max_entropy == 0:
            return 0.0
        
        # 归一化熵
        normalized_entropy = entropy / max_entropy
        
        # 结合频率数量
        count_factor = min(1.0, freq_count / 10.0)
        
        # 综合复杂度分数
        complexity = 0.6 * normalized_entropy + 0.4 * count_factor
        return complexity
    
    def _calculate_pattern_quality(self, periodicity: float, complexity: float) -> float:
        """计算模式质量"""
        # 高质量模式：适中的周期性和复杂度
        # 太低：过于简单或随机
        # 太高：过于复杂难以理解
        
        # 理想范围：周期性0.3-0.7，复杂度0.3-0.7
        periodicity_quality = 1.0 - abs(periodicity - 0.5) * 2.0
        complexity_quality = 1.0 - abs(complexity - 0.5) * 2.0
        
        # 综合质量
        quality = 0.5 * periodicity_quality + 0.5 * complexity_quality
        return max(0.0, min(1.0, quality))
    
    def _generate_pattern_insight(self, pattern_type: str, periodicity: float, complexity: float) -> str:
        """生成模式洞察"""
        insights = []
        
        insights.append(f"Pattern type: {pattern_type}")
        
        if periodicity > 0.7:
            insights.append("Highly periodic code - may indicate repetitive patterns that could be refactored.")
        elif periodicity > 0.4:
            insights.append("Moderately periodic - some repetition exists.")
        else:
            insights.append("Low periodicity - code appears diverse or random.")
        
        if complexity > 0.7:
            insights.append("High complexity - code may be difficult to understand or maintain.")
        elif complexity > 0.4:
            insights.append("Moderate complexity - reasonable balance.")
        else:
            insights.append("Low complexity - code may be overly simple or trivial.")
        
        # 基于模式类型的特定洞察
        if pattern_type == "harmonic":
            insights.append("Harmonic patterns detected - code may have nested structures.")
        elif pattern_type == "quasi_periodic":
            insights.append("Quasi-periodic patterns - code has some structure but not strictly periodic.")
        
        return " ".join(insights)
    
    def _generate_fourier_refactoring_recommendation(self, pattern_type: str, frequencies: List[Dict]) -> str:
        """生成傅里叶分析重构建议"""
        recommendations = []
        
        if pattern_type in ["slow_periodic", "fast_periodic", "harmonic"]:
            recommendations.append("Consider extracting repeated patterns into functions or classes.")
        
        if pattern_type == "complex_aperiodic" and len(frequencies) > 5:
            recommendations.append("Code appears highly complex. Consider breaking down into smaller, more focused modules.")
        
        if pattern_type == "random_noise":
            recommendations.append("Code lacks clear patterns. Consider adding more structure and consistency.")
        
        # 基于具体频率的建议
        if frequencies:
            top_freq = frequencies[0]
            if top_freq["power"] > 0.3:
                period = top_freq["period"]
                if period < 10:
                    recommendations.append(f"Short period ({period:.1f} lines) suggests frequent small repetitions.")
                elif period < 50:
                    recommendations.append(f"Medium period ({period:.1f} lines) suggests modular repetitions.")
                else:
                    recommendations.append(f"Long period ({period:.1f} lines) suggests architectural-level patterns.")
        
        if not recommendations:
            recommendations.append("Pattern analysis suggests code structure is reasonable. No major refactoring needed.")
        
        return " ".join(recommendations)
    
    # ==================== 矩阵分解依赖分析 ====================
    
    def matrix_factorization_dependency_analysis(self, dependency_matrix: np.ndarray) -> Dict[str, Any]:
        """
        使用矩阵分解分析代码依赖关系
        """
        try:
            n = dependency_matrix.shape[0]
            if n == 0:
                return {"error": "Empty dependency matrix", "analysis_type": "matrix_factorization"}
            
            # 奇异值分解 (SVD)
            U, S, Vt = np.linalg.svd(dependency_matrix, full_matrices=False)
            
            # 主成分分析
            total_variance = np.sum(S ** 2)
            explained_variance = (S ** 2) / total_variance if total_variance > 0 else np.zeros_like(S)
            cumulative_variance = np.cumsum(explained_variance)
            
            # 识别关键依赖
            critical_dependencies = self._identify_critical_dependencies(U, S, Vt, dependency_matrix)
            
            # 计算耦合度
            coupling_score = self._calculate_coupling_score(dependency_matrix)
            
            # 计算内聚度
            cohesion_score = self._calculate_cohesion_score(dependency_matrix)
            
            # 计算模块化质量
            modularity_quality = self._calculate_modularity_quality(coupling_score, cohesion_score)
            
            # 识别模块边界
            module_boundaries = self._identify_module_boundaries(U, Vt, S)
            
            # 生成重构建议
            refactoring_recommendations = self._generate_matrix_refactoring_recommendations(
                critical_dependencies, coupling_score, cohesion_score, module_boundaries
            )
            
            # 计算架构质量分数
            architecture_quality = self._calculate_architecture_quality(
                coupling_score, cohesion_score, modularity_quality, explained_variance
            )
            
            return {
                "analysis_type": "matrix_factorization",
                "matrix_dimensions": f"{n}x{n}",
                "singular_values": S.tolist(),
                "explained_variance": explained_variance.tolist(),
                "cumulative_variance": cumulative_variance.tolist(),
                "variance_explained_by_top_3": float(np.sum(explained_variance[:3])),
                "critical_dependencies": critical_dependencies,
                "coupling_score": coupling_score,
                "cohesion_score": cohesion_score,
                "modularity_quality": modularity_quality,
                "module_boundaries": module_boundaries,
                "architecture_quality": architecture_quality,
                "refactoring_recommendations": refactoring_recommendations,
                "mathematical_basis": "Dependency structure analyzed via Singular Value Decomposition (SVD)"
            }
            
        except Exception as e:
            return {"error": str(e), "analysis_type": "matrix_factorization"}
    
    def _identify_critical_dependencies(self, U: np.ndarray, S: np.ndarray, Vt: np.ndarray, 
                                      original_matrix: np.ndarray) -> List[Dict]:
        """识别关键依赖"""
        n = U.shape[0]
        critical = []
        
        # 基于奇异值识别最重要的依赖
        for i in range(min(5, len(S))):
            if S[i] > 0.1 * S[0]:  # 显著奇异值
                # 左奇异向量（行重要性）
                u_component = U[:, i]
                # 右奇异向量（列重要性）
                v_component = Vt[i, :]
                
                # 找到最重要的行和列
                max_u_idx = np.argmax(np.abs(u_component))
                max_v_idx = np.argmax(np.abs(v_component))
                
                # 计算依赖强度
                dependency_strength = float(np.abs(u_component[max_u_idx] * v_component[max_v_idx]))
                
                # 获取原始依赖值
                original_strength = float(original_matrix[max_u_idx, max_v_idx])
                
                critical.append({
                    "singular_value_rank": i + 1,
                    "singular_value": float(S[i]),
                    "from_component": int(max_u_idx),
                    "to_component": int(max_v_idx),
                    "dependency_strength": dependency_strength,
                    "original_strength": original_strength,
                    "explained_variance_contribution": float((S[i] ** 2) / np.sum(S ** 2))
                })
        
        return critical
    
    def _calculate_coupling_score(self, matrix: np.ndarray) -> float:
        """计算耦合度分数 (0-1, 越低越好)"""
        n = matrix.shape[0]
        if n == 0:
            return 0.0
        
        # 耦合度 = 非对角线元素强度
        diagonal = np.diag(matrix)
        total_sum = np.sum(matrix)
        diagonal_sum = np.sum(diagonal)
        
        if total_sum == 0:
            return 0.0
        
        # 耦合 = 非对角线元素 / 总元素
        coupling = (total_sum - diagonal_sum) / total_sum
        
        return coupling
    
    def _calculate_cohesion_score(self, matrix: np.ndarray) -> float:
        """计算内聚度分数 (0-1, 越高越好)"""
        n = matrix.shape[0]
        if n == 0:
            return 1.0
        
        # 内聚度 = 对角线元素强度 / 行总和
        cohesion_scores = []
        for i in range(n):
            row_sum = np.sum(matrix[i, :])
            if row_sum > 0:
                cohesion = matrix[i, i] / row_sum
                cohesion_scores.append(cohesion)
        
        if not cohesion_scores:
            return 0.0
        
        return float(np.mean(cohesion_scores))
    
    def _calculate_modularity_quality(self, coupling: float, cohesion: float) -> float:
        """计算模块化质量分数"""
        # 高质量模块：低耦合，高内聚
        return (1 - coupling) * cohesion
    
    def _identify_module_boundaries(self, U: np.ndarray, Vt: np.ndarray, S: np.ndarray) -> List[Dict]:
        """识别模块边界"""
        n = U.shape[0]
        boundaries = []
        
        # 基于前3个奇异向量识别模块
        for i in range(min(3, len(S))):
            if S[i] > 0.1 * S[0]:
                u_vector = U[:, i]
                v_vector = Vt[i, :]
                
                # 找到向量中的显著元素（绝对值大于阈值）
                threshold = 0.3 * np.max(np.abs(u_vector))
                significant_rows = [idx for idx, val in enumerate(u_vector) if abs(val) > threshold]
                
                threshold = 0.3 * np.max(np.abs(v_vector))
                significant_cols = [idx for idx, val in enumerate(v_vector) if abs(val) > threshold]
                
                if significant_rows and significant_cols:
                    boundaries.append({
                        "module_id": i + 1,
                        "singular_value": float(S[i]),
                        "rows_in_module": significant_rows,
                        "cols_in_module": significant_cols,
                        "module_size": len(significant_rows),
                        "explained_variance": float((S[i] ** 2) / np.sum(S ** 2))
                    })
        
        return boundaries
    
    def _generate_matrix_refactoring_recommendations(self, critical_deps, coupling, cohesion, module_boundaries):
        """生成矩阵分析重构建议"""
        recommendations = []
        
        if coupling > 0.3:
            recommendations.append(f"High coupling ({coupling:.2f}) detected. Consider breaking down modules to reduce interdependencies.")
        
        if cohesion < 0.5:
            recommendations.append(f"Low cohesion ({cohesion:.2f}) detected. Consider consolidating related functionality within modules.")
        
        if critical_deps:
            for dep in critical_deps[:3]:
                recommendations.append(
                    f"Critical dependency from component {dep['from_component']} to {dep['to_component']} "
                    f"(strength: {dep['dependency_strength']:.3f}). Consider decoupling."
                )
        
        if module_boundaries:
            recommendations.append(f"Identified {len(module_boundaries)} potential modules via SVD analysis.")
            for module in module_boundaries[:2]:
                recommendations.append(
                    f"Module {module['module_id']}: {module['module_size']} components, "
                    f"explains {module['explained_variance']:.1%} of variance."
                )
        
        if not recommendations:
            recommendations.append("Matrix analysis suggests good modular structure. No major refactoring needed.")
        
        return recommendations
    
    def _calculate_architecture_quality(self, coupling, cohesion, modularity, explained_variance):
        """计算架构质量分数"""
        # 基于多个指标计算综合质量
        coupling_quality = 1.0 - coupling  # 耦合越低越好
        cohesion_quality = cohesion  # 内聚越高越好
        
        # 解释方差质量（前3个成分解释大部分方差）
        variance_explained = sum(explained_variance[:3])
        variance_quality = min(1.0, variance_explained * 1.5)
        
        # 综合质量
        quality = 0.3 * coupling_quality + 0.3 * cohesion_quality + 0.2 * modularity + 0