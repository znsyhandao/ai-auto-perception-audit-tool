#!/usr/bin/env node

/**
 * OpenClaw Consistency Checker CLI - Fixed version
 * 命令行界面工具 (修复chalk问题)
 */

const path = require('path');
const fs = require('fs').promises;

// 简单的命令行参数解析
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    skillPath: '.',
    report: false,
    fix: false,
    json: false,
    verbose: false,
    quiet: false,
    level: 'strict'
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      if (key === 'report') options.report = true;
      else if (key === 'fix') options.fix = true;
      else if (key === 'json') options.json = true;
      else if (key === 'verbose') options.verbose = true;
      else if (key === 'quiet') options.quiet = true;
      else if (key === 'help') return { help: true };
      else if (key === 'version') return { version: true };
      else if (key === 'level' && i + 1 < args.length) {
        options.level = args[++i];
      }
    } else if (arg.startsWith('-')) {
      const flags = arg.slice(1);
      if (flags.includes('r')) options.report = true;
      if (flags.includes('f')) options.fix = true;
      if (flags.includes('j')) options.json = true;
      if (flags.includes('v')) options.verbose = true;
      if (flags.includes('q')) options.quiet = true;
      if (flags.includes('h')) return { help: true };
    } else if (i === 0) {
      options.skillPath = arg;
    }
  }
  
  return options;
}

// 简单的颜色输出
const color = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};

// 版本信息
const packageJson = require('./package.json');
const VERSION = packageJson.version;

// 设置命令行程序
program
  .name('openclaw-consistency-checker')
  .description('OpenClaw Consistency Checker - Detect document-metadata inconsistencies')
  .version(VERSION)
  .argument('[skill-path]', 'Path to the OpenClaw skill directory', '.')
  .option('-c, --config <path>', 'Path to configuration file')
  .option('-r, --report', 'Generate detailed report')
  .option('-f, --fix', 'Attempt to automatically fix issues')
  .option('-j, --json', 'Output results in JSON format')
  .option('-v, --verbose', 'Verbose output')
  .option('-q, --quiet', 'Quiet mode (only errors)')
  .option('--level <level>', 'Check level: basic, strict, paranoid', 'strict');

// 解析命令行参数
program.parse();

// 获取选项
const options = program.opts();
const skillPath = program.args[0] || '.';

async function main() {
  try {
    console.log(color.blue(color.bold('🔍 OpenClaw Consistency Checker')));
    console.log(color.gray(`Version: ${VERSION}`));
    console.log(color.gray(`Checking: ${path.resolve(skillPath)}`));
    console.log(color.gray('='.repeat(60)));
    
    // 检查目录是否存在
    try {
      await fs.access(skillPath);
    } catch (error) {
      console.error(color.red(`❌ Directory does not exist: ${skillPath}`));
      process.exit(1);
    }
    
    // 加载配置
    let config = {
      level: options.level,
      verbose: options.verbose,
      quiet: options.quiet,
      autoFix: options.fix
    };
    
    if (options.config) {
      try {
        const configPath = path.resolve(options.config);
        const configContent = await fs.readFile(configPath, 'utf8');
        const userConfig = JSON.parse(configContent);
        config = { ...config, ...userConfig };
      } catch (error) {
        console.error(color.red(`❌ Failed to load config file: ${error.message}`));
        process.exit(1);
      }
    }
    
    // 创建检查器实例
    const ConsistencyCheckerPlugin = require('./index');
    const checker = new ConsistencyCheckerPlugin(config);
    
    // 运行检查
    console.log(color.blue('📋 Running consistency checks...'));
    const startTime = Date.now();
    
    const results = await checker.runChecks(skillPath);
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    // 输出结果
    console.log(color.gray('='.repeat(60)));
    
    if (options.json) {
      // JSON输出格式
      const jsonOutput = {
        skill: path.basename(path.resolve(skillPath)),
        timestamp: new Date().toISOString(),
        duration: `${duration}s`,
        config: {
          level: config.level,
          autoFix: config.autoFix || false
        },
        results: results
      };
      
      console.log(JSON.stringify(jsonOutput, null, 2));
      
    } else {
      // 人类可读输出格式
      console.log(color.bold('📊 Check Results:'));
      console.log('');
      
      if (results.passed) {
        console.log(color.green.bold('✅ All checks passed!'));
      } else {
        console.log(color.red.bold('❌ Issues found:'));
        
        // 输出错误
        if (results.errors && results.errors.length > 0) {
          console.log(color.red.bold('\nErrors:'));
          results.errors.forEach((error, index) => {
            console.log(color.red(`  ${index + 1}. ${error}`));
          });
        }
        
        // 输出警告
        if (results.warnings && results.warnings.length > 0) {
          console.log(color.yellow.bold('\nWarnings:'));
          results.warnings.forEach((warning, index) => {
            console.log(color.yellow(`  ${index + 1}. ${warning}`));
          });
        }
      }
      
      // 输出统计信息
      console.log('');
      console.log(color.gray('📈 Statistics:'));
      console.log(color.gray(`  Duration: ${duration}s`));
      console.log(color.gray(`  Level: ${config.level}`));
      
      if (results.errors) {
        console.log(color.gray(`  Errors: ${results.errors.length}`));
      }
      
      if (results.warnings) {
        console.log(color.gray(`  Warnings: ${results.warnings.length}`));
      }
    }
    
    // 生成报告文件
    if (options.report) {
      await generateReport(skillPath, results, duration, config);
    }
    
    // 根据结果退出代码
    if (!results.passed) {
      process.exit(1);
    }
    
  } catch (error) {
    console.error(color.red(`❌ Unexpected error: ${error.message}`));
    if (options.verbose) {
      console.error(color.red(error.stack));
    }
    process.exit(1);
  }
}

async function generateReport(skillPath, results, duration, config) {
  try {
    const reportDir = path.join(skillPath, '.consistency-reports');
    await fs.mkdir(reportDir, { recursive: true });
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportFile = path.join(reportDir, `consistency-report-${timestamp}.json`);
    
    const report = {
      skill: path.basename(path.resolve(skillPath)),
      path: path.resolve(skillPath),
      timestamp: new Date().toISOString(),
      duration: `${duration}s`,
      config: config,
      results: results,
      summary: {
        passed: results.passed,
        totalIssues: (results.errors?.length || 0) + (results.warnings?.length || 0),
        errors: results.errors?.length || 0,
        warnings: results.warnings?.length || 0
      }
    };
    
    await fs.writeFile(reportFile, JSON.stringify(report, null, 2));
    console.log(color.green(`📄 Report generated: ${reportFile}`));
    
  } catch (error) {
    console.error(color.yellow(`⚠️ Failed to generate report: ${error.message}`));
  }
}

// 运行主函数
if (require.main === module) {
  main().catch(error => {
    console.error(color.red(`❌ Fatal error: ${error.message}`));
    process.exit(1);
  });
}

module.exports = { main };