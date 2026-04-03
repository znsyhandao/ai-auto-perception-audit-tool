const fs = require('fs').promises;
const path = require('path');
const fsSync = require('fs');

async function auditSkill(skillPath) {
  console.log('\n🔍 OpenClaw Skill 一致性审核工具');
  console.log('=' .repeat(70));
  console.log(`📁 Skill 路径: ${skillPath}\n`);
  
  // 检查路径是否存在
  if (!fsSync.existsSync(skillPath)) {
    console.error(`❌ 错误: 路径不存在 - ${skillPath}`);
    return;
  }
  
  const issues = {
    errors: [],
    warnings: []
  };
  
  try {
    // 1. 扫描所有文档文件
    const allFiles = await scanAllFiles(skillPath);
    const docFiles = allFiles.filter(f => /\.(md|txt|rst)$/i.test(f));
    const jsonFiles = allFiles.filter(f => /\.json$/i.test(f));
    
    console.log(`📄 找到 ${docFiles.length} 个文档文件`);
    console.log(`🔧 找到 ${jsonFiles.length} 个 JSON 文件\n`);
    
    // 2. 读取元数据
    const metadata = await loadMetadata(skillPath);
    
    // 3. 检查网络一致性
    await checkNetworkConsistency(skillPath, docFiles, metadata, issues);
    
    // 4. 检查版本一致性
    checkVersionConsistency(metadata, issues);
    
    // 5. 检查来源完整性
    await checkProvenance(skillPath, docFiles, metadata, issues);
    
    // 6. 检查 skill 结构
    await checkSkillStructure(skillPath, issues);
    
    // 7. 输出报告
    printReport(issues);
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    issues.errors.push(`无法访问 skill 目录: ${err.message}`);
    printReport(issues);
  }
}

async function scanAllFiles(dir, files = []) {
  try {
    const entries = await fs.readdir(dir);
    for (const entry of entries) {
      const fullPath = path.join(dir, entry);
      const stat = await fs.stat(fullPath);
      if (stat.isDirectory() && !entry.startsWith('.') && entry !== 'node_modules' && entry !== 'dist') {
        await scanAllFiles(fullPath, files);
      } else if (stat.isFile()) {
        files.push(fullPath);
      }
    }
  } catch (err) {
    // 忽略权限错误
  }
  return files;
}

async function loadMetadata(skillPath) {
  const metadata = {};
  
  // 读取 skill_info.json
  const skillInfoPath = path.join(skillPath, 'skill_info.json');
  if (await fileExists(skillInfoPath)) {
    try {
      const content = await fs.readFile(skillInfoPath, 'utf8');
      metadata.skillInfo = JSON.parse(content);
      console.log('✅ 找到 skill_info.json');
      if (metadata.skillInfo.version) console.log(`   版本: ${metadata.skillInfo.version}`);
      if (metadata.skillInfo.runtime_network_access !== undefined) {
        console.log(`   网络访问: ${metadata.skillInfo.runtime_network_access}`);
      }
    } catch (err) {
      console.warn('⚠️  skill_info.json 格式错误:', err.message);
    }
  } else {
    console.log('⚠️  未找到 skill_info.json');
  }
  
  // 读取 package.json
  const packagePath = path.join(skillPath, 'package.json');
  if (await fileExists(packagePath)) {
    try {
      const content = await fs.readFile(packagePath, 'utf8');
      metadata.package = JSON.parse(content);
      console.log('✅ 找到 package.json');
      if (metadata.package.version) console.log(`   版本: ${metadata.package.version}`);
    } catch (err) {
      console.warn('⚠️  package.json 格式错误:', err.message);
    }
  }
  
  // 读取 SKILL.md 头部
  const skillMdPath = path.join(skillPath, 'SKILL.md');
  if (await fileExists(skillMdPath)) {
    const content = await fs.readFile(skillMdPath, 'utf8');
    const lines = content.split('\n').slice(0, 30);
    for (const line of lines) {
      if (line.startsWith('version:')) metadata.skillMdVersion = line.split(':')[1].trim();
      if (line.startsWith('author:')) metadata.skillMdAuthor = line.split(':')[1].trim();
      if (line.startsWith('source:')) metadata.skillMdSource = line.split(':')[1].trim();
      if (line.startsWith('name:')) metadata.skillMdName = line.split(':')[1].trim();
    }
    console.log('✅ 找到 SKILL.md');
    if (metadata.skillMdVersion) console.log(`   版本: ${metadata.skillMdVersion}`);
  }
  
  console.log();
  return metadata;
}

async function checkNetworkConsistency(skillPath, docFiles, metadata, issues) {
  console.log('🌐 检查网络声明一致性...');
  
  // 检查是否声明为无网络
  let noNetworkDeclared = false;
  if (metadata.skillInfo && metadata.skillInfo.runtime_network_access === false) {
    noNetworkDeclared = true;
    console.log('   ✓ 声明为无网络访问 (runtime_network_access: false)');
  }
  if (metadata.package && metadata.package.permissions) {
    if (!metadata.package.permissions.includes('network') && 
        !metadata.package.permissions.includes('internet')) {
      noNetworkDeclared = true;
      console.log('   ✓ package.json 未声明网络权限');
    }
  }
  
  if (noNetworkDeclared) {
    const networkPatterns = [
      { pattern: /port\s+(\d{4,5})/gi, name: '端口' },
      { pattern: /http:\/\/[^\s]+/gi, name: 'HTTP链接' },
      { pattern: /https:\/\/[^\s]+/gi, name: 'HTTPS链接' },
      { pattern: /\bsocket\b/gi, name: 'Socket' },
      { pattern: /\bserver\b/gi, name: 'Server' },
      { pattern: /listening\s+on/gi, name: 'Listening' },
      { pattern: /api\s+endpoint/gi, name: 'API端点' },
      { pattern: /:\d{4,5}\b/gi, name: '端口号' }
    ];
    
    for (const filePath of docFiles) {
      const content = await fs.readFile(filePath, 'utf8');
      const fileName = path.basename(filePath);
      
      for (const { pattern, name } of networkPatterns) {
        const matches = content.match(pattern);
        if (matches) {
          issues.errors.push(
            `文档 "${fileName}" 中包含 ${name} 相关描述 (${matches[0]})，` +
            `但 skill 声明为无网络访问`
          );
          console.log(`   ❌ 发现: ${fileName} - ${matches[0]}`);
        }
      }
    }
  }
  
  if (issues.errors.filter(e => e.includes('网络')).length === 0) {
    console.log('   ✅ 网络声明一致性检查通过');
  }
  console.log();
}

function checkVersionConsistency(metadata, issues) {
  console.log('📌 检查版本一致性...');
  
  const versions = [];
  if (metadata.skillInfo?.version) versions.push({ file: 'skill_info.json', version: metadata.skillInfo.version });
  if (metadata.package?.version) versions.push({ file: 'package.json', version: metadata.package.version });
  if (metadata.skillMdVersion) versions.push({ file: 'SKILL.md', version: metadata.skillMdVersion });
  
  if (versions.length > 1) {
    const firstVersion = versions[0].version;
    const mismatches = versions.filter(v => v.version !== firstVersion);
    
    if (mismatches.length > 0) {
      issues.errors.push('版本号不一致:\n' + versions.map(v => `  - ${v.file}: ${v.version}`).join('\n'));
      console.log('   ❌ 版本不一致:');
      versions.forEach(v => console.log(`      ${v.file}: ${v.version}`));
    } else {
      console.log(`   ✅ 版本一致: ${firstVersion}`);
    }
  } else if (versions.length === 1) {
    console.log(`   ⚠️  只有一个文件包含版本信息: ${versions[0].version}`);
  } else {
    console.log('   ⚠️  未找到版本信息');
  }
  console.log();
}

async function checkProvenance(skillPath, docFiles, metadata, issues) {
  console.log('🔗 检查来源完整性...');
  
  let hasSource = false;
  if (metadata.skillInfo?.source) {
    hasSource = true;
    console.log(`   ✓ source 字段: ${metadata.skillInfo.source}`);
  }
  if (metadata.skillMdSource) {
    hasSource = true;
    console.log(`   ✓ SKILL.md source: ${metadata.skillMdSource}`);
  }
  
  if (!hasSource) {
    // 查找 GitHub 链接
    const githubPattern = /https?:\/\/github\.com\/[a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-_]+/g;
    let foundGithub = false;
    
    for (const filePath of docFiles) {
      const content = await fs.readFile(filePath, 'utf8');
      const matches = content.match(githubPattern);
      if (matches && matches.length > 0) {
        foundGithub = true;
        issues.warnings.push(
          `文档中引用了 GitHub (${matches[0]})，但未在元数据中设置 source 字段\n` +
          `  建议: 在 skill_info.json 中添加 "source": "${matches[0]}"`
        );
        console.log(`   ⚠️  发现 GitHub 引用但无 source 字段: ${matches[0]}`);
        break;
      }
    }
    
    if (!foundGithub) {
      issues.warnings.push('未设置 source 字段，建议添加来源信息');
      console.log('   ⚠️  未设置 source 字段');
    }
  }
  
  console.log();
}

async function checkSkillStructure(skillPath, issues) {
  console.log('📁 检查 skill 结构...');
  
  const requiredFiles = ['SKILL.md'];
  const optionalFiles = ['skill_info.json', 'package.json', 'README.md', 'config.yaml'];
  
  for (const file of requiredFiles) {
    const filePath = path.join(skillPath, file);
    if (await fileExists(filePath)) {
      console.log(`   ✅ ${file} 存在`);
    } else {
      issues.errors.push(`缺少必需文件: ${file}`);
      console.log(`   ❌ 缺少必需文件: ${file}`);
    }
  }
  
  for (const file of optionalFiles) {
    const filePath = path.join(skillPath, file);
    if (await fileExists(filePath)) {
      console.log(`   ✓ ${file} 存在`);
    }
  }
  
  console.log();
}

function printReport(issues) {
  console.log('=' .repeat(70));
  console.log('📊 审核报告');
  console.log('=' .repeat(70));
  
  if (issues.errors.length === 0 && issues.warnings.length === 0) {
    console.log('\n✅ 所有检查通过！Skill 符合规范。\n');
    return;
  }
  
  if (issues.errors.length > 0) {
    console.log('\n❌ 错误 (必须修复才能提交到 clawhub):');
    issues.errors.forEach((err, i) => {
      console.log(`\n${i + 1}. ${err}`);
    });
  }
  
  if (issues.warnings.length > 0) {
    console.log('\n⚠️  警告 (建议修复):');
    issues.warnings.forEach((warn, i) => {
      console.log(`\n${i + 1}. ${warn}`);
    });
  }
  
  console.log('\n' + '=' .repeat(70));
  if (issues.errors.length > 0) {
    console.log('❌ 审核失败，请修复上述错误后重新提交');
  } else {
    console.log('⚠️  审核通过但有警告，建议修复后提交');
  }
  console.log('=' .repeat(70) + '\n');
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

// 运行审核
const skillPath = process.argv[2];
if (!skillPath) {
  console.log('用法: node audit-skill.js <skill路径>');
  console.log('示例: node audit-skill.js D:\\OpenClaw_TestingFramework\\my-skill');
  console.log('\n或者指定完整路径:');
  console.log('node audit-skill.js "C:\\Users\\cqs10\\.openclaw\\skills\\your-skill"');
  process.exit(1);
}

auditSkill(skillPath).catch(console.error);