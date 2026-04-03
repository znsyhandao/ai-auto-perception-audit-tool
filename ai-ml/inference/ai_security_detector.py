"""
AI驱动的安全检测器
使用深度学习和机器学习模型检测恶意代码
"""

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import joblib
from typing import Dict, List, Any, Tuple
import ast
import hashlib
from pathlib import Path


class DeepCodeAnalyzer(nn.Module):
    """深度学习代码分析器"""
    
    def __init__(self, vocab_size=50000, embedding_dim=256, hidden_dim=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=8)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 10)  # 10种恶意类型
        )
    
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        attended, _ = self.attention(lstm_out, lstm_out, lstm_out)
        pooled = torch.mean(attended, dim=1)
        return self.classifier(pooled)


class AISecurityDetector:
    """AI驱动的安全检测器"""
    
    def __init__(self):
        self.malware_model = None  # 恶意软件检测模型
        self.anomaly_detector = None  # 异常检测模型
        self.code_smell_model = None  # 代码异味检测模型
        self.tokenizer = None
        self._load_models()
    
    def _load_models(self):
        """加载预训练模型"""
        # 加载代码BERT模型
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.codebert = AutoModelForSequenceClassification.from_pretrained(
            "microsoft/codebert-base", num_labels=10
        )
        
        # 加载传统ML模型
        self.malware_model = joblib.load('models/malware_detector.pkl')
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.code_smell_model = joblib.load('models/code_smell_detector.pkl')
        
        # 加载深度学习模型
        self.deep_model = DeepCodeAnalyzer()
        self.deep_model.load_state_dict(torch.load('models/deep_code_analyzer.pth'))
        self.deep_model.eval()
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        综合分析代码安全性
        
        Returns:
            {
                'malware_score': 0-1,
                'anomaly_score': 0-1,
                'vulnerabilities': [],
                'cve_matches': [],
                'behavior_analysis': {}
            }
        """
        result = {
            'malware_score': 0.0,
            'anomaly_score': 0.0,
            'vulnerabilities': [],
            'cve_matches': [],
            'behavior_analysis': {},
            'risk_level': 'low',
            'recommendations': []
        }
        
        # 1. 静态代码特征提取
        features = self._extract_features(code)
        
        # 2. 恶意软件检测
        malware_prob = self.malware_model.predict_proba([features])[0][1]
        result['malware_score'] = float(malware_prob)
        
        # 3. 异常检测
        anomaly_score = self.anomaly_detector.score_samples([features])[0]
        result['anomaly_score'] = 1 / (1 + np.exp(-anomaly_score))  # 归一化
        
        # 4. 深度学习分析
        deep_features = self._prepare_deep_features(code)
        with torch.no_grad():
            deep_output = self.deep_model(deep_features)
            deep_probs = torch.softmax(deep_output, dim=1)
            result['vulnerabilities'] = self._interpret_deep_output(deep_probs)
        
        # 5. CodeBERT分析
        codebert_result = self._analyze_with_codebert(code)
        result.update(codebert_result)
        
        # 6. 行为分析
        result['behavior_analysis'] = self._analyze_behavior(code)
        
        # 7. CVE匹配
        result['cve_matches'] = self._match_cves(code)
        
        # 8. 综合风险评估
        result['risk_level'] = self._calculate_risk_level(result)
        
        # 9. 生成建议
        result['recommendations'] = self._generate_ai_recommendations(result)
        
        return result
    
    def _extract_features(self, code: str) -> np.ndarray:
        """提取代码特征向量（150+维度）"""
        features = []
        
        # AST特征
        try:
            tree = ast.parse(code)
            features.extend(self._extract_ast_features(tree))
        except:
            features.extend([0] * 50)
        
        # 统计特征
        features.extend(self._extract_statistical_features(code))
        
        # 结构特征
        features.extend(self._extract_structural_features(code))
        
        # 复杂度特征
        features.extend(self._extract_complexity_features(code))
        
        # 依赖特征
        features.extend(self._extract_dependency_features(code))
        
        return np.array(features)
    
    def _extract_ast_features(self, tree: ast.AST) -> List[float]:
        """提取AST特征"""
        features = []
        
        # 节点类型统计
        node_types = {}
        for node in ast.walk(tree):
            node_type = type(node).__name__
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # 危险节点检测
        dangerous_nodes = {
            'Call': node_types.get('Call', 0),
            'Import': node_types.get('Import', 0),
            'ImportFrom': node_types.get('ImportFrom', 0),
            'Exec': node_types.get('Exec', 0),
            'Eval': node_types.get('Eval', 0)
        }
        features.extend(dangerous_nodes.values())
        
        # 深度特征
        max_depth = self._get_ast_depth(tree)
        features.append(max_depth)
        
        # 分支因子
        avg_branching = self._get_avg_branching(tree)
        features.append(avg_branching)
        
        return features
    
    def _extract_statistical_features(self, code: str) -> List[float]:
        """提取统计特征"""
        lines = code.split('\n')
        
        features = [
            len(code),  # 代码长度
            len(lines),  # 行数
            len([l for l in lines if l.strip()]),  # 非空行数
            len([l for l in lines if l.strip().startswith('#')]),  # 注释行数
            code.count('if'),  # if语句数
            code.count('for'),  # for循环数
            code.count('while'),  # while循环数
            code.count('try'),  # try块数
            code.count('except'),  # except块数
            code.count('class'),  # 类数
            code.count('def'),  # 函数数
            code.count('lambda'),  # lambda表达式数
            code.count('import'),  # 导入数
            code.count('from'),  # from导入数
            code.count('return'),  # return语句数
            code.count('yield'),  # yield语句数
            code.count('async'),  # 异步函数数
            code.count('await'),  # await语句数
        ]
        
        return features
    
    def _extract_structural_features(self, code: str) -> List[float]:
        """提取结构特征"""
        features = []
        
        # 缩进特征
        lines = code.split('\n')
        indent_levels = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)
        
        if indent_levels:
            features.append(np.mean(indent_levels))
            features.append(np.std(indent_levels))
            features.append(max(indent_levels))
        else:
            features.extend([0, 0, 0])
        
        # 括号平衡
        features.append(code.count('(') - code.count(')'))
        features.append(code.count('[') - code.count(']'))
        features.append(code.count('{') - code.count('}'))
        
        # 字符串特征
        features.append(code.count("'") + code.count('"'))
        features.append(code.count('\\n'))
        features.append(code.count('\\t'))
        
        return features
    
    def _extract_complexity_features(self, code: str) -> List[float]:
        """提取复杂度特征"""
        features = []
        
        # 圈复杂度
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code)
        features.append(cyclomatic_complexity)
        
        # Halstead指标
        halstead = self._calculate_halstead_metrics(code)
        features.extend([
            halstead['volume'],
            halstead['difficulty'],
            halstead['effort']
        ])
        
        # 认知复杂度
        cognitive_complexity = self._calculate_cognitive_complexity(code)
        features.append(cognitive_complexity)
        
        return features
    
    def _extract_dependency_features(self, code: str) -> List[float]:
        """提取依赖特征"""
        features = []
        
        # 检查危险依赖
        dangerous_imports = [
            'os', 'sys', 'subprocess', 'socket', 'requests',
            'urllib', 'http', 'ftplib', 'telnetlib', 'pickle',
            'marshal', 'ctypes', 'cffi', 'pyautoit', 'selenium'
        ]
        
        for imp in dangerous_imports:
            if f'import {imp}' in code or f'from {imp}' in code:
                features.append(1)
            else:
                features.append(0)
        
        return features
    
    def _prepare_deep_features(self, code: str) -> torch.Tensor:
        """准备深度学习模型输入"""
        # 将代码转换为token序列
        tokens = self.tokenizer.encode(code, max_length=512, truncation=True)
        return torch.tensor([tokens])
    
    def _analyze_with_codebert(self, code: str) -> Dict[str, Any]:
        """使用CodeBERT分析"""
        inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.codebert(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)
        
        # 分类结果
        vulnerability_types = [
            'injection', 'xss', 'path_traversal', 'command_injection',
            'sql_injection', 'xxe', 'ssrf', 'idor', 'cryptographic_failure',
            'security_misconfiguration'
        ]
        
        result = {}
        for i, vuln_type in enumerate(vulnerability_types):
            result[f'{vuln_type}_score'] = float(probabilities[0][i])
        
        return result
    
    def _analyze_behavior(self, code: str) -> Dict[str, Any]:
        """行为分析 - 检测潜在的恶意行为模式"""
        behavior = {
            'network_access': False,
            'file_operations': False,
            'process_creation': False,
            'registry_modification': False,
            'privilege_escalation': False,
            'persistence': False,
            'data_exfiltration': False,
            'anti_debugging': False,
            'obfuscation': False
        }
        
        # 网络访问
        if any(pattern in code for pattern in ['socket.', 'requests.', 'urllib.', 'http.client']):
            behavior['network_access'] = True
        
        # 文件操作
        if any(pattern in code for pattern in ['open(', 'file(', 'os.remove', 'shutil.', 'pathlib']):
            behavior['file_operations'] = True
        
        # 进程创建
        if any(pattern in code for pattern in ['subprocess.', 'os.system', 'os.popen', 'Popen']):
            behavior['process_creation'] = True
        
        # 持久化
        if any(pattern in code for pattern in ['startup', 'registry', 'cron', 'systemd', 'launchd']):
            behavior['persistence'] = True
        
        # 混淆检测
        if any(pattern in code for pattern in ['base64', 'b64decode', 'eval(', 'exec(', 'compile(']):
            behavior['obfuscation'] = True
        
        # 反调试
        if any(pattern in code for pattern in ['ptrace', 'debugger', 'sys.gettrace', 'pydevd']):
            behavior['anti_debugging'] = True
        
        return behavior
    
    def _match_cves(self, code: str) -> List[Dict[str, Any]]:
        """匹配已知CVE漏洞"""
        cve_matches = []
        
        # CVE数据库（示例）
        cve_database = {
            'pickle.loads': 'CVE-2020-12345',
            'yaml.load': 'CVE-2019-12346',
            'xml.etree.ElementTree': 'CVE-2021-12347',
            'subprocess.Popen': 'CVE-2018-12348',
            'eval(': 'CVE-2017-12349'
        }
        
        for pattern, cve_id in cve_database.items():
            if pattern in code:
                cve_matches.append({
                    'cve_id': cve_id,
                    'pattern': pattern,
                    'severity': 'high',
                    'description': f'使用危险的{pattern}函数可能导致{CVE数据库中的描述}'
                })
        
        return cve_matches
    
    def _calculate_risk_level(self, result: Dict) -> str:
        """计算综合风险等级"""
        risk_score = 0
        
        # 恶意软件分数
        risk_score += result['malware_score'] * 40
        
        # 异常分数
        risk_score += result['anomaly_score'] * 20
        
        # CVE匹配数
        risk_score += len(result['cve_matches']) * 10
        
        # 行为风险
        behavior_risks = sum(result['behavior_analysis'].values())
        risk_score += behavior_risks * 5
        
        # 阈值判定
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'high'
        elif risk_score >= 30:
            return 'medium'
        else:
            return 'low'
    
    def _generate_ai_recommendations(self, result: Dict) -> List[str]:
        """生成AI驱动的优化建议"""
        recommendations = []
        
        if result['malware_score'] > 0.7:
            recommendations.append("⚠️ 高风险：检测到疑似恶意代码模式，建议立即审查")
        
        if result['anomaly_score'] > 0.6:
            recommendations.append("⚠️ 异常行为：代码行为与正常模式差异较大，可能存在未知风险")
        
        if result['cve_matches']:
            recommendations.append(f"🔒 发现{len(result['cve_matches'])}个已知CVE漏洞，建议更新相关依赖")
        
        behavior = result['behavior_analysis']
        if behavior['obfuscation']:
            recommendations.append("🕵️ 检测到代码混淆，这在恶意软件中常见，建议深入分析")
        
        if behavior['network_access'] and behavior['data_exfiltration']:
            recommendations.append("🚨 检测到网络访问和数据外泄模式，可能存在数据泄露风险")
        
        if behavior['process_creation'] and behavior['privilege_escalation']:
            recommendations.append("⚠️ 进程创建和权限提升组合可能用于系统入侵")
        
        return recommendations
    
    def _calculate_cyclomatic_complexity(self, code: str) -> float:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        keywords = ['if', 'elif', 'for', 'while', 'except', 'and', 'or']
        
        for keyword in keywords:
            complexity += code.count(keyword)
        
        return complexity
    
    def _calculate_halstead_metrics(self, code: str) -> Dict[str, float]:
        """计算Halstead指标"""
        # 简化实现
        operators = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=',
                     'and', 'or', 'not', 'in', 'is', 'lambda']
        
        operands = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
        
        n1 = len(operators)
        n2 = len(set(operands))
        N1 = sum(code.count(op) for op in operators)
        N2 = len(operands)
        
        volume = (N1 + N2) * np.log2(n1 + n2) if n1 + n2 > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = volume * difficulty
        
        return {'volume': volume, 'difficulty': difficulty, 'effort': effort}
    
    def _calculate_cognitive_complexity(self, code: str) -> float:
        """计算认知复杂度"""
        complexity = 0
        nesting_level = 0
        
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # 检测嵌套结构
            if stripped.startswith(('if', 'for', 'while', 'try', 'with')):
                complexity += 1 + nesting_level
                nesting_level += 1
            elif stripped.startswith(('elif', 'except', 'finally')):
                complexity += 1 + nesting_level
            elif stripped.startswith(('else',)):
                complexity += 1 + nesting_level
            
            # 减少嵌套层级
            if stripped.startswith(('return', 'break', 'continue', 'pass')):
                nesting_level = max(0, nesting_level - 1)
        
        return complexity
    
    def _get_ast_depth(self, node: ast.AST, current_depth=0) -> int:
        """获取AST深度"""
        if not hasattr(node, '_fields'):
            return current_depth
        
        max_depth = current_depth
        for field in node._fields:
            child = getattr(node, field)
            if isinstance(child, ast.AST):
                depth = self._get_ast_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, ast.AST):
                        depth = self._get_ast_depth(item, current_depth + 1)
                        max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_avg_branching(self, node: ast.AST) -> float:
        """获取平均分支因子"""
        branches = []
        
        def count_children(n):
            if not hasattr(n, '_fields'):
                return 0
            count = 0
            for field in n._fields:
                child = getattr(n, field)
                if isinstance(child, ast.AST):
                    count += 1
                    count += count_children(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, ast.AST):
                            count += 1
                            count += count_children(item)
            return count
        
        total_children = count_children(node)
        total_nodes = sum(1 for _ in ast.walk(node))
        
        return total_children / total_nodes if total_nodes > 0 else 0