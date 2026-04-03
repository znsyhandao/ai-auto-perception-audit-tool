/**
 * OpenClaw Consistency Checker 使用示例
 * 展示如何集成和使用插件
 */

const path = require('path');
const fs = require('fs').promises;

// 方法1: 直接使用插件
async function usePluginDirectly() {
  console.log('🔧 方法1: 直接使用插件');
  console.log('='.repeat(50));
  
  const ConsistencyCheckerPlugin = require('../index');
  
  // 创建检查器实例
  const checker = new ConsistencyCheckerPlugin({
    level: 'strict',
    verbose: true,
    autoFix: false
  });
  
  // 运行检查
  const skillPath = path.join(__dirname, 'test-skill');
  const results = await checker.runChecks(skillPath);
  
  console.log('检查结果:');
  console.log(JSON.stringify(results, null, 2));
}

// 方法2: 使用命令行界面
async function useCommandLine() {
  console.log('\n🔧 方法2: 使用命令行界面');
  console.log('='.repeat(50));
  
  console.log('基本命令:');
  console.log('  node cli_fixed.js <技能目录>');
  console.log('');
  
  console.log('常用选项:');
  console.log('  --report         生成详细报告');
  console.log('  --fix            尝试自动修复问题');
  console.log('  --json           JSON格式输出');
  console.log('  --verbose        详细输出');
  console.log('  --level <级别>   检查级别: basic, strict, paranoid');
  console.log('');
  
  console.log('示例:');
  console.log('  node cli_fixed.js ./my-skill --report --json');
  console.log('  node cli_fixed.js ./my-skill --fix --level strict');
}

// 方法3: 集成到构建流程
async function integrateWithBuild() {
  console.log('\n🔧 方法3: 集成到构建流程');
  console.log('='.repeat(50));
  
  const buildScript = `#!/bin/bash
# 构建脚本示例

echo "🔨 开始构建OpenClaw技能..."

# 1. 运行一致性检查
echo "📋 运行一致性检查..."
node cli_fixed.js . --level strict

if [ $? -ne 0 ]; then
  echo "❌ 一致性检查失败，请修复问题后重试"
  exit 1
fi

# 2. 清理缓存文件
echo "🧹 清理缓存文件..."
rm -rf __pycache__ *.pyc

# 3. 创建发布包
echo "📦 创建发布包..."
# ... 其他构建步骤

echo "✅ 构建完成！"`;
  
  console.log(buildScript);
}

// 方法4: 集成到CI/CD
async function integrateWithCICD() {
  console.log('\n🔧 方法4: 集成到CI/CD');
  console.log('='.repeat(50));
  
  const githubActions = `name: Consistency Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install Consistency Checker
        run: |
          npm install @your-org/openclaw-consistency-checker
          
      - name: Run Consistency Check
        run: |
          npx openclaw-consistency-checker . --level strict
          if [ $? -ne 0 ]; then exit 1; fi
          
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: consistency-report
          path: .consistency-reports/`;
  
  console.log(githubActions);
}

// 方法5: 创建自定义检查
async function createCustomCheck() {
  console.log('\n🔧 方法5: 创建自定义检查');
  console.log('='.repeat(50));
  
  const customChecker = `// checkers/custom-checker.js
class CustomChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
  }

  async check(metadata, skillPath) {
    console.log('[CustomChecker] 运行自定义检查...');
    
    // 自定义检查逻辑
    // 例如：检查文件大小限制
    const maxSize = 1024 * 1024; // 1MB
    const largeFiles = await this.findLargeFiles(skillPath, maxSize);
    
    if (largeFiles.length > 0) {
      this.results.warnings.push(
        \`发现大文件: \${largeFiles.join(', ')}\`
      );
    }
    
    return this.results;
  }

  async findLargeFiles(skillPath, maxSize) {
    const largeFiles = [];
    // 实现文件大小检查逻辑
    return largeFiles;
  }
}

module.exports = CustomChecker;`;
  
  console.log(customChecker);
}

// 运行所有示例
async function runAllExamples() {
  console.log('🚀 OpenClaw Consistency Checker 使用示例');
  console.log('='.repeat(60));
  
  await usePluginDirectly();
  await useCommandLine();
  await integrateWithBuild();
  await integrateWithCICD();
  await createCustomCheck();
  
  console.log('\n' + '='.repeat(60));
  console.log('🎯 总结:');
  console.log('  这个插件提供了多种使用方式:');
  console.log('  1. 直接API调用 - 最大灵活性');
  console.log('  2. 命令行界面 - 简单易用');
  console.log('  3. 构建集成 - 自动化检查');
  console.log('  4. CI/CD集成 - 团队协作');
  console.log('  5. 自定义扩展 - 满足特定需求');
}

// 运行示例
if (require.main === module) {
  runAllExamples().catch(error => {
    console.error('❌ 示例运行失败:', error.message);
    process.exit(1);
  });
}

module.exports = { runAllExamples };