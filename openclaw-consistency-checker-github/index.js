const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');

// 简单的颜色输出
const color = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  magenta: (text) => `\x1b[35m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};
const NetworkConsistencyChecker = require('./checkers/network-consistency');
const MetadataConsistencyChecker = require('./checkers/metadata-consistency');
const ProvenanceChecker = require('./checkers/provenance-check');
const VersionConsistencyChecker = require('./checkers/version-consistency');
const ContentConsistencyChecker = require('./checkers/content-consistency');

class ConsistencyCheckerPlugin {
  constructor(config = {}) {
    this.config = {
      level: config.level || 'strict',
      verbose: config.verbose || false,
      quiet: config.quiet || false,
      autoFix: config.autoFix || false,
      ignore: config.ignore || [
        'node_modules',
        '__pycache__',
        '*.pyc',
        '*.log',
        '.git'
      ],
      fileTypes: config.fileTypes || ['.yaml', '.yml', '.json', '.md', '.py', '.js', '.txt']
    };
    
    this.results = {
      passed: true,
      errors: [],
      warnings: [],
      checks: {},
      statistics: {
        totalFiles: 0,
        checkedFiles: 0,
        issuesFound: 0,
        duration: 0
      }
    };
    
    // 初始化检查器
    this.checkers = [
      new MetadataConsistencyChecker(this.config),
      new NetworkConsistencyChecker(this.config),
      new ProvenanceChecker(this.config),
      new VersionConsistencyChecker(this.config),
      new ContentConsistencyChecker(this.config)
    ];
    
    this.startTime = Date.now();
  }

  async runChecks(skillPath) {
    console.log('[ConsistencyChecker] 开始一致性检查...');
    
    const metadata = await this.loadMetadata(skillPath);
    const docFiles = await this.scanDocFiles(skillPath);
    const docContents = await this.readFiles(docFiles);
    
    await this.checkNetworkConsistency(metadata, docContents, docFiles);
    await this.checkMetadataConsistency(metadata, skillPath);
    await this.checkProvenance(metadata, docContents);
    
    this.printResults();
    return this.results;
  }

  async loadMetadata(skillPath) {
    const metadata = {};
    
    try {
      const skillInfoPath = path.join(skillPath, 'skill_info.json');
      if (await this.fileExists(skillInfoPath)) {
        metadata.skillInfo = JSON.parse(await fs.readFile(skillInfoPath, 'utf8'));
      }
      
      const packagePath = path.join(skillPath, 'package.json');
      if (await this.fileExists(packagePath)) {
        metadata.package = JSON.parse(await fs.readFile(packagePath, 'utf8'));
      }
      
      const skillMdPath = path.join(skillPath, 'SKILL.md');
      if (await this.fileExists(skillMdPath)) {
        const content = await fs.readFile(skillMdPath, 'utf8');
        metadata.skillMd = this.parseSkillMdMetadata(content);
      }
      
      const configPath = path.join(skillPath, 'config.yaml');
      if (await this.fileExists(configPath)) {
        const yaml = require('js-yaml');
        const content = await fs.readFile(configPath, 'utf8');
        metadata.config = yaml.load(content);
      }
    } catch (err) {
      console.error('加载元数据失败:', err);
    }
    
    return metadata;
  }

  parseSkillMdMetadata(content) {
    const metadata = {};
    const lines = content.split('\n');
    
    for (let i = 0; i < Math.min(20, lines.length); i++) {
      const line = lines[i];
      if (line.startsWith('version:')) {
        metadata.version = line.split(':')[1].trim();
      } else if (line.startsWith('author:')) {
        metadata.author = line.split(':')[1].trim();
      } else if (line.startsWith('source:')) {
        metadata.source = line.split(':')[1].trim();
      }
    }
    
    return metadata;
  }

  async scanDocFiles(skillPath) {
    const docExtensions = ['.md', '.txt', '.rst', '.adoc'];
    const docFiles = [];
    
    const scanDir = async (dir) => {
      const files = await fs.readdir(dir);
      for (const file of files) {
        const fullPath = path.join(dir, file);
        const stat = await fs.stat(fullPath);
        
        if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
          await scanDir(fullPath);
        } else if (docExtensions.includes(path.extname(file))) {
          docFiles.push(fullPath);
        }
      }
    };
    
    await scanDir(skillPath);
    return docFiles;
  }

  async readFiles(filePaths) {
    const contents = {};
    for (const filePath of filePaths) {
      try {
        contents[filePath] = await fs.readFile(filePath, 'utf8');
      } catch (err) {
        console.warn(`无法读取文件: ${filePath}`);
      }
    }
    return contents;
  }

  async checkNetworkConsistency(metadata, docContents, docFiles) {
    const checker = new NetworkConsistencyChecker(this.config);
    const result = await checker.check(metadata, docContents, docFiles);
    
    if (!result.passed) this.results.passed = false;
    this.results.errors.push(...result.errors);
    this.results.warnings.push(...result.warnings);
  }

  async checkMetadataConsistency(metadata, skillPath) {
    const checker = new MetadataConsistencyChecker(this.config);
    const result = await checker.check(metadata, skillPath);
    
    if (!result.passed) this.results.passed = false;
    this.results.errors.push(...result.errors);
    this.results.warnings.push(...result.warnings);
  }

  async checkProvenance(metadata, docContents) {
    const checker = new ProvenanceChecker(this.config);
    const result = await checker.check(metadata, docContents);
    
    if (!result.passed) this.results.passed = false;
    this.results.errors.push(...result.errors);
    this.results.warnings.push(...result.warnings);
  }

  printResults() {
    console.log('\n========== 一致性检查结果 ==========');
    
    if (this.results.errors.length > 0) {
      console.log('\n❌ 错误:');
      this.results.errors.forEach(err => console.log(`  - ${err}`));
    }
    
    if (this.results.warnings.length > 0) {
      console.log('\n⚠️  警告:');
      this.results.warnings.forEach(warn => console.log(`  - ${warn}`));
    }
    
    if (this.results.passed) {
      console.log('\n✅ 所有检查通过！');
    } else {
      console.log('\n❌ 检查失败，请修复上述问题后重新提交');
    }
    
    console.log('====================================\n');
  }

  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }
}

module.exports = {
  name: 'consistency-checker',
  version: '1.0.0',
  
  async auditPre(context) {
    const plugin = new ConsistencyCheckerPlugin(context.config);
    const results = await plugin.runChecks(context.skillPath);
    
    return {
      passed: results.passed,
      errors: results.errors,
      warnings: results.warnings
    };
  }
};
