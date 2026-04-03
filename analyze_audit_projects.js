/**
 * 分析D:\OpenClaw_TestingFramework中的审核项目
 * 检查哪些有官方审核替代
 */

const fs = require('fs').promises;
const path = require('path');

// 官方ClawHub审核功能列表（基于文档和已知信息）
const OFFICIAL_AUDIT_CAPABILITIES = [
  // 文件结构检查
  '必需文件检查',
  '文件格式验证',
  '文件编码检查',
  '文件大小限制',
  
  // 元数据检查
  'config.yaml验证',
  '_meta.json验证',
  '版本号格式检查',
  '技能名称验证',
  
  // 安全检查
  '危险函数检测',
  '网络访问声明验证',
  '隐私政策检查',
  '内容安全审核',
  
  // 内容检查
  '文档完整性检查',
  '示例代码验证',
  '标签分类检查',
  
  // 发布检查
  '打包文件检查',
  '依赖关系验证',
  '许可证检查'
];

async function analyzeAuditProjects() {
  console.log('🔍 分析D:\\OpenClaw_TestingFramework审核项目');
  console.log('='.repeat(60));
  
  const baseDir = 'D:\\OpenClaw_TestingFramework';
  const auditProjects = [
    'openclaw-plugin-consistency-checker',
    'simple_audit',
    'aisleepgen_final_audit',
    'aisleepgen_release_audit',
    'aisleepgen_simple_audit',
    'mathematical_audit_deployment'
  ];
  
  const results = [];
  
  for (const project of auditProjects) {
    const projectPath = path.join(baseDir, project);
    
    try {
      await fs.access(projectPath);
      
      console.log(`\n📁 项目: ${project}`);
      console.log('-'.repeat(40));
      
      // 分析项目内容
      const analysis = await analyzeProject(projectPath, project);
      results.push(analysis);
      
      // 显示分析结果
      console.log(`   类型: ${analysis.type}`);
      console.log(`   文件数: ${analysis.fileCount}`);
      console.log(`   主要功能: ${analysis.mainFunctions.join(', ')}`);
      
      // 检查是否有官方替代
      const officialAlternatives = checkOfficialAlternatives(analysis);
      if (officialAlternatives.length > 0) {
        console.log(`   🎯 官方审核替代: ${officialAlternatives.join(', ')}`);
      } else {
        console.log(`   💡 无直接官方替代 (独特功能)`);
      }
      
    } catch (error) {
      console.log(`\n📁 项目: ${project} (不存在或无法访问)`);
    }
  }
  
  // 生成总结报告
  console.log('\n' + '='.repeat(60));
  console.log('📊 总结报告');
  console.log('='.repeat(60));
  
  generateSummaryReport(results);
}

async function analyzeProject(projectPath, projectName) {
  const analysis = {
    name: projectName,
    type: '未知',
    fileCount: 0,
    mainFunctions: [],
    hasOfficialAlternative: false,
    officialAlternatives: []
  };
  
  try {
    // 统计文件
    const files = await getAllFiles(projectPath);
    analysis.fileCount = files.length;
    
    // 根据项目名称和内容判断类型
    if (projectName.includes('consistency-checker')) {
      analysis.type = '一致性检查插件';
      analysis.mainFunctions = [
        '版本一致性检查',
        '名称一致性检查',
        '内容声明检查',
        '元数据一致性检查'
      ];
    } else if (projectName.includes('simple_audit')) {
      analysis.type = '简单审核脚本';
      analysis.mainFunctions = [
        '基础文件检查',
        '必需文件验证',
        '简单格式检查'
      ];
    } else if (projectName.includes('aisleepgen')) {
      analysis.type = 'AISleepGen项目特定审核';
      analysis.mainFunctions = [
        '项目特定规则检查',
        '发布前验证',
        '自定义审核流程'
      ];
    } else if (projectName.includes('mathematical')) {
      analysis.type = '数学算法审核';
      analysis.mainFunctions = [
        '数学公式验证',
        '算法正确性检查',
        '数值稳定性分析'
      ];
    }
    
    // 检查文件内容获取更多信息
    const pyFiles = files.filter(f => f.endsWith('.py'));
    const jsFiles = files.filter(f => f.endsWith('.js'));
    const mdFiles = files.filter(f => f.endsWith('.md'));
    
    if (pyFiles.length > 0) {
      analysis.mainFunctions.push('Python代码分析');
    }
    if (jsFiles.length > 0) {
      analysis.mainFunctions.push('JavaScript代码分析');
    }
    
    // 读取README或文档文件
    for (const mdFile of mdFiles) {
      if (mdFile.toLowerCase().includes('readme')) {
        try {
          const content = await fs.readFile(mdFile, 'utf8');
          if (content.includes('检查') || content.includes('审核') || content.includes('验证')) {
            // 从文档中提取功能描述
            const lines = content.split('\n');
            for (const line of lines) {
              if (line.includes('-') || line.includes('•') || line.includes('✓')) {
                if (line.toLowerCase().includes('check') || line.includes('验证') || line.includes('检查')) {
                  const func = line.replace(/[-•✓]/g, '').trim();
                  if (func.length > 3 && !analysis.mainFunctions.includes(func)) {
                    analysis.mainFunctions.push(func);
                  }
                }
              }
            }
          }
        } catch (error) {
          // 忽略读取错误
        }
      }
    }
    
  } catch (error) {
    console.error(`分析项目 ${projectName} 失败:`, error.message);
  }
  
  return analysis;
}

function checkOfficialAlternatives(analysis) {
  const alternatives = [];
  
  // 根据功能匹配官方审核能力
  for (const func of analysis.mainFunctions) {
    for (const officialCap of OFFICIAL_AUDIT_CAPABILITIES) {
      if (func.includes(officialCap) || officialCap.includes(func)) {
        if (!alternatives.includes(officialCap)) {
          alternatives.push(officialCap);
        }
      }
    }
  }
  
  // 特殊匹配规则
  if (analysis.type === '一致性检查插件') {
    alternatives.push('版本号格式检查', '技能名称验证', '内容安全审核');
  } else if (analysis.type === '简单审核脚本') {
    alternatives.push('必需文件检查', '文件格式验证');
  } else if (analysis.type.includes('AISleepGen')) {
    // 项目特定审核，官方可能没有直接替代
    alternatives.push('自定义规则检查（需要手动配置）');
  } else if (analysis.type === '数学算法审核') {
    // 高度专业化，官方没有替代
    alternatives.push('无直接官方替代（专业领域）');
  }
  
  return alternatives;
}

async function getAllFiles(dirPath) {
  const files = [];
  
  async function traverse(currentPath) {
    try {
      const items = await fs.readdir(currentPath);
      
      for (const item of items) {
        // 跳过node_modules等目录
        if (item === 'node_modules' || item.startsWith('.') || item === '__pycache__') {
          continue;
        }
        
        const fullPath = path.join(currentPath, item);
        
        try {
          const stat = await fs.stat(fullPath);
          
          if (stat.isDirectory()) {
            await traverse(fullPath);
          } else {
            files.push(fullPath);
          }
        } catch (error) {
          // 忽略无法访问的文件
        }
      }
    } catch (error) {
      // 忽略目录读取错误
    }
  }
  
  await traverse(dirPath);
  return files;
}

function generateSummaryReport(results) {
  console.log('\n📋 项目分类:');
  console.log('-'.repeat(40));
  
  const categories = {};
  results.forEach(result => {
    if (!categories[result.type]) {
      categories[result.type] = [];
    }
    categories[result.type].push(result.name);
  });
  
  Object.entries(categories).forEach(([type, projects]) => {
    console.log(`   ${type}: ${projects.join(', ')}`);
  });
  
  console.log('\n🎯 官方审核替代情况:');
  console.log('-'.repeat(40));
  
  let hasFullAlternative = 0;
  let hasPartialAlternative = 0;
  let hasNoAlternative = 0;
  
  results.forEach(result => {
    if (result.officialAlternatives.length >= result.mainFunctions.length * 0.7) {
      hasFullAlternative++;
      console.log(`   ✅ ${result.name}: 有完整官方替代`);
    } else if (result.officialAlternatives.length > 0) {
      hasPartialAlternative++;
      console.log(`   ⚠️ ${result.name}: 有部分官方替代`);
    } else {
      hasNoAlternative++;
      console.log(`   💡 ${result.name}: 无官方替代 (独特价值)`);
    }
  });
  
  console.log('\n📊 统计:');
  console.log(`   总项目数: ${results.length}`);
  console.log(`   有完整替代: ${hasFullAlternative}`);
  console.log(`   有部分替代: ${hasPartialAlternative}`);
  console.log(`   无替代 (独特): ${hasNoAlternative}`);
  
  console.log('\n💡 建议:');
  console.log('-'.repeat(40));
  
  if (hasNoAlternative > 0) {
    console.log('   1. 无官方替代的项目有独特价值，值得维护');
  }
  
  if (hasFullAlternative > 0) {
    console.log('   2. 有完整官方替代的项目可考虑归档或简化');
  }
  
  console.log('   3. 部分替代的项目可以专注于官方未覆盖的功能');
}

// 运行分析
if (require.main === module) {
  analyzeAuditProjects().catch(error => {
    console.error('分析失败:', error.message);
    process.exit(1);
  });
}

module.exports = { analyzeAuditProjects };