"""
部署数学审核服务到测试环境
"""

import os
import subprocess
import time
import requests
import json
from pathlib import Path

def check_docker_environment():
    """检查Docker环境"""
    print("1. Checking Docker environment...")
    
    try:
        # 检查Docker是否安装
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   Docker installed: {result.stdout.strip()}")
        else:
            print("   ERROR: Docker not installed or not in PATH")
            return False
        
        # 检查Docker服务是否运行
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   Docker service is running")
        else:
            print("   ERROR: Docker service not running")
            return False
        
        return True
        
    except Exception as e:
        print(f"   Docker check error: {e}")
        return False

def build_docker_image():
    """构建Docker镜像"""
    print("\n2. Building Docker image...")
    
    try:
        # 创建临时部署目录
        deploy_dir = Path('test_deployment')
        deploy_dir.mkdir(exist_ok=True)
        
        # 复制Dockerfile
        dockerfile_src = Path('Dockerfile.mathematical')
        dockerfile_dst = deploy_dir / 'Dockerfile'
        
        if dockerfile_src.exists():
            dockerfile_src.copy(dockerfile_dst)
            print("   Copied Dockerfile")
        else:
            print("   ERROR: Dockerfile.mathematical not found")
            return False
        
        # 复制需求文件
        req_src = Path('requirements_mathematical.txt')
        req_dst = deploy_dir / 'requirements.txt'
        
        if req_src.exists():
            req_src.copy(req_dst)
            print("   Copied requirements.txt")
        else:
            # 创建默认需求文件
            with open(req_dst, 'w') as f:
                f.write("fastapi==0.104.1\nuvicorn[standard]==0.24.0\npydantic==2.5.0\nnumpy==1.24.3\n")
            print("   Created requirements.txt")
        
        # 复制服务代码
        service_src = Path('microservices/mathematical-audit-service')
        service_dst = deploy_dir / 'service'
        
        if service_src.exists():
            import shutil
            if service_dst.exists():
                shutil.rmtree(service_dst)
            shutil.copytree(service_src, service_dst)
            print("   Copied service code")
        else:
            print("   ERROR: Service code not found")
            return False
        
        # 构建Docker镜像
        print("   Building image...")
        build_cmd = ['docker', 'build', '-t', 'mathematical-audit-test:latest', '.']
        
        result = subprocess.run(
            build_cmd,
            cwd=deploy_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("   Docker image built successfully")
            return True
        else:
            print(f"   Docker build failed: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ERROR: Docker build timeout (5 minutes)")
        return False
    except Exception as e:
        print(f"   Build error: {e}")
        return False

def run_test_container():
    """运行测试容器"""
    print("\n3. Running test container...")
    
    try:
        # 停止现有容器
        stop_cmd = ['docker', 'stop', 'mathematical-audit-test', '2>nul', '||', 'true']
        subprocess.run(' '.join(stop_cmd), shell=True, capture_output=True)
        
        # 删除现有容器
        rm_cmd = ['docker', 'rm', 'mathematical-audit-test', '2>nul', '||', 'true']
        subprocess.run(' '.join(rm_cmd), shell=True, capture_output=True)
        
        # 运行新容器
        run_cmd = [
            'docker', 'run',
            '-d',
            '--name', 'mathematical-audit-test',
            '-p', '8020:8010',  # 测试环境使用8020端口
            'mathematical-audit-test:latest'
        ]
        
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"   Container started: {container_id[:12]}")
            print(f"   Port mapping: 8020 -> 8010")
            return True
        else:
            print(f"   Container start failed: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"   Container error: {e}")
        return False

def wait_for_service_start():
    """等待服务启动"""
    print("\n4. Waiting for service to start...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:8020/health', timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"   Service started successfully (attempt {attempt + 1}/{max_attempts})")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                return True
        except:
            pass
        
        print(f"   Waiting... ({attempt + 1}/{max_attempts})")
        time.sleep(3)
    
    print("   ERROR: Service did not start within timeout")
    return False

def test_service_functionality():
    """测试服务功能"""
    print("\n5. Testing service functionality...")
    
    tests = [
        {
            'name': 'Health check',
            'method': 'GET',
            'url': 'http://localhost:8020/health',
            'expected_status': 200
        },
        {
            'name': 'Single audit (maclaurin)',
            'method': 'POST',
            'url': 'http://localhost:8020/audit',
            'data': {
                'skill_id': 'test-skill',
                'skill_path': 'test/path',
                'audit_types': ['maclaurin'],
                'mathematical_depth': 3
            },
            'expected_status': 200
        },
        {
            'name': 'Full audit (all types)',
            'method': 'POST',
            'url': 'http://localhost:8020/audit',
            'data': {
                'skill_id': 'test-skill-full',
                'skill_path': 'test/path',
                'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
                'mathematical_depth': 5
            },
            'expected_status': 200
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"   Testing: {test['name']}...")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=5)
            else:  # POST
                response = requests.post(
                    test['url'],
                    json=test['data'],
                    timeout=10
                )
            
            if response.status_code == test['expected_status']:
                print(f"     PASS")
                passed += 1
                
                if test['name'] == 'Full audit (all types)':
                    result = response.json()
                    score = result.get('overall_mathematical_score', 0)
                    certs = len(result.get('mathematical_certificates', []))
                    print(f"     Score: {score}, Certificates: {certs}")
            else:
                print(f"     FAIL: HTTP {response.status_code}")
                failed += 1
                
        except Exception as e:
            print(f"     ERROR: {e}")
            failed += 1
    
    print(f"\n   Test results: {passed} passed, {failed} failed")
    return failed == 0

def check_container_logs():
    """检查容器日志"""
    print("\n6. Checking container logs...")
    
    try:
        logs_cmd = ['docker', 'logs', '--tail', '20', 'mathematical-audit-test']
        result = subprocess.run(logs_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Recent logs:")
            for line in result.stdout.strip().split('\n')[-5:]:
                print(f"     {line}")
        else:
            print(f"   Log check failed: {result.stderr}")
            
    except Exception as e:
        print(f"   Log error: {e}")

def generate_deployment_report():
    """生成部署报告"""
    print("\n7. Generating deployment report...")
    
    report = {
        'deployment_id': f'TEST_DEPLOY_{int(time.time())}',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'environment': 'test',
        'service': 'mathematical-audit-service',
        'version': '4.0.0',
        'port': 8020,
        'docker_image': 'mathematical-audit-test:latest',
        'container_name': 'mathematical-audit-test',
        'health_check': 'http://localhost:8020/health',
        'api_docs': 'http://localhost:8020/docs',
        'tests': {
            'docker_environment': 'checked',
            'image_built': 'success',
            'container_running': 'success',
            'service_healthy': 'success',
            'functionality_tests': 'passed'
        },
        'next_steps': [
            '1. Verify service at http://localhost:8020/health',
            '2. Test API at http://localhost:8020/docs',
            '3. Run extended load tests',
            '4. Monitor logs for errors'
        ]
    }
    
    report_file = 'test_deployment_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"   Report saved: {report_file}")
    return report

def main():
    """主部署函数"""
    print("DEPLOYING MATHEMATICAL AUDIT SERVICE TO TEST ENVIRONMENT")
    print("=" * 70)
    
    steps = [
        ("Checking Docker environment", check_docker_environment),
        ("Building Docker image", build_docker_image),
        ("Running test container", run_test_container),
        ("Waiting for service start", wait_for_service_start),
        ("Testing service functionality", test_service_functionality),
        ("Checking container logs", check_container_logs),
        ("Generating deployment report", generate_deployment_report)
    ]
    
    all_passed = True
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if step_func():
            print(f"  PASS")
        else:
            print(f"  FAIL")
            all_passed = False
            break
    
    print("\n" + "=" * 70)
    if all_passed:
        print("DEPLOYMENT SUCCESSFUL!")
        print("Mathematical audit service is now running in test environment.")
        print("\nAccess points:")
        print("  Health check: http://localhost:8020/health")
        print("  API docs:     http://localhost:8020/docs")
        print("  Test audit:   POST http://localhost:8020/audit")
        print("\nNext: Begin integration with enterprise framework (Phase B)")
    else:
        print("DEPLOYMENT FAILED")
        print("Check errors above and fix before retrying.")
    
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)