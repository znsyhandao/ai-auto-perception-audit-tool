const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');

async function deepAudit(skillPath) {
  console.log('\n🔍 OpenClaw Skill 深度一致性审核工具');
  console.log('=' .repeat(70));
  console.log(`📁 Skill 路径: ${skillPath}\n`);
  
  const issues = {
    errors: [],
    warnings: []
  };
  
  try {
    // 1. 读取所有文件
    const allFiles = await scanAllFiles(skillPath);
    const codeFiles = allFiles.filter(f => /\.(py|js|ts)$/i.test(f));
    const docFiles = allFiles.filter(f => /\.(md|txt)$/i.test(f));
    
    console.log(`📄 找到 ${docFiles.length} 个文档文件`);
    console.log(`💻 找到 ${codeFiles.length} 个代码文件\n`);
    
    // 2. 读取元数据和文档
    const docs = await readDocs(docFiles);
    const allCode = await readAllCode(codeFiles);
    
    // 3. 检查文档声明 vs 代码实现
    await checkDocumentationVsCode(docs, allCode, issues);
    
    // 4. 检查路径限制
    await checkPathRestrictions(docs, allCode, issues);
    
    // 5. 检查输入验证
    await checkInputValidation(allCode, issues);
    
    // 6. 输出报告
    printReport(issues);
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    issues.errors.push(err.message);
    printReport(issues);
  }
}

async function scanAllFiles(dir, files = []) {
  try {
    const entries = await fs.readdir(dir);
    for (const entry of entries) {
      const fullPath = path.join(dir, entry);
      const stat = await fs.stat(fullPath);
      if (stat.isDirectory() && !entry.startsWith('.') && entry !== 'node_modules' && entry !== '__pycache__' && entry !== 'dist') {
        await scanAllFiles(fullPath, files);
      } else if (stat.isFile()) {
        files.push(fullPath);
      }
    }
  } catch (err) {}
  return files;
}

async function readDocs(docFiles) {
  const docs = {};
  for (const file of docFiles) {
    try {
      docs[path.basename(file)] = await fs.readFile(file, 'utf8');
    } catch (err) {}
  }
  return docs;
}

async function readAllCode(codeFiles) {
  let allCode = '';
  for (const file of codeFiles) {
    try {
      const content = await fs.readFile(file, 'utf8');
      allCode += content + '\n';
    } catch (err) {}
  }
  return allCode;
}

async function checkDocumentationVsCode(docs, allCode, issues) {
  console.log('📋 检查文档声明 vs 代码实现...\n');
  
  // 收集文档中的承诺（只检查实际可实现的功能）
  const claims = [];
  
  for (const [filename, content] of Object.entries(docs)) {
    // 检测自动化验证声明
    if (content.match(/automated.*validation|自动.*验证|自动校验/i)) {
      claims.push({ file: filename, claim: 'automated validation', desc: '自动化验证' });
    }
    
    // 检测路径限制声明
    if (content.match(/restricted to skill directory|仅限于.*目录|只能访问.*目录|路径限制/i)) {
      claims.push({ file: filename, claim: 'path restriction', desc: '路径限制' });
    }
    
    // 检测内存/时间限制
    if (content.match(/memory limit|time limit|内存限制|时间限制|运行时限制/i)) {
      claims.push({ file: filename, claim: 'runtime limits', desc: '运行时限制' });
    }
  }
  
  // 检查代码中是否实现了这些承诺
  for (const claim of claims) {
    const implemented = await checkIfImplemented(claim.claim, allCode);
    if (!implemented) {
      issues.warnings.push(
        `📄 ${claim.file}: 文档声称有 "${claim.desc}"，但代码中未找到对应实现`
      );
      console.log(`   ⚠️  ${claim.file}: 声称有 "${claim.desc}" 但代码未实现`);
    } else {
      console.log(`   ✅ ${claim.file}: "${claim.desc}" 已在代码中实现`);
    }
  }
  
  if (claims.length === 0) {
    console.log('   ℹ️  未发现文档声明需要验证的功能');
  }
  console.log();
}

async function checkIfImplemented(claimType, allCode) {
  const patterns = {
    'automated validation': /validate|check|verify|校验|验证|检测/i,
    'path restriction': /path.*check|skill.*dir|allowed.*path|限制路径|路径检查|is_safe|within_skill|skill_dir/i,
    'runtime limits': /timeout|time_limit|max_time|memory_limit|资源限制|超时/i
  };
  
  const pattern = patterns[claimType];
  if (!pattern) return false;
  
  return pattern.test(allCode);
}

async function checkPathRestrictions(docs, allCode, issues) {
  console.log('📁 检查路径限制实现...\n');
  
  // 检查文档中是否声称有路径限制
  let claimsPathRestriction = false;
  for (const [filename, content] of Object.entries(docs)) {
    if (content.match(/restricted to skill directory|仅限于.*目录|只能访问.*目录|路径限制/i)) {
      claimsPathRestriction = true;
      console.log(`   📄 ${filename}: 声称有路径限制`);
      break;
    }
  }
  
  if (claimsPathRestriction) {
    // 检查代码中是否实现了路径限制
    const hasPathCheck = allCode.match(/skill.*dir|base.*dir|allowed.*path|限制.*路径|check.*path|is_safe|within_skill|os\.path\.abspath.*startswith/i);
    
    if (!hasPathCheck) {
      issues.errors.push(
        '文档声称"仅限于 skill 目录"，但代码中没有发现路径限制实现\n' +
        '  风险: skill 可能读取任意系统文件\n' +
        '  建议: 添加路径验证函数'
      );
      console.log('   ❌ 代码中没有实现路径限制');
    } else {
      console.log('   ✅ 代码中有路径检查实现');
    }
  } else {
    console.log('   ℹ️  文档未声称有路径限制');
  }
  console.log();
}

async function checkInputValidation(allCode, issues) {
  console.log('🔧 检查输入验证...\n');
  
  // 检查是否有文件路径输入
  const hasFileInput = allCode.match(/file.*path|read.*file|open.*file|文件路径/i);
  
  if (hasFileInput) {
    const hasValidation = allCode.match(/validate|check|sanitize|filter|验证|检查|清洗|白名单|is_safe|startswith/i);
    
    if (!hasValidation) {
      issues.warnings.push(
        '代码处理文件路径但缺少输入验证，可能被利用读取任意文件'
      );
      console.log('   ⚠️  处理文件路径但缺少输入验证');
    } else {
      console.log('   ✅ 有输入验证机制');
    }
  } else {
    console.log('   ℹ️  未发现文件路径处理');
  }
  console.log();
}

function printReport(issues) {
  console.log('=' .repeat(70));
  console.log('📊 深度审核报告');
  console.log('=' .repeat(70));
  
  if (issues.errors.length === 0 && issues.warnings.length === 0) {
    console.log('\n✅ 所有检查通过！文档与代码一致。\n');
    return;
  }
  
  if (issues.errors.length > 0) {
    console.log('\n❌ 错误 (必须修复才能通过 clawhub 安全扫描):');
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
  console.log('💡 修复建议:');
  console.log('1. 移除文档中未实现的声明，或实现相应功能');
  console.log('2. 添加路径验证: 确保只能访问 skill 目录内的文件');
  console.log('3. 添加输入验证: 清理用户输入的路径');
  console.log('=' .repeat(70) + '\n');
}

// 运行深度审核
const skillPath = process.argv[2];
if (!skillPath) {
  console.log('用法: node deep-audit-skill.js <skill路径>');
  process.exit(1);
}

deepAudit(skillPath).catch(console.error);