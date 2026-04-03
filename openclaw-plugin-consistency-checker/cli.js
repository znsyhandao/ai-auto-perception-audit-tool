#!/usr/bin/env node

/**
 * OpenClaw Consistency Checker CLI
 * 命令行界面工具
 */

const { program } = require('commander');
const path = require('path');
const fs = require('fs').promises;

// 简单的颜色输出替代chalk
const colors = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  magenta: (text) => `\x1b[35m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};

const ConsistencyCheckerPlugin = require('./index');

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
    console.log(colors.blue(colors.bold('🔍 OpenClaw Consistency Checker')));
    console.log(colors.gray(`Version: ${VERSION}`));
    console.log(colors.gray(`Checking: ${path.resolve(skillPath)}`));
    console.log(colors.gray('='.repeat(60)));
    
    // 检查目录是否存在
    try {
      await fs.access(skillPath);
    } catch (error) {
      console.error(chalk.red(`❌ Directory does not exist: ${skillPath}`));
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
        console.error(chalk.red(`❌ Failed to load config file: ${error.message}`));
        process.exit(1);
      }
    }
    
    // 创建检查器实例
    const checker = new ConsistencyCheckerPlugin(config);
    
    // 运行检查
    console.log(chalk.blue('📋 Running consistency checks...'));
    const startTime = Date.now();
    
    const results = await checker.runChecks(skillPath);
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    // 输出结果
    console.log(chalk.gray('='.repeat(60)));
    
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
      console.log(chalk.bold('📊 Check Results:'));
      console.log('');
      
      if (results.passed) {
        console.log(chalk.green.bold('✅ All checks passed!'));
      } else {
        console.log(chalk.red.bold('❌ Issues found:'));
        
        // 输出错误
        if (results.errors && results.errors.length > 0) {
          console.log(chalk.red.bold('\nErrors:'));
          results.errors.forEach((error, index) => {
            console.log(chalk.red(`  ${index + 1}. ${error}`));
          });
        }
        
        // 输出警告
        if (results.warnings && results.warnings.length > 0) {
          console.log(chalk.yellow.bold('\nWarnings:'));
          results.warnings.forEach((warning, index) => {
            console.log(chalk.yellow(`  ${index + 1}. ${warning}`));
          });
        }
      }
      
      // 输出统计信息
      console.log('');
      console.log(chalk.gray('📈 Statistics:'));
      console.log(chalk.gray(`  Duration: ${duration}s`));
      console.log(chalk.gray(`  Level: ${config.level}`));
      
      if (results.errors) {
        console.log(chalk.gray(`  Errors: ${results.errors.length}`));
      }
      
      if (results.warnings) {
        console.log(chalk.gray(`  Warnings: ${results.warnings.length}`));
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
    console.error(chalk.red(`❌ Unexpected error: ${error.message}`));
    if (options.verbose) {
      console.error(chalk.red(error.stack));
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
    console.log(chalk.green(`📄 Report generated: ${reportFile}`));
    
  } catch (error) {
    console.error(chalk.yellow(`⚠️ Failed to generate report: ${error.message}`));
  }
}

// 运行主函数
if (require.main === module) {
  main().catch(error => {
    console.error(chalk.red(`❌ Fatal error: ${error.message}`));
    process.exit(1);
  });
}

module.exports = { main };