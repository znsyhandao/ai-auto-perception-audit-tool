/**
 * 测试插件对我们今天遇到的所有问题的检测能力
 */

const fs = require('fs').promises;
const path = require('path');
const { testPlugin } = require('./openclaw-plugin-consistency-checker/test_simple');

async function createTestSkill() {
  const testDir = path.join(__dirname, 'test-consistency-skill-all');
  
  // 清理并创建测试目录
  try {
    await fs.rm(testDir, { recursive: true, force: true });
  } catch {}
  
  await fs.mkdir(testDir, { recursive: true });
  
  // 创建有问题的config.yaml
  const configYaml = `name: "test-skill"
version: "1.0.0"
description: "A test skill with all consistency issues we faced today"
runtime_network_access: false
security:
  claims:
    - "No religious content"
    - "100% local execution"
tags:
  - "secular"
  - "non-religious"`;
  
  await fs.writeFile(path.join(testDir, 'config.yaml'), configYaml);
  
  // 创建版本不一致的_meta.json
  const metaJson = {
    name: "test-skill-different",
    version: "1.0.1",
    slug: "test-skill",
    description: "Different description"
  };
  
  await fs.writeFile(path.join(testDir, '_meta.json'), JSON.stringify(metaJson, null, 2));
  
  // 创建有宗教内容的SKILL.md
  const skillMd = `# Test Skill Different Title

## Features
- Provides loving-kindness meditation
- Uses HTTP API for data fetching
- Secure execution with eval() function

## Security
This skill is 100% secure with no vulnerabilities.`;
  
  await fs.writeFile(path.join(testDir, 'SKILL.md'), skillMd);
  
  // 创建CHANGELOG.md
  const changelog = `# Changelog

## [1.0.2] - 2026-04-02
### Changed
- Updated dependencies

## [1.0.0] - 2026-04-01
### Added
- Initial release`;
  
  await fs.writeFile(path.join(testDir, 'CHANGELOG.md'), changelog);
  
  // 创建skill.py
  const skillPy = `'''Test skill with issues'''
import subprocess
import requests

version = '1.0.3'

class TestSkill:
    def __init__(self):
        self.name = 'test-skill'
    
    def run(self):
        # Dangerous eval usage
        result = eval('2 + 2')
        return result`;
  
  await fs.writeFile(path.join(testDir, 'skill.py'), skillPy);
  
  // 创建README.md
  const readme = `# Test Skill Package

This is a test skill with multiple consistency issues.`;
  
  await fs.writeFile(path.join(testDir, 'README.md'), readme);
  
  // 创建__pycache__目录
  await fs.mkdir(path.join(testDir, '__pycache__'), { recursive: true });
  await fs.writeFile(path.join(testDir, '__pycache__', 'skill.cpython-313.pyc'), 'compiled python bytecode');
  
  console.log('✅ 测试技能创建完成，包含我们今天遇到的所有问题:');
  console.log('1. 版本不一致 (1.0.0, 1.0.1, 1.0.2, 1.0.3)');
  console.log('2. 名称不一致 (test-skill, test-skill-different, Test Skill Different Title)');
  console.log('3. 内容矛盾 (排除宗教但包含loving-kindness)');
  console.log('4. 网络矛盾 (声明无网络但使用HTTP API)');
  console.log('5. 安全矛盾 (声明安全但使用eval)');
  console.log('6. 缓存文件 (__pycache__目录)');
  
  return testDir;
}

async function runTest() {
  console.log('🧪 测试插件对我们今天所有问题的检测能力');
  console.log('='.repeat(60));
  
  try {
    // 创建测试技能
    const testDir = await createTestSkill();
    
    // 运行插件检查
    console.log('\n🔍 运行插件检查...');
    const results = await testPlugin(testDir);
    
    // 分析结果
    console.log('\n📊 检查结果分析:');
    console.log('='.repeat(60));
    
    const detectedIssues = [];
    const missedIssues = [];
    
    // 检查版本不一致检测
    const hasVersionIssue = results.errors?.some(e => e.includes('版本号不一致'));
    if (hasVersionIssue) {
      detectedIssues.push('版本不一致');
    } else {
      missedIssues.push('版本不一致');
    }
    
    // 检查名称不一致检测
    const hasNameIssue = results.errors?.some(e => e.includes('技能名称不一致'));
    if (hasNameIssue) {
      detectedIssues.push('名称不一致');
    } else {
      missedIssues.push('名称不一致');
    }
    
    // 检查缓存文件检测
    const hasCacheIssue = results.warnings?.some(w => w.includes('__pycache__'));
    if (hasCacheIssue) {
      detectedIssues.push('缓存文件');
    } else {
      missedIssues.push('缓存文件');
    }
    
    // 显示结果
    console.log(`✅ 检测到的问题 (${detectedIssues.length}/6):`);
    detectedIssues.forEach(issue => console.log(`   - ${issue}`));
    
    if (missedIssues.length > 0) {
      console.log(`\n❌ 未检测到的问题 (${missedIssues.length}/6):`);
      missedIssues.forEach(issue => console.log(`   - ${issue}`));
    }
    
    // 详细结果
    console.log('\n📋 详细检查结果:');
    console.log(`   检查文件数: ${results.fileCount}`);
    console.log(`   错误数: ${results.errors?.length || 0}`);
    console.log(`   警告数: ${results.warnings?.length || 0}`);
    
    if (results.errors && results.errors.length > 0) {
      console.log('\n   错误详情:');
      results.errors.forEach((error, index) => {
        const lines = error.split('\n');
        console.log(`     ${index + 1}. ${lines[0]}`);
        if (lines.length > 1) {
          lines.slice(1, 3).forEach(line => console.log(`       ${line}`));
        }
      });
    }
    
    // 清理测试目录
    await fs.rm(testDir, { recursive: true, force: true });
    
    // 总结
    console.log('\n' + '='.repeat(60));
    console.log('🎯 测试总结:');
    const detectionRate = (detectedIssues.length / 6) * 100;
    console.log(`   问题检测率: ${detectionRate.toFixed(1)}%`);
    
    if (detectionRate >= 80) {
      console.log('   ✅ 插件能有效检测我们今天遇到的大部分问题');
    } else {
      console.log('   ⚠️ 插件需要改进以更好地检测问题');
    }
    
  } catch (error) {
    console.error(`❌ 测试失败: ${error.message}`);
  }
}

// 运行测试
if (require.main === module) {
  runTest().catch(error => {
    console.error(`❌ 测试运行失败: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runTest };