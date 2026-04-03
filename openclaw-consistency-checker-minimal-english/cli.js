#!/usr/bin/env node

/**
 * OpenClaw Consistency Checker CLI
 * Command-line interface tool (fixed chalk issues)
 */

const path = require('path');
const fs = require('fs').promises;

// Simple command-line argument parsing
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

// Simple color output
const color = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};

// Display help information
function showHelp() {
  console.log(color.bold('OpenClaw Consistency Checker'));
  console.log('='.repeat(50));
  console.log('');
  console.log(color.bold('Usage:'));
  console.log('  openclaw-consistency-checker [skill-path] [options]');
  console.log('');
  console.log(color.bold('Options:'));
  console.log('  --report, -r          Generate detailed report');
  console.log('  --fix, -f             Attempt to auto-fix issues');
  console.log('  --json, -j            Output in JSON format');
  console.log('  --verbose, -v         Verbose output');
  console.log('  --quiet, -q           Quiet mode (errors only)');
  console.log('  --level <level>       Check level: basic, strict, paranoid');
  console.log('  --help, -h            Show this help');
  console.log('  --version             Show version');
  console.log('');
  console.log(color.bold('Examples:'));
  console.log('  openclaw-consistency-checker ./my-skill');
  console.log('  openclaw-consistency-checker ./my-skill --report --json');
  console.log('  openclaw-consistency-checker ./my-skill --fix --level strict');
  console.log('');
  console.log(color.bold('What it checks:'));
  console.log('  • Version consistency across files');
  console.log('  • Name format consistency');
  console.log('  • Content declaration contradictions');
  console.log('  • Network access consistency');
  console.log('  • Source code provenance');
  console.log('  • Cache file detection');
  console.log('');
  console.log('GitHub: https://github.com/znsyhandao/openclaw-consistency-checker');
}

// Display version information
function showVersion() {
  const packageJson = require('./package.json');
  console.log(`OpenClaw Consistency Checker v${packageJson.version}`);
}

// Main function
async function main() {
  const options = parseArgs();
  
  // Show help or version
  if (options.help) {
    showHelp();
    return;
  }
  
  if (options.version) {
    showVersion();
    return;
  }
  
  try {
    // Check if skill path exists
    const skillPath = path.resolve(options.skillPath);
    const stats = await fs.stat(skillPath).catch(() => null);
    
    if (!stats || !stats.isDirectory()) {
      console.error(color.red(`Error: Skill directory not found: ${skillPath}`));
      console.error(color.yellow('Usage: openclaw-consistency-checker <skill-directory>'));
      process.exit(1);
    }
    
    if (!options.quiet) {
      console.log(color.bold('🔍 Testing OpenClaw Consistency Checker Plugin...'));
      console.log('='.repeat(60));
      console.log(`Check directory: ${skillPath}`);
      console.log('='.repeat(60));
      console.log('');
    }
    
    // Load and run the checker
    const ConsistencyChecker = require('./index');
    const checker = new ConsistencyChecker({
      level: options.level,
      verbose: options.verbose,
      autoFix: options.fix
    });
    
    const results = await checker.runChecks(skillPath);
    
    // Display results
    if (options.json) {
      console.log(JSON.stringify(results, null, 2));
    } else {
      displayResults(results, options);
    }
    
    // Exit with appropriate code
    if (results.errors && results.errors.length > 0) {
      process.exit(1);
    } else {
      process.exit(0);
    }
    
  } catch (error) {
    console.error(color.red(`❌ Fatal error: ${error.message}`));
    if (options.verbose) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Display results in human-readable format
function displayResults(results, options) {
  console.log(color.bold('📊 Check Results:'));
  console.log('='.repeat(60));
  
  if (results.errors && results.errors.length > 0) {
    console.log(color.red('❌ Issues found:'));
    console.log('');
    
    results.errors.forEach((error, index) => {
      console.log(color.red(`  ${index + 1}. ${error}`));
    });
    
    console.log('');
  } else {
    console.log(color.green('✅ No issues found!'));
    console.log('');
  }
  
  if (results.warnings && results.warnings.length > 0) {
    console.log(color.yellow('⚠️  Warnings:'));
    console.log('');
    
    results.warnings.forEach((warning, index) => {
      console.log(color.yellow(`  ${index + 1}. ${warning}`));
    });
    
    console.log('');
  }
  
  // Statistics
  console.log(color.bold('📈 Statistics:'));
  console.log(`  Files checked: ${results.fileCount || 0}`);
  console.log(`  Errors: ${results.errors ? results.errors.length : 0}`);
  console.log(`  Warnings: ${results.warnings ? results.warnings.length : 0}`);
  
  if (results.fixes && results.fixes.length > 0) {
    console.log('');
    console.log(color.green('🔧 Auto-fixes applied:'));
    results.fixes.forEach((fix, index) => {
      console.log(color.green(`  ${index + 1}. ${fix}`));
    });
  }
  
  console.log('');
  console.log('='.repeat(60));
  
  // Suggestions
  if (results.errors && results.errors.length > 0) {
    console.log(color.yellow('💡 Suggestions:'));
    console.log('  1. Run with --fix to attempt auto-fixes');
    console.log('  2. Run with --report for detailed analysis');
    console.log('  3. Check documentation for specific fixes');
    console.log('');
  }
}

// Run the CLI
if (require.main === module) {
  main().catch(error => {
    console.error(`Unhandled error: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { parseArgs, showHelp, showVersion };