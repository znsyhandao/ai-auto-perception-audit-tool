/**
 * OpenClaw Consistency Checker 测试套件
 * 测试插件核心功能
 */

const fs = require('fs').promises;
const path = require('path');
const { testPlugin } = require('../test_simple');

// 测试数据目录
const TEST_DATA_DIR = path.join(__dirname, 'test-data');

async function setupTestData() {
  // 创建测试数据目录
  await fs.mkdir(TEST_DATA_DIR, { recursive: true });
  
  // 创建测试技能目录
  const testSkillDir = path.join(TEST_DATA_DIR, 'test-skill');
  await fs.mkdir(testSkillDir, { recursive: true });
  
  // 创建有问题的config.yaml
  const configYaml = `name: "test-skill"
version: "1.0.0"
description: "A test skill with consistency issues"
runtime_network_access: false
security:
  claims:
    - "No network access"
    - "100% local execution"
tags:
  - "test"
  - "secular"
  - "non-religious"`;
  
  await fs.writeFile(path.join(testSkillDir, 'config.yaml'), configYaml);
  
  // 创建版本不一致的_meta.json
  const metaJson = {
    name: "test-skill-different",
    version: "1.0.1",
    slug: "test-skill",
    description: "Different description"
  };
  
  await fs.writeFile(path.join(testSkillDir, '_meta.json'), JSON.stringify(metaJson, null, 2));
  
  // 创建有宗教内容的SKILL.md
  const skillMd = `# Test Skill Different Title

## Description
This skill provides loving-kindness meditation exercises.

## Features
- Network API integration
- HTTP requests to external services
- Secure execution with eval() function

## Security
This skill is 100% secure and has no vulnerabilities.`;
  
  await fs.writeFile(path.join(testSkillDir, 'SKILL.md'), skillMd);
  
  // 创建CHANGELOG.md
  const changelog = `# Changelog

## [1.0.2] - 2026-04-02
### Changed
- Updated dependencies

## [1.0.0] - 2026-04-01
### Added
- Initial release`;
  
  await fs.writeFile(path.join(testSkillDir, 'CHANGELOG.md'), changelog);
  
  // 创建skill.py
  const skillPy = `"""Test skill module"""
import subprocess
import requests

version = "1.0.3"

class TestSkill:
    def __init__(self):
        self.name = "test-skill"
    
    def run(self):
        # This uses eval which is dangerous
        result = eval("2 + 2")
        return result`;
  
  await fs.writeFile(path.join(testSkillDir, 'skill.py'), skillPy);
  
  // 创建README.md
  const readme = `# Test Skill Package

This is a test skill with multiple consistency issues.`;
  
  await fs.writeFile(path.join(testSkillDir, 'README.md'), readme);
  
  // 创建__pycache__目录和.pyc文件
  const pycacheDir = path.join(testSkillDir, '__pycache__');
  await fs.mkdir(pycacheDir, { recursive: true });
  await fs.writeFile(path.join(pycacheDir, 'skill.cpython-313.pyc'), 'compiled python bytecode');
  
  return testSkillDir;
}

async function cleanupTestData() {
  try {
    await fs.rm(TEST_DATA_DIR, { recursive: true, force: true });
  } catch (error) {
    console.warn(`清理测试数据失败: ${error.message}`);
  }
}

async function runTests() {
  console.log('🧪 运行OpenClaw一致性检查插件测试...');
  console.log('='.repeat(60));
  
  let testSkillDir;
  let passedTests = 0;
  let failedTests = 0;
  
  try {
    // 设置测试数据
    console.log('1. 设置测试数据...');
    testSkillDir = await setupTestData();
    console.log(`   测试数据目录: ${testSkillDir}`);
    
    // 测试1: 运行插件检查
    console.log('\n2. 测试插件检查功能...');
    const results = await testPlugin(testSkillDir);
    
    // 验证测试结果
    console.log('\n3. 验证检查结果...');
    
    // 应该检测到错误
    if (!results.passed) {
      console.log('   ✅ 插件正确检测到问题');
      passedTests++;
    } else {
      console.log('   ❌ 插件应该检测到问题但未检测到');
      failedTests++;
    }
    
    // 应该检测到版本不一致
    const hasVersionIssues = results.errors.some(error => error.includes('版本号不一致'));
    if (hasVersionIssues) {
      console.log('   ✅ 检测到版本不一致问题');
      passedTests++;
    } else {
      console.log('   ❌ 应该检测到版本不一致问题');
      failedTests++;
    }
    
    // 应该检测到名称不一致
    const hasNameIssues = results.errors.some(error => error.includes('技能名称不一致'));
    if (hasNameIssues) {
      console.log('   ✅ 检测到名称不一致问题');
      passedTests++;
    } else {
      console.log('   ❌ 应该检测到名称不一致问题');
      failedTests++;
    }
    
    // 应该检测到缓存文件
    const hasCacheIssues = results.warnings.some(warning => warning.includes('__pycache__'));
    if (hasCacheIssues) {
      console.log('   ✅ 检测到缓存文件问题');
      passedTests++;
    } else {
      console.log('   ❌ 应该检测到缓存文件问题');
      failedTests++;
    }
    
    // 显示详细结果
    console.log('\n4. 详细检查结果:');
    console.log('   - 检查文件数:', results.fileCount);
    console.log('   - 错误数:', results.errors?.length || 0);
    console.log('   - 警告数:', results.warnings?.length || 0);
    
    if (results.errors && results.errors.length > 0) {
      console.log('\n   检测到的错误:');
      results.errors.forEach((error, index) => {
        console.log(`     ${index + 1}. ${error.split('\n')[0]}`);
      });
    }
    
    if (results.warnings && results.warnings.length > 0) {
      console.log('\n   检测到的警告:');
      results.warnings.forEach((warning, index) => {
        console.log(`     ${index + 1}. ${warning}`);
      });
    }
    
  } catch (error) {
    console.error(`❌ 测试失败: ${error.message}`);
    failedTests++;
  } finally {
    // 清理测试数据
    console.log('\n5. 清理测试数据...');
    await cleanupTestData();
    
    // 测试总结
    console.log('\n' + '='.repeat(60));
    console.log('📊 测试总结:');
    console.log(`   通过测试: ${passedTests}`);
    console.log(`   失败测试: ${failedTests}`);
    console.log(`   总计: ${passedTests + failedTests}`);
    
    if (failedTests === 0) {
      console.log('\n🎉 所有测试通过！插件功能正常。');
      process.exit(0);
    } else {
      console.log('\n❌ 有测试失败，需要修复。');
      process.exit(1);
    }
  }
}

// 运行测试
if (require.main === module) {
  runTests().catch(error => {
    console.error(`❌ 测试运行失败: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runTests, setupTestData, cleanupTestData };