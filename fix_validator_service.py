"""
紧急修复验证服务语法错误
"""

import os

def fix_validator_service():
    """修复验证服务"""
    print("紧急修复验证服务语法错误...")
    
    file_path = "microservices/validator-service/main.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到根端点函数并修复
    root_function_start = 'async def root():'
    root_function_end = '}'
    
    # 简单的修复：移除错误的AST代码，恢复标准根端点
    lines = content.split('\n')
    fixed_lines = []
    in_broken_root = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'async def root():' in line:
            in_broken_root = True
            indent_level = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            fixed_lines.append(' ' * (indent_level + 4) + '"""根端点"""')
            fixed_lines.append(' ' * (indent_level + 4) + 'return {')
            fixed_lines.append(' ' * (indent_level + 8) + '"service": "validator-service",')
            fixed_lines.append(' ' * (indent_level + 8) + '"version": "3.0.0",')
            fixed_lines.append(' ' * (indent_level + 8) + '"status": "running",')
            fixed_lines.append(' ' * (indent_level + 8) + '"port": 8001,')
            fixed_lines.append(' ' * (indent_level + 8) + '"endpoints": {')
            fixed_lines.append(' ' * (indent_level + 12) + '"validate": "POST /validate - 验证技能",')
            fixed_lines.append(' ' * (indent_level + 12) + '"results": "GET /validate/{skill_id} - 获取结果",')
            fixed_lines.append(' ' * (indent_level + 12) + '"health": "GET /health - 健康检查"')
            fixed_lines.append(' ' * (indent_level + 8) + '}')
            fixed_lines.append(' ' * (indent_level + 4) + '}')
            continue
        
        if in_broken_root:
            # 跳过所有错误的AST代码行，直到找到函数结束
            if line.strip() == '}' and len(line) - len(line.lstrip()) == indent_level:
                in_broken_root = False
                fixed_lines.append(line)
            # 跳过其他行
            continue
        
        fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    # 备份原文件
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 验证服务已修复")
    print(f"📁 备份文件: {backup_path}")
    
    # 验证修复
    print("\n验证修复...")
    try:
        # 检查语法
        import ast
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ 语法检查通过")
        
        # 检查关键函数
        with open(file_path, 'r', encoding='utf-8') as f:
            fixed_content = f.read()
        
        required_functions = [
            'async def root():',
            'async def health_check():',
            'async def validate_skill(',
            'async def get_validation_result('
        ]
        
        missing = []
        for func in required_functions:
            if func not in fixed_content:
                missing.append(func)
        
        if missing:
            print(f"❌ 缺失函数: {missing}")
            return False
        else:
            print("✅ 所有必需函数存在")
            return True
            
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False

if __name__ == "__main__":
    if fix_validator_service():
        print("\n🎉 验证服务修复成功！")
        print("下一步: 重启验证服务")
    else:
        print("\n❌ 验证服务修复失败")