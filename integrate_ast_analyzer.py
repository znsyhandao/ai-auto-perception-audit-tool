"""
将AST分析器集成到验证服务
"""

import os
import sys
import shutil
from pathlib import Path

def integrate_ast_analyzer():
    """集成AST分析器到验证服务"""
    print("=" * 60)
    print("深度分析工具集成 - AST分析器")
    print("=" * 60)
    
    # 源文件路径
    ast_analyzer_path = Path("ast_analyzer_v1.py")
    validator_service_path = Path("microservices/validator-service")
    
    if not ast_analyzer_path.exists():
        print(f"❌ AST分析器文件不存在: {ast_analyzer_path}")
        return False
    
    if not validator_service_path.exists():
        print(f"❌ 验证服务目录不存在: {validator_service_path}")
        return False
    
    print("[1] 复制AST分析器到验证服务...")
    
    # 复制文件
    destination = validator_service_path / "ast_analyzer.py"
    shutil.copy2(ast_analyzer_path, destination)
    
    print(f"  已复制: {ast_analyzer_path} -> {destination}")
    
    print()
    print("[2] 更新验证服务主文件...")
    
    # 读取验证服务主文件
    main_file = validator_service_path / "main.py"
    if not main_file.exists():
        print(f"❌ 验证服务主文件不存在: {main_file}")
        return False
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加AST分析器导入
    if "import ast_analyzer" not in content:
        # 找到import部分
        import_section = "import os\nimport json\nimport logging\n"
        new_import = "import os\nimport json\nimport logging\nimport ast_analyzer\n"
        
        content = content.replace(import_section, new_import)
        print("  已添加AST分析器导入")
    
    # 在validate_skill函数中添加AST分析
    if "def validate_skill" in content and "# AST分析" not in content:
        # 找到validate_skill函数
        lines = content.split('\n')
        new_lines = []
        
        in_validate_function = False
        function_indent = 0
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            if line.strip().startswith("def validate_skill"):
                in_validate_function = True
                function_indent = len(line) - len(line.lstrip())
            
            if in_validate_function and line.strip().startswith("return {"):
                # 在返回前添加AST分析
                indent = " " * function_indent
                
                ast_analysis_code = f'''
{indent}    # AST深度分析
{indent}    ast_results = {{}}
{indent}    skill_py_path = os.path.join(skill_path, "skill.py")
{indent}    if os.path.exists(skill_py_path):
{indent}        try:
{indent}            analyzer = ast_analyzer.ASTAnalyzer(skill_py_path)
{indent}            if analyzer.parse():
{indent}                analyzer.detect_infinite_loops()
{indent}                analyzer.detect_unreachable_code()
{indent}                analyzer.detect_security_issues()
{indent}                analyzer.detect_code_smells()
{indent}                
{indent}                ast_results = {{
{indent}                    "issues_found": len(analyzer.issues),
{indent}                    "issues": analyzer.issues[:10],  # 限制前10个问题
{indent}                    "analysis_complete": True
{indent}                }}
{indent}        except Exception as e:
{indent}            ast_results = {{
{indent}                "error": str(e),
{indent}                "analysis_complete": False
{indent}            }}
'''
                
                new_lines.append(ast_analysis_code)
        
        content = '\n'.join(new_lines)
        print("  已在validate_skill函数中添加AST分析")
    
    # 在返回结果中包含AST分析
    if '"metadata":' in content and '"ast_analysis":' not in content:
        # 找到metadata部分
        metadata_pattern = '"metadata": {'
        if metadata_pattern in content:
            # 在metadata中添加ast_analysis
            new_metadata = '"metadata": {\n            "ast_analysis": ast_results,'
            content = content.replace(metadata_pattern, new_metadata, 1)
            print("  已在metadata中添加AST分析结果")
    
    # 写入更新后的文件
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("[3] 创建测试脚本验证集成...")
    
    # 创建测试脚本
    test_script = """
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ast_analyzer import ASTAnalyzer

def test_ast_analyzer():
    '''测试AST分析器集成'''
    print("测试AST分析器集成...")
    
    # 测试文件路径
    test_file = os.path.join("..", "..", "releases", "AISleepGen", "v1.0.7_fixed", "skill.py")
    
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False
    
    print(f"分析文件: {test_file}")
    
    try:
        analyzer = ASTAnalyzer(test_file)
        
        if analyzer.parse():
            print("✅ AST解析成功")
            
            analyzer.detect_infinite_loops()
            analyzer.detect_unreachable_code()
            analyzer.detect_security_issues()
            analyzer.detect_code_smells()
            
            print(f"发现的问题数量: {len(analyzer.issues)}")
            
            if analyzer.issues:
                print("前5个问题:")
                for i, issue in enumerate(analyzer.issues[:5]):
                    print(f"  {i+1}. [{issue['type']}] {issue['message']} (行: {issue.get('line', 'N/A')})")
            else:
                print("✅ 未发现问题")
            
            return True
        else:
            print("❌ AST解析失败")
            return False
            
    except Exception as e:
        print(f"❌ 分析错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ast_analyzer()
    if success:
        print("\\n✅ AST分析器集成测试通过!")
    else:
        print("\\n❌ AST分析器集成测试失败")
"""
    
    test_file_path = validator_service_path / "test_ast_integration.py"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"  已创建测试脚本: {test_file_path}")
    
    print()
    print("[4] 运行集成测试...")
    
    # 运行测试
    os.chdir(validator_service_path)
    os.system("python test_ast_integration.py")
    os.chdir("../..")
    
    print()
    print("=" * 60)
    print("✅ AST分析器集成完成!")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 重启验证服务以应用更改")
    print("2. 测试验证服务是否正常工作")
    print("3. 运行完整审核验证AST分析功能")
    print()
    print("重启验证服务命令:")
    print("  cd microservices\\validator-service")
    print("  uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
    
    return True

if __name__ == "__main__":
    integrate_ast_analyzer()