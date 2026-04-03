#!/usr/bin/env python3
"""
AI审核守护进程 - 24/7自动运行，感知问题，学习经验，升级框架
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread, Event
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "ai_audit_daemon.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AI_Audit_Daemon")

class AIAuditDaemon:
    """AI审核守护进程"""
    
    def __init__(self):
        self.running = Event()
        self.running.set()
        
        # 配置
        self.config = self._load_config()
        
        # 状态
        self.status = {
            "started_at": datetime.now().isoformat(),
            "last_maintenance": None,
            "last_audit": None,
            "last_learning": None,
            "last_upgrade": None,
            "total_audits": 0,
            "total_lessons_learned": 0,
            "total_upgrades": 0,
            "errors": []
        }
        
        # 信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🤖 AI审核守护进程初始化")
    
    def _load_config(self):
        """加载配置"""
        config_path = Path(__file__).parent / "ai_daemon_config.json"
        
        default_config = {
            "check_interval_minutes": 30,  # 检查间隔
            "maintenance_interval_hours": 24,  # 维护间隔
            "auto_learn": True,
            "auto_fix": True,
            "auto_upgrade": True,
            "monitor_directories": [
                str(Path.home() / ".openclaw" / "workspace" / "releases"),
                str(Path.home() / ".openclaw" / "workspace" / "skills")
            ],
            "backup_retention_days": 7,
            "log_level": "INFO"
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
        
        return default_config
    
    def signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"收到信号 {signum}，正在关闭...")
        self.running.clear()
    
    def run(self):
        """运行守护进程"""
        logger.info("🚀 AI审核守护进程启动")
        logger.info(f"配置: {json.dumps(self.config, indent=2, ensure_ascii=False)}")
        
        # 启动监控线程
        threads = [
            Thread(target=self.monitor_loop, name="MonitorLoop"),
            Thread(target=self.maintenance_loop, name="MaintenanceLoop"),
            Thread(target=self.status_report_loop, name="StatusReportLoop")
        ]
        
        for thread in threads:
            thread.daemon = True
            thread.start()
        
        # 主循环
        try:
            while self.running.is_set():
                time.sleep(1)
                
                # 检查线程状态
                for thread in threads:
                    if not thread.is_alive():
                        logger.error(f"线程 {thread.name} 已停止，重新启动...")
                        thread = Thread(target=getattr(self, thread.name.lower()), name=thread.name)
                        thread.daemon = True
                        thread.start()
                        
        except KeyboardInterrupt:
            logger.info("用户中断")
        except Exception as e:
            logger.error(f"主循环出错: {e}")
        finally:
            self.shutdown()
    
    def monitor_loop(self):
        """监控循环"""
        logger.info("👀 开始监控循环")
        
        last_check = datetime.now() - timedelta(minutes=self.config["check_interval_minutes"])
        
        while self.running.is_set():
            try:
                now = datetime.now()
                
                # 检查是否需要运行
                if (now - last_check).total_seconds() >= self.config["check_interval_minutes"] * 60:
                    logger.info("⏰ 执行定期检查")
                    
                    # 检查监控目录
                    for dir_path in self.config["monitor_directories"]:
                        if Path(dir_path).exists():
                            self.check_directory(dir_path)
                    
                    last_check = now
                    self.status["last_audit"] = now.isoformat()
                
                time.sleep(10)  # 短暂休眠
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                self.status["errors"].append(f"监控循环: {e}")
                time.sleep(60)  # 出错后等待更长时间
    
    def check_directory(self, dir_path):
        """检查目录"""
        try:
            dir_obj = Path(dir_path)
            
            # 查找技能目录
            for item in dir_obj.iterdir():
                if item.is_dir():
                    # 检查是否是技能目录（有skill.py文件）
                    skill_file = item / "skill.py"
                    if skill_file.exists():
                        logger.info(f"🔍 发现技能目录: {item.name}")
                        
                        # 检查是否需要审核
                        if self.needs_audit(item):
                            self.audit_skill(item)
            
        except Exception as e:
            logger.error(f"检查目录 {dir_path} 出错: {e}")
    
    def needs_audit(self, skill_dir):
        """检查技能是否需要审核"""
        try:
            # 检查最后修改时间
            skill_file = skill_dir / "skill.py"
            if skill_file.exists():
                mtime = datetime.fromtimestamp(skill_file.stat().st_mtime)
                
                # 检查是否有审核报告
                audit_report = skill_dir / "ai_enhanced_audit_report.json"
                if audit_report.exists():
                    report_mtime = datetime.fromtimestamp(audit_report.stat().st_mtime)
                    
                    # 如果技能文件比审核报告新，需要重新审核
                    if mtime > report_mtime:
                        return True
                else:
                    # 没有审核报告，需要审核
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查是否需要审核出错 {skill_dir}: {e}")
            return False
    
    def audit_skill(self, skill_dir):
        """审核技能"""
        try:
            logger.info(f"📊 开始审核技能: {skill_dir.name}")
            
            # 导入AI系统
            sys.path.insert(0, str(Path(__file__).parent))
            
            try:
                from ai_self_evolving_audit import AISelfEvolvingAudit
                
                # 创建AI系统实例
                ai_system = AISelfEvolvingAudit()
                
                # 设置模式
                ai_system.learning_mode = self.config["auto_learn"]
                ai_system.auto_fix_mode = self.config["auto_fix"]
                ai_system.auto_upgrade_mode = self.config["auto_upgrade"]
                
                # 运行审核
                report = ai_system.audit_skill(str(skill_dir))
                
                self.status["total_audits"] += 1
                logger.info(f"✅ 技能审核完成: {skill_dir.name}")
                
                # 检查是否学习了新经验
                if hasattr(ai_system, 'experience_lessons'):
                    new_lessons = len(ai_system.experience_lessons) - self.status.get("last_lesson_count", 0)
                    if new_lessons > 0:
                        self.status["total_lessons_learned"] += new_lessons
                        self.status["last_learning"] = datetime.now().isoformat()
                        logger.info(f"🎓 学习了 {new_lessons} 个新经验教训")
                
                return True
                
            except ImportError as e:
                logger.error(f"导入AI系统失败: {e}")
                return False
                
        except Exception as e:
            logger.error(f"审核技能 {skill_dir} 出错: {e}")
            self.status["errors"].append(f"审核技能 {skill_dir}: {e}")
            return False
    
    def maintenance_loop(self):
        """维护循环"""
        logger.info("🛠️  开始维护循环")
        
        last_maintenance = None
        
        while self.running.is_set():
            try:
                now = datetime.now()
                
                # 检查是否需要维护
                needs_maintenance = False
                
                if last_maintenance is None:
                    needs_maintenance = True
                elif (now - last_maintenance).total_seconds() >= self.config["maintenance_interval_hours"] * 3600:
                    needs_maintenance = True
                
                if needs_maintenance:
                    logger.info("🔧 执行定期维护")
                    
                    # 运行维护
                    self.run_maintenance()
                    
                    last_maintenance = now
                    self.status["last_maintenance"] = now.isoformat()
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"维护循环出错: {e}")
                self.status["errors"].append(f"维护循环: {e}")
                time.sleep(300)  # 出错后等待5分钟
    
    def run_maintenance(self):
        """运行维护"""
        try:
            # 导入AI系统
            sys.path.insert(0, str(Path(__file__).parent))
            
            from ai_self_evolving_audit import AISelfEvolvingAudit
            
            # 创建AI系统实例
            ai_system = AISelfEvolvingAudit()
            
            # 运行每日维护
            ai_system.run_daily_maintenance()
            
            # 检查是否有升级
            if hasattr(ai_system, 'framework_upgrades'):
                new_upgrades = len(ai_system.framework_upgrades) - self.status.get("last_upgrade_count", 0)
                if new_upgrades > 0:
                    self.status["total_upgrades"] += new_upgrades
                    self.status["last_upgrade"] = datetime.now().isoformat()
                    logger.info(f"🔄 完成了 {new_upgrades} 个框架升级")
            
            logger.info("✅ 维护完成")
            
        except Exception as e:
            logger.error(f"运行维护出错: {e}")
            self.status["errors"].append(f"运行维护: {e}")
    
    def status_report_loop(self):
        """状态报告循环"""
        logger.info("📈 开始状态报告循环")
        
        while self.running.is_set():
            try:
                # 每小时报告一次状态
                time.sleep(3600)
                
                self.report_status()
                
            except Exception as e:
                logger.error(f"状态报告循环出错: {e}")
                time.sleep(60)
    
    def report_status(self):
        """报告状态"""
        try:
            # 保存状态到文件
            status_path = Path(__file__).parent / "ai_daemon_status.json"
            
            # 更新运行时间
            self.status["uptime"] = str(datetime.now() - datetime.fromisoformat(self.status["started_at"]))
            self.status["last_report"] = datetime.now().isoformat()
            
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, indent=2, ensure_ascii=False)
            
            # 日志报告
            logger.info("📊 状态报告:")
            logger.info(f"   运行时间: {self.status['uptime']}")
            logger.info(f"   总审核数: {self.status['total_audits']}")
            logger.info(f"   总经验教训: {self.status['total_lessons_learned']}")
            logger.info(f"   总升级数: {self.status['total_upgrades']}")
            logger.info(f"   错误数: {len(self.status['errors'])}")
            
            # 清除旧错误
            if len(self.status["errors"]) > 10:
                self.status["errors"] = self.status["errors"][-10:]
                
        except Exception as e:
            logger.error(f"报告状态出错: {e}")
    
    def shutdown(self):
        """关闭守护进程"""
        logger.info("🛑 正在关闭AI审核守护进程...")
        
        # 保存最终状态
        self.status["shutdown_at"] = datetime.now().isoformat()
        self.report_status()
        
        logger.info("👋 AI审核守护进程已关闭")

def main():
    """主函数"""
    print("🤖 AI审核守护进程")
    print("=" * 50)
    
    # 检查是否以守护进程模式运行
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        print("以守护进程模式运行...")
        print("日志文件: ai_audit_daemon.log")
        print("状态文件: ai_daemon_status.json")
        print("按 Ctrl+C 停止")
        print("-" * 50)
        
        # 运行守护进程
        daemon = AIAuditDaemon()
        daemon.run()
        
    else:
        # 交互式模式
        print("交互式命令:")
        print("  --daemon    以守护进程模式运行")
        print("  --status    查看守护进程状态")
        print("  --stop      停止守护进程")
        print("  --start     启动守护进程")
        print("  --restart   重启守护进程")
        
        # 检查守护进程状态
        status_path = Path(__file__).parent / "ai_daemon_status.json"
        if status_path.exists():
            try:
                with open(status_path, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                
                print(f"\n📊 守护进程状态:")
                print(f"   最后启动: {status.get('started_at', '未知')}")
                print(f"   最后报告: {status.get('last_report', '未知')}")
                print(f"   总审核数: {status.get('total_audits', 0)}")
                print(f"   总经验教训: {status.get('total_lessons_learned', 0)}")
                
            except Exception as e:
                print(f"读取状态失败: {e}")

if __name__ == "__main__":
    main()