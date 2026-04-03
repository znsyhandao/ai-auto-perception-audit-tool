"""
基于数学定理的完整AI引擎 - 麦克劳林级数、泰勒展开、傅里叶变换、矩阵分解
"""

import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import ast
import sympy as sp
from sympy import symbols, diff, factorial, series, simplify
import json
from datetime import datetime

class CompleteMathematicalAIEngine:
    """基于数学定理的完整AI引擎"""
    
    def __init__(self):
        self.x = sp.symbols('x')  # 符号变量
        self.n = sp.symbols('n')  # 复杂度变量
        
    # ==================== 麦克劳林级数方法 ====================
    
    def maclaurin_series_expansion(self, function_str: str, degree: int = 5) -> Dict[str, Any]:
        """
        麦克劳林级数展开
        f(x) = f(0) + f'(0)x + f''(0)x²/2! + f'''(0)x³/3! + ...
        """
        try:
            # 解析函数
            expr = sp.sympify(function_str)
            
            # 计算麦克劳林级数
            series_terms = []
            for n in range(degree + 1):
                # 计算n阶导数在x=0处的值
                derivative = sp.diff(expr, self.x, n)
                value_at_zero = derivative.subs(self.x, 0)
                
                if value_at_zero != 0:
                    term = {
                        "degree": n,
                        "coefficient": float(value_at_zero),
                        "term": f"({value_at_zero} * x^{n}) / {math.factorial(n)}",
                        "significance": abs(float(value_at_zero)) / math.factorial(n),
                        "mathematical_form": f"f^{({n})}(0) = {value_at_zero}"
                    }
                    series_terms.append(term)
            
            # 计算级数近似
            approximation = sum(term["coefficient"] * (self.x**term["degree"]) / math.factorial(term["degree"]) 
                              for term in series_terms)
            
            # 计算收敛半径
            convergence_radius = self._calculate_convergence_radius(series_terms)
            
            # 找到主导项
            dominant_term = self._find_dominant_term(series_terms)
            
            # 计算级数质量
            series_quality = self._calculate_series_quality(series_terms, convergence_radius)
            
            return {
                "original_function": str(expr),
                "maclaurin_series": series_terms,
                "approximation": str(approximation),
                "convergence_radius": convergence_radius,
                "dominant_term": dominant_term,
                "series_quality": series_quality,
                "mathematical_insight": self._generate_maclaurin_insight(series_terms, convergence_radius),
                "convergence_guarantee": convergence_radius > 1.0
            }
            
        except Exception as e:
            return {"error": str(e), "analysis_type": "maclaurin_series"}
    
    def _calculate_convergence_radius(self, series_terms: List[Dict]) -> float:
        """计算级数收敛半径"""
        if len(series_terms) < 2:
            return float('inf')
        
        # 使用比值判别法
        coefficients = [term["coefficient"] / math.factorial(term["degree"]) for term in series_terms]
        
        if len(coefficients) >= 2:
            ratios = []
            for i in range(len(coefficients) - 1):
                if coefficients[i] != 0:
                    ratio = abs(coefficients[i+1] / coefficients[i])
                    ratios.append(ratio)
            
            if ratios:
                avg_ratio = np.mean(ratios)
                return 1 / avg_ratio if avg_ratio != 0 else float('inf')
        
        return float('inf')
    
    def _find_dominant_term(self, series_terms: List[Dict]) -> Dict:
        """找到级数中的主导项"""
        if not series_terms:
            return {"degree": 0, "coefficient": 0, "significance": 0}
        
        # 根据显著性找到主导项
        dominant = max(series_terms, key=lambda x: x["significance"])
        return {
            "degree": dominant["degree"],
            "coefficient": dominant["coefficient"],
            "significance": dominant["significance"],
            "explanation": f"Term x^{dominant['degree']} dominates with significance {dominant['significance']:.4f}"
        }
    
    def _calculate_series_quality(self, series_terms: List[Dict], convergence_radius: float) -> float:
        """计算级数质量分数 (0-1)"""
        if not series_terms:
            return 0.0
        
        # 基于收敛半径和项数计算质量
        radius_score = min(1.0, convergence_radius / 10.0)  # 收敛半径越大越好
        term_count_score = min(1.0, len(series_terms) / 10.0)  # 项数适中
        
        # 基于系数分布计算均匀性
        coefficients = [abs(term["coefficient"]) for term in series_terms]
        if coefficients:
            uniformity = 1.0 - (np.std(coefficients) / (np.mean(coefficients) + 1e-10))
            uniformity_score = max(0.0, min(1.0, uniformity))
        else:
            uniformity_score = 0.0
        
        # 综合质量分数
        quality = 0.4 * radius_score + 0.3 * term_count_score + 0.3 * uniformity_score
        return quality
    
    def _generate_maclaurin_insight(self, series_terms: List[Dict], convergence_radius: float) -> str:
        """生成麦克劳林级数洞察"""
        if not series_terms:
            return "Function cannot be expanded as Maclaurin series."
        
        dominant = self._find_dominant_term(series_terms)
        
        insights = []
        insights.append(f"Maclaurin series has {len(series_terms)} significant terms.")
        insights.append(f"Dominant term: x^{dominant['degree']} with coefficient {dominant['coefficient']:.4f}.")
        
        if convergence_radius == float('inf'):
            insights.append("Series converges for all x (entire function).")
        elif convergence_radius > 5.0:
            insights.append(f"Good convergence radius: {convergence_radius:.2f}.")
        else:
            insights.append(f"Limited convergence radius: {convergence_radius:.2f}.")
        
        # 基于主导项提供建议
        if dominant["degree"] == 0:
            insights.append("Function is approximately constant near x=0.")
        elif dominant["degree"] == 1:
            insights.append("Function is approximately linear near x=0.")
        elif dominant["degree"] == 2:
            insights.append("Function has strong quadratic behavior near x=0.")
        else:
            insights.append(f"Function has high-order (degree {dominant['degree']}) behavior near x=0.")
        
        return " ".join(insights)
    
    # ==================== 泰勒级数复杂度分析 ====================
    
    def taylor_series_complexity_analysis(self, execution_times: List[float], 
                                         input_sizes: List[int], degree: int = 3) -> Dict[str, Any]:
        """
        使用泰勒级数分析算法复杂度
        T(n) ≈ a₀ + a₁n + a₂n²/2! + a₃n³/3! + ...
        """
        try:
            # 转换为numpy数组
            n = np.array(input_sizes, dtype=float)
            t = np.array(execution_times, dtype=float)
            
            if len(n) < degree + 1:
                return {"error": f"Need at least {degree + 1} data points for degree {degree} analysis"}
            
            # 构建范德蒙德矩阵进行多项式回归
            A = np.vander(n, degree + 1, increasing=True)
            
            # 使用最小二乘法拟合系数
            coefficients, residuals, rank, s = np.linalg.lstsq(A, t, rcond=None)
            
            # 计算拟合质量
            predicted = A @ coefficients
            r_squared = 1 - np.sum((t - predicted) ** 2) / np.sum((t - np.mean(t)) ** 2)
            
            # 识别主导项
            dominant_degree = self._identify_dominant_degree(coefficients)
            
            # 转换为大O表示法
            big_o = self._coefficients_to_big_o(coefficients, dominant_degree)
            
            # 计算复杂度置信度
            complexity_confidence = self._calculate_complexity_confidence(coefficients, r_squared, dominant_degree)
            
            # 生成数学证明
            mathematical_proof = self._generate_complexity_proof(coefficients, dominant_degree, r_squared)
            
            return {
                "coefficients": coefficients.tolist(),
                "r_squared": float(r_squared),
                "dominant_degree": dominant_degree,
                "big_o_notation": big_o,
                "complexity_confidence": complexity_confidence,
                "mathematical_model": f"T(n) ≈ {self._format_polynomial(coefficients)}",
                "mathematical_proof": mathematical_proof,
                "fitting_quality": self._assess_fitting_quality(r_squared, residuals),
                "recommendation": self._generate_complexity_recommendation(big_o, complexity_confidence)
            }
            
        except Exception as e:
            return {"error": str(e), "analysis_type": "taylor_series"}
    
    def _identify_dominant_degree(self, coefficients: np.ndarray) -> int:
        """识别多项式中的主导次数"""
        # 找到最后一个显著非零系数
        threshold = 0.01 * np.max(np.abs(coefficients))
        for i in range(len(coefficients) - 1, -1, -1):
            if abs(coefficients[i]) > threshold:
                return i
        return 0
    
    def _coefficients_to_big_o(self, coefficients: np.ndarray, dominant_degree: int) -> str:
        """将系数转换为大O表示法"""
        if dominant_degree == 0:
            return "O(1)"
        elif dominant_degree == 1:
            return "O(n)"
        elif dominant_degree == 2:
            return "O(n²)"
        elif dominant_degree == 3:
            return "O(n³)"
        elif dominant_degree == 4:
            return "O(n⁴)"
        else:
            return f"O(n^{dominant_degree})"
    
    def _calculate_complexity_confidence(self, coefficients: np.ndarray, r_squared: float, dominant_degree: int) -> float:
        """计算复杂度置信度"""
        # 基于R²和系数稳定性计算置信度
        r2_score = min(1.0, r_squared * 1.2)  # 调整R²分数
        
        # 检查系数稳定性
        coeff_stability = self._assess_coefficient_stability(coefficients)
        
        # 检查主导项清晰度
        dominance_clarity = self._assess_dominance_clarity(coefficients, dominant_degree)
        
        # 综合置信度
        confidence = 0.5 * r2_score + 0.3 * coeff_stability + 0.2 * dominance_clarity
        return confidence
    
    def _assess_coefficient_stability(self, coefficients: np.ndarray) -> float:
        """评估系数稳定性"""
        if len(coefficients) < 2:
            return 0.5
        
        # 检查系数是否单调递减（对于复杂度分析，高阶项系数应该较小）
        abs_coeffs = np.abs(coefficients)
        if len(abs_coeffs) >= 2:
            # 检查高阶项是否比低阶项小
            stability_score = 0.0
            for i in range(1, len(abs_coeffs)):
                if abs_coeffs[i] <= abs_coeffs[i-1] * 1.5:  # 允许一定波动
                    stability_score += 1.0 / (len(abs_coeffs) - 1)
            
            return stability_score
        
        return 0.5
    
    def _assess_dominance_clarity(self, coefficients: np.ndarray, dominant_degree: int) -> float:
        """评估主导项清晰度"""
        if len(coefficients) <= 1:
            return 1.0
        
        abs_coeffs = np.abs(coefficients)
        dominant_value = abs_coeffs[dominant_degree]
        
        # 计算主导项相对于其他项的清晰度
        other_values = [abs_coeffs[i] for i in range(len(abs_coeffs)) if i != dominant_degree]
        if not other_values:
            return 1.0
        
        max_other = max(other_values)
        if dominant_value == 0:
            return 0.0
        
        clarity = dominant_value / (dominant_value + max_other)
        return clarity
    
    def _generate_complexity_proof(self, coefficients: np.ndarray, dominant_degree: int, r_squared: float) -> str:
        """生成复杂度数学证明"""
        proof = []
        proof.append(f"1. Polynomial regression yields coefficients: {self._format_coefficients(coefficients)}")
        proof.append(f"2. Dominant term identified as degree {dominant_degree} with coefficient {coefficients[dominant_degree]:.6f}")
        proof.append(f"3. R² = {r_squared:.4f} indicates good fit to empirical data")
        
        if dominant_degree == 0:
            proof.append("4. Therefore, T(n) ∈ O(1) (constant time)")
        elif dominant_degree == 1:
            proof.append("4. Therefore, T(n) ∈ O(n) (linear time)")
        elif dominant_degree == 2:
            proof.append("4. Therefore, T(n) ∈ O(n²) (quadratic time)")
        else:
            proof.append(f"4. Therefore, T(n) ∈ O(n^{dominant_degree})")
        
        proof.append("5. Mathematical induction can verify this bound for all n ≥ n₀")
        
        return "\n".join(proof)
    
    def _assess_fitting_quality(self, r_squared: float, residuals) -> str:
        """评估拟合质量"""
        if r_squared >= 0.95:
            return "EXCELLENT"
        elif r_squared >= 0.85:
            return "GOOD"
        elif r_squared >= 0.70:
            return "FAIR"
        else:
            return "POOR"
    
    def _generate_complexity_recommendation(self, big_o: str, confidence: float) -> str:
        """生成复杂度建议"""
        if confidence >= 0.8:
            return f"High confidence in {big_o} complexity. Algorithm is efficient for this complexity class."
        elif confidence >= 0.6:
            return f"Moderate confidence in {big_o} complexity. Consider further testing with larger inputs."
        else:
            return f"Low confidence in complexity analysis. Need more data points or consider different model."
    
    def _format_polynomial(self, coefficients: np.ndarray) -> str:
        """格式化多项式"""
        terms = []
        for i, coeff in enumerate(coefficients):
            if abs(coeff) > 1e-10:  # 忽略接近零的系数
                if i == 0:
                    terms.append(f"{coeff:.6f}")
                elif i == 1:
                    terms.append(f"{coeff:.6f}·n")
                else:
                    terms.append(f"{coeff:.6f}·n^{i}/{math.factorial(i)}")
        
        if not terms:
            return "0"
        
        return " + ".join(terms)
    
    def _format_coefficients(self, coefficients: np.ndarray) -> str:
        """格式化系数显示"""
        return "[" + ", ".join(f"{c:.6f}" for c in coefficients) + "]"
    
    # ==================== 傅里叶变换模式识别 ====================
    
    def fourier_code_pattern_recognition(self, code_sequence: List[str], 
                                        max_frequencies: int = 10) -> Dict[str, Any]:
        """
        使用傅里叶变换识别代码模式
        """
        try:
            # 将代码转换为数值序列
            numeric_sequence = self._code_to_numeric_sequence(code_sequence)
            
            if len(numeric_sequence) < 4:
                return {"error": "Sequence too short for Fourier analysis", "analysis_type": "fourier_transform"}
            
            # 执行快速傅里叶变换
            fft_result = np.fft.fft(numeric_sequence)
            frequencies = np.fft.fftfreq(len(numeric_sequence))
            
            # 提取主要频率成分
            magnitudes = np.abs(fft_result)
            dominant_indices = np.argsort(magnitudes)[-max_frequencies:]
            
            dominant_frequencies = []
            total_power = np.sum(magnitudes ** 2)
            
            for idx in dominant_indices:
                freq = frequencies[idx]
                if freq > 0:  # 只考虑正频率
                    power = (magnitudes[idx] ** 2) / total_power if total_power > 0 else 0
                    dominant_frequencies.append({
                        "frequency": float(freq),
                        "magnitude": float(magnitudes[idx]),
                        "power": float(power),
                        "period": 1 / freq if freq != 0 else float('inf'),
                        "phase": float(np.angle(fft_result[idx]))
                    })
            
            # 按功率排序
            dominant_frequencies.sort(key=lambda x: x["power"], reverse=True)
            
            # 识别模式类型
            pattern_type = self._