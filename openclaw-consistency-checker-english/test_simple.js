#!/usr/bin/env node

/**
 * 简化测试版本 - 避免依赖问题
 */

const path = require('path');
const fs = require('fs').promises;

async function testPlugin() {
  console.log('🔍 测试OpenClaw一致性检查插件...');
  console.log('='.repeat(60));
  
  const skillPath = process.argv[2] || 'D:\\openclaw\\releases\\sleep-health-assistant-v1.0.0';
  
  if (!skillPath) {
    console.error('❌ 请提供技能目录路径');
    console.log('用法: node test_simple.js <技能目录>');
    process.exit(1);
  }
  
  console.log(`检查目录: ${skillPath}`);
  console.log('='.repeat(60));
  
  try {
    // Check 目录是否存在
    await fs.access(skillPath);
    
    // Run 简化检查
    const results = await runSimpleChecks(skillPath);
    
    // Output 结果
    console.log('\n📊 检查结果:');
    console.log('='.repeat(60));
    
    if (results.passed) {
      console.log('✅ 所有检查通过！');
    } else {
      console.log('❌ 发现问题：');
      
      if (results.errors && results.errors.length > 0) {
        console.log('\n错误:');
        results.errors.forEach((error, index) => {
          console.log(`  ${index + 1}. ${error}`);
        });
      }
      
      if (results.warnings && results.warnings.length > 0) {
        console.log('\n警告:');
        results.warnings.forEach((warning, index) => {
          console.log(`  ${index + 1}. ${warning}`);
        });
      }
    }
    
    console.log('\n📈 统计:');
    console.log(`  检查文件数: ${results.fileCount || 0}`);
    console.log(`  错误数: ${results.errors?.length || 0}`);
    console.log(`  警告数: ${results.warnings?.length || 0}`);
    
  } catch (error) {
    console.error(`❌ 测试失败: ${error.message}`);
    process.exit(1);
  }
}

async function runSimpleChecks(skillPath) {
  const results = {
    passed: true,
    errors: [],
    warnings: [],
    fileCount: 0
  };
  
  // 1. 检查必需文件是否存在
  const requiredFiles = ['skill.py', 'config.yaml', 'SKILL.md', 'README.md', 'CHANGELOG.md'];
  const missingFiles = [];
  
  for (const file of requiredFiles) {
    const filePath = path.join(skillPath, file);
    try {
      await fs.access(filePath);
      results.fileCount++;
    } catch {
      missingFiles.push(file);
    }
  }
  
  if (missingFiles.length > 0) {
    results.passed = false;
    results.errors.push(`缺少必需文件: ${missingFiles.join(', ')}`);
  }
  
  // 2. 检查版本一致性
  try {
    const versionIssues = await checkVersionConsistency(skillPath);
    if (versionIssues.length > 0) {
      results.passed = false;
      results.errors.push(...versionIssues);
    }
  } catch (error) {
    results.warnings.push(`版本检查失败: ${error.message}`);
  }
  
  // 3. 检查名称一致性
  try {
    const nameIssues = await checkNameConsistency(skillPath);
    if (nameIssues.length > 0) {
      results.passed = false;
      results.errors.push(...nameIssues);
    }
  } catch (error) {
    results.warnings.push(`名称检查失败: ${error.message}`);
  }
  
  // 4. 检查缓存文件
  try {
    const cacheIssues = await checkCacheFiles(skillPath);
    if (cacheIssues.length > 0) {
      results.warnings.push(...cacheIssues);
    }
  } catch (error) {
    // 忽略缓存检查错误
  }
  
  return results;
}

async function checkVersionConsistency(skillPath) {
  const issues = [];
  const versions = {};
  
  // Check config.yaml
  const configPath = path.join(skillPath, 'config.yaml');
  if (await fileExists(configPath)) {
    try {
      const content = await fs.readFile(configPath, 'utf8');
      const versionMatch = content.match(/version:\s*["']?([\d.]+)["']?/);
      if (versionMatch) {
        versions.config = versionMatch[1];
      }
    } catch (error) {
      issues.push(`无法读取config.yaml: ${error.message}`);
    }
  }
  
  // Check _meta.json
  const metaPath = path.join(skillPath, '_meta.json');
  if (await fileExists(metaPath)) {
    try {
      const content = await fs.readFile(metaPath, 'utf8');
      const meta = JSON.parse(content);
      if (meta.version) {
        versions.meta = meta.version;
      }
    } catch (error) {
      issues.push(`无法读取_meta.json: ${error.message}`);
    }
  }
  
  // Check CHANGELOG.md
  const changelogPath = path.join(skillPath, 'CHANGELOG.md');
  if (await fileExists(changelogPath)) {
    try {
      const content = await fs.readFile(changelogPath, 'utf8');
      const versionMatch = content.match(/##\s*\[([\d.]+)\]/);
      if (versionMatch) {
        versions.changelog = versionMatch[1];
      }
    } catch (error) {
      issues.push(`无法读取CHANGELOG.md: ${error.message}`);
    }
  }
  
  // Check 版本一致性
  const uniqueVersions = [...new Set(Object.values(versions))];
  if (uniqueVersions.length > 1) {
    let versionMessage = '版本号不一致:\n';
    Object.entries(versions).forEach(([source, version]) => {
      versionMessage += `  ${source}: ${version}\n`;
    });
    issues.push(versionMessage.trim());
  }
  
  return issues;
}

async function checkNameConsistency(skillPath) {
  const issues = [];
  const names = new Set();
  
  // 从config.yaml提取名称
  const configPath = path.join(skillPath, 'config.yaml');
  if (await fileExists(configPath)) {
    try {
      const content = await fs.readFile(configPath, 'utf8');
      const nameMatch = content.match(/name:\s*["']([^"']+)["']/);
      if (nameMatch) {
        names.add(nameMatch[1].toLowerCase());
      }
    } catch (error) {
      // 忽略解析错误
    }
  }
  
  // 从SKILL.md提取名称
  const skillMdPath = path.join(skillPath, 'SKILL.md');
  if (await fileExists(skillMdPath)) {
    try {
      const content = await fs.readFile(skillMdPath, 'utf8');
      const titleMatch = content.match(/^#\s+(.+)$/m);
      if (titleMatch) {
        names.add(titleMatch[1].toLowerCase());
      }
    } catch (error) {
      // 忽略解析错误
    }
  }
  
  // Check 名称一致性
  if (names.size > 1) {
    issues.push(`技能名称不一致: ${Array.from(names).join(', ')}`);
  }
  
  // Check 是否有旧的sleep-rabbit引用
  const searchTerms = ['sleep.rabbit', 'sleeprabbit', 'sleep-rabbit', 'SleepRabbit'];
  const foundTerms = [];
  
  const filesToCheck = ['config.yaml', 'SKILL.md', 'README.md', 'CHANGELOG.md'];
  for (const file of filesToCheck) {
    const filePath = path.join(skillPath, file);
    if (await fileExists(filePath)) {
      try {
        const content = await fs.readFile(filePath, 'utf8');
        for (const term of searchTerms) {
          if (content.includes(term)) {
            foundTerms.push(`${file}: ${term}`);
          }
        }
      } catch (error) {
        // 忽略读取错误
      }
    }
  }
  
  if (foundTerms.length > 0) {
    issues.push(`发现旧的sleep-rabbit引用: ${foundTerms.join(', ')}`);
  }
  
  return issues;
}

async function checkCacheFiles(skillPath) {
  const issues = [];
  
  // Check __pycache__目录
  const pycachePath = path.join(skillPath, '__pycache__');
  if (await fileExists(pycachePath)) {
    issues.push('发现__pycache__目录，建议清理');
  }
  
  // Check .pyc文件
  try {
    const files = await fs.readdir(skillPath);
    const pycFiles = files.filter(file => file.endsWith('.pyc'));
    if (pycFiles.length > 0) {
      issues.push(`发现.pyc文件: ${pycFiles.join(', ')}`);
    }
  } catch (error) {
    // 忽略目录读取错误
  }
  
  return issues;
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

// Run 测试
if (require.main === module) {
  testPlugin().catch(error => {
    console.error(`❌ 测试失败: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { testPlugin };

