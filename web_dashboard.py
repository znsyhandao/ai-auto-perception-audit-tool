#!/usr/bin/env python3
"""
企业级审核框架 v3.0 - Web仪表板
基本的可视化界面
"""

import os
import sys
import json
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 尝试导入Flask
try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[WARNING] Flask not installed. Installing...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        from flask import Flask, render_template, jsonify, request, send_from_directory
        FLASK_AVAILABLE = True
        print("[SUCCESS] Flask installed successfully")
    except:
        print("[ERROR] Failed to install Flask")

class WebDashboard:
    """Web仪表板"""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = None
        self.reports_dir = "dashboard_reports"
        self.static_dir = "static"
        
        # 创建必要的目录
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        
        # 创建CSS文件
        self.create_css_file()
        
        if FLASK_AVAILABLE:
            self.setup_flask_app()
    
    def create_css_file(self):
        """创建CSS文件"""
        css_content = """
/* 企业级审核框架仪表板样式 */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f7fa;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
    padding: 30px;
}

.header {
    text-align: center;
    margin-bottom: 40px;
    border-bottom: 2px solid #eaeaea;
    padding-bottom: 20px;
}

.header h1 {
    color: #2c3e50;
    margin: 0;
    font-size: 2.5em;
}

.header .subtitle {
    color: #7f8c8d;
    font-size: 1.2em;
    margin-top: 10px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-left: 4px solid #3498db;
}

.card.critical {
    border-left-color: #e74c3c;
}

.card.high {
    border-left-color: #e67e22;
}

.card.medium {
    border-left-color: #f39c12;
}

.card.low {
    border-left-color: #27ae60;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.card-title {
    font-size: 1.2em;
    font-weight: 600;
    color: #2c3e50;
}

.card-value {
    font-size: 2em;
    font-weight: 700;
}

.risk-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 600;
    color: white;
}

.risk-critical { background-color: #e74c3c; }
.risk-high { background-color: #e67e22; }
.risk-medium { background-color: #f39c12; }
.risk-low { background-color: #27ae60; }

.chart-container {
    height: 200px;
    margin: 20px 0;
}

.issues-list {
    margin-top: 20px;
}

.issue-item {
    padding: 10px;
    margin: 5px 0;
    background: #f8f9fa;
    border-radius: 4px;
    border-left: 3px solid #3498db;
}

.issue-item.critical {
    border-left-color: #e74c3c;
    background: #ffeaea;
}

.issue-item.high {
    border-left-color: #e67e22;
    background: #fff3e6;
}

.issue-item.medium {
    border-left-color: #f39c12;
    background: #fff9e6;
}

.issue-item.low {
    border-left-color: #27ae60;
    background: #e8f7ef;
}

.issue-severity {
    font-weight: 600;
    margin-right: 10px;
}

.issue-description {
    color: #555;
}

.controls {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
}

.btn-primary {
    background-color: #3498db;
    color: white;
}

.btn-primary:hover {
    background-color: #2980b9;
}

.btn-secondary {
    background-color: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background-color: #7f8c8d;
}

.btn-danger {
    background-color: #e74c3c;
    color: white;
}

.btn-danger:hover {
    background-color: #c0392b;
}

.footer {
    text-align: center;
    margin-top: 40px;
    color: #7f8c8d;
    font-size: 0.9em;
    border-top: 1px solid #eaeaea;
    padding-top: 20px;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #7f8c8d;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 15px;
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .header h1 {
        font-size: 2em;
    }
}
"""
        
        css_path = os.path.join(self.static_dir, "style.css")
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def setup_flask_app(self):
        """设置Flask应用"""
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.app = Flask(__name__, 
                        static_folder=self.static_dir,
                        template_folder=template_dir)
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/reports')
        def list_reports():
            return self.api_list_reports()
        
        @self.app.route('/api/report/<report_id>')
        def get_report(report_id):
            return self.api_get_report(report_id)
        
        @self.app.route('/api/scan', methods=['POST'])
        def scan_skill():
            return self.api_scan_skill()
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory(self.static_dir, filename)
    

    
    def api_list_reports(self):
        """API: 列出所有报告"""
        reports = []
        
        # 扫描报告目录
        for file in Path(self.reports_dir).glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                reports.append({
                    "id": file.stem,
                    "filename": file.name,
                    "timestamp": data.get("scan_timestamp", ""),
                    "skill_directory": data.get("skill_directory", ""),
                    "risk_score": data.get("combined_risk_score", 0)
                })
            except:
                continue
        
        # 按时间排序（最新的在前）
        reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return jsonify(reports)
    
    def api_get_report(self, report_id):
        """API: 获取单个报告"""
        report_path = os.path.join(self.reports_dir, f"{report_id}.json")
        
        if not os.path.exists(report_path):
            return jsonify({"error": "Report not found"}), 404
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 添加报告ID
            data["id"] = report_id
            
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def api_scan_skill(self):
        """API: 扫描技能"""
        try:
            data = request.json
            skill_dir = data.get("skill_directory", "")
            
            if not skill_dir or not os.path.exists(skill_dir):
                return jsonify({"error": "Invalid skill directory"}), 400
            
            # 这里可以调用实际的扫描逻辑
            # 暂时返回模拟结果
            result = {
                "id": f"scan-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "skill_directory": skill_dir,
                "combined_risk_score": 65.5,
                "risk_level": "HIGH",
                "summary": {
                    "enterprise_scan": {
                        "ai_analysis": {
                            "quality_score": 0.72,
                            "malware_detections": [
                                {"type": "obfuscated_code", "pattern": "__import__"}
                            ]
                        },
                        "sandbox_execution": {
                            "security_score": 55,
                            "policy_violations": 2
                        }
                    },
                    "v2_deep_analysis": {
                        "ast_analysis": {"issues_count": 4},
                        "deep_analysis_suite": {"summary": {"total_issues": 23}}
                    }
                }
            }
            
            # 保存报告
            report_path = os.path.join(self.reports_dir, f"{result['id']}.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def start(self):
        """启动Web服务器"""
        if not FLASK_AVAILABLE:
            print("[ERROR] Flask is not available. Cannot start web dashboard.")
            print("[INFO] Please install Flask: pip install flask")
            return False
        
        print(f"[INFO] Starting Web Dashboard on http://localhost:{self.port}")
        print("[INFO] Press Ctrl+C to stop the server")
        
        # 在后台线程中启动Flask
        def run_flask():
            self.app.run(debug=False, port=self.port, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # 等待服务器启动
        import time
        time.sleep(2)
        
        # 打开浏览器
        try:
            webbrowser.open(f"http://localhost:{self.port}")
        except:
            print(f"[INFO] Please open http://localhost:{self.port} in your browser")
        
        return True
    
    def stop(self):
        """停止Web服务器"""
        # Flask服务器在后台线程中运行，主程序退出时会自动停止
        print("[INFO] Web Dashboard stopped")

def main():
    """主函数"""
    print("=" * 60)
    print("Enterprise Audit Framework v3.0 - Web Dashboard")
    print("=" * 60)
    
    # 检查Flask是否可用
    global FLASK_AVAILABLE
    if not FLASK_AVAILABLE:
        print("[ERROR] Flask is required but not installed.")
        print("[INFO] Attempting to install Flask...")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
            print("[SUCCESS] Flask installed successfully")
            
            # 重新导入
            from flask import Flask, render_template, jsonify, request, send_from_directory
            FLASK_AVAILABLE = True
        except Exception as e:
            print(f"[ERROR] Failed to install Flask: {e}")
            print("[INFO] Please install Flask manually: pip install flask")
            return 1
    
    # 创建并启动仪表板
    dashboard = WebDashboard(port=5000)
    
    if dashboard.start():
        try:
            # 保持主线程运行
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            dashboard.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
