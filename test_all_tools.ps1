# test_all_tools.ps1
# 测试所有深度分析工具

param(
    [string]$TestDir = ".\test_data",
    [switch]$InstallDeps = $true
)

Write-Host "=== Testing All Deep Analysis Tools ===" -ForegroundColor Cyan
Write-Host "Test Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# 创建测试目录
if (-not (Test-Path $TestDir)) {
    New-Item -ItemType Directory -Path $TestDir -Force | Out-Null
    Write-Host "Created test directory: $TestDir" -ForegroundColor Green
}

# 安装依赖
if ($InstallDeps) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    try {
        pip install networkx 2>&1 | Out-Null
        Write-Host "  [OK] Installed networkx" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Failed to install networkx: $_" -ForegroundColor Yellow
    }
}

# 创建测试文件
Write-Host "`nCreating test files..." -ForegroundColor Yellow

# 1. 创建有问题的测试文件
$problematicCode = @'
# test_problematic.py
# 包含各种问题的测试文件

import os
import sys
import pickle  # 危险导入
import marshal  # 危险导入

def infinite_loop():
    while True:  # 无限循环
        pass

def unreachable_code():
    return 42
    print("This is unreachable")  # 不可达代码

def dangerous_function():
    # 危险函数调用
    eval("print('dangerous')")
    exec("x = 1")
    os.system("dir")  # 系统命令
    
def sensitive_data():
    password = "secret123"  # 敏感数据
    api_key = "sk_test_123456"
    return password + api_key

def inefficient_algorithm():
    # 低效算法
    result = []
    for i in range(1000):
        for j in range(1000):
            for k in range(1000):  # 三层嵌套循环
                result.append(i + j + k)
    return result

def unvalidated_input(user_input):
    # 未验证的输入
    return eval(user_input)  # 直接执行用户输入

def resource_leak():
    # 资源泄漏
    f = open("test.txt", "w")
    # 忘记关闭文件
    f.write("test")
    # 应该有关闭: f.close()

class TestClass:
    def __init__(self):
        self.data = "test"
    
    def complex_method(self):
        # 高复杂度方法
        if True:
            if False:
                for i in range(10):
                    while True:
                        try:
                            pass
                        except:
                            pass
        return self.data
'@

$testFile = Join-Path $TestDir "test_problematic.py"
$problematicCode | Out-File -FilePath $testFile -Encoding UTF8
Write-Host "  [OK] Created problematic test file: $testFile" -ForegroundColor Green

# 2. 创建干净的测试文件
$cleanCode = @"
# test_clean.py
# 干净的测试文件

import json
import math

def calculate_statistics(data):
    """计算统计数据"""
    if not data:
        return {}
    
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = math.sqrt(variance)
    
    return {
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "count": len(data)
    }

def process_data_safely(data):
    """安全处理数据"""
    try:
        parsed = json.loads(data)
        return calculate_statistics(parsed.get("values", []))
    except Exception as e:
        return {"error": str(e)}

def main():
    """主函数"""
    test_data = '{"values": [1.0, 2.0, 3.0, 4.0, 5.0]}'
    result = process_data_safely(test_data)
    print("Result: {}".format(result))
    
    # 正确的资源管理
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
"@

$cleanFile = Join-Path $TestDir "test_clean.py"
$cleanCode | Out-File -FilePath $cleanFile -Encoding UTF8
Write-Host "  [OK] Created clean test file: $cleanFile" -ForegroundColor Green

# 3. 创建requirements.txt
$requirements = @'
# requirements.txt
json==1.0.0
typing-extensions==4.0.0
'@

$reqFile = Join-Path $TestDir "requirements.txt"
$requirements | Out-File -FilePath $reqFile -Encoding UTF8
Write-Host "  [OK] Created requirements.txt: $reqFile" -ForegroundColor Green

# 测试函数
function Test-Tool {
    param(
        [string]$ToolName,
        [string]$ScriptPath,
        [string]$Arguments
    )
    
    Write-Host "`nTesting $ToolName..." -ForegroundColor Yellow
    Write-Host "  Command: python $ScriptPath $Arguments" -ForegroundColor Gray
    
    try {
        $output = python $ScriptPath $Arguments 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "  [PASS] $ToolName completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  [FAIL] $ToolName failed with exit code $exitCode" -ForegroundColor Red
            Write-Host "  Output: $output" -ForegroundColor Gray
            return $false
        }
    } catch {
        Write-Host "  [ERROR] $ToolName execution error: $_" -ForegroundColor Red
        return $false
    }
}

# 测试所有工具
Write-Host "`n=== Running Tool Tests ===" -ForegroundColor Cyan

$testResults = @{}

# 1. 测试AST分析工具
$testResults.ast = Test-Tool -ToolName "AST Analyzer" `
    -ScriptPath ".\ast_analyzer_v1.py" `
    -Arguments "`"$testFile`""

# 2. 测试第三方库分析工具
$testResults.third_party = Test-Tool -ToolName "Third-Party Analyzer" `
    -ScriptPath ".\third_party_analyzer_v1.py" `
    -Arguments "`"$testFile`" `"$reqFile`""

# 3. 测试数据流分析工具
$testResults.data_flow = Test-Tool -ToolName "Data Flow Analyzer" `
    -ScriptPath ".\data_flow_analyzer_v1.py" `
    -Arguments "`"$testFile`""

# 4. 测试性能分析工具
$testResults.performance = Test-Tool -ToolName "Performance Analyzer" `
    -ScriptPath ".\performance_analyzer_v1.py" `
    -Arguments "`"$testFile`""

# 5. 测试控制流分析工具 (需要networkx)
try {
    python -c "import networkx" 2>&1 | Out-Null
    $testResults.control_flow = Test-Tool -ToolName "Control Flow Analyzer" `
        -ScriptPath ".\control_flow_analyzer_v1.py" `
        -Arguments "`"$testFile`""
} catch {
    Write-Host "`n[SKIP] Control Flow Analyzer requires networkx" -ForegroundColor Yellow
    $testResults.control_flow = $null
}

# 6. 测试综合套件
$testResults.suite = Test-Tool -ToolName "Deep Analysis Suite" `
    -ScriptPath ".\deep_analysis_suite.py" `
    -Arguments "`"$testFile`" -r `"$reqFile`""

# 7. 测试干净文件
Write-Host "`n=== Testing Clean File ===" -ForegroundColor Cyan
$testResults.clean = Test-Tool -ToolName "Clean File Test" `
    -ScriptPath ".\ast_analyzer_v1.py" `
    -Arguments "`"$cleanFile`""

# 生成测试报告
Write-Host "`n=== Test Report ===" -ForegroundColor Cyan

$passed = ($testResults.Values | Where-Object { $_ -eq $true }).Count
$failed = ($testResults.Values | Where-Object { $_ -eq $false }).Count
$skipped = ($testResults.Values | Where-Object { $_ -eq $null }).Count
$total = $testResults.Count

Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "Skipped: $skipped" -ForegroundColor Yellow

Write-Host "`nDetailed Results:" -ForegroundColor Cyan
foreach ($tool in $testResults.Keys | Sort-Object) {
    $result = $testResults[$tool]
    $color = if ($result -eq $true) { "Green" } elseif ($result -eq $false) { "Red" } else { "Yellow" }
    $status = if ($result -eq $true) { "PASS" } elseif ($result -eq $false) { "FAIL" } else { "SKIP" }
    
    Write-Host "  $tool : $status" -ForegroundColor $color
}

# 清理
Write-Host "`nCleaning up test files..." -ForegroundColor Yellow
if (Test-Path $TestDir) {
    Remove-Item -Path $TestDir -Recurse -Force
    Write-Host "  [OK] Removed test directory" -ForegroundColor Green
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan

# 返回退出码
if ($failed -eq 0) {
    exit 0
} else {
    exit 1
}