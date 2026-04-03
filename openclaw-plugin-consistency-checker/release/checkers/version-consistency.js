const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');

// 简单的颜色输出
const color = {
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`
};

class VersionConsistencyChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
  }

  async check(metadata, skillPath) {
    if (this.config.verbose) {
      console.log(color.blue('[VersionConsistency] 检查版本一致性...'));
    }
    
    try {
      const versionData = await this.extractAllVersions(skillPath);
      await this.validateVersions(versionData);
      
    } catch (error) {
      this.results.passed = false;
      this.results.errors.push(`版本检查失败: ${error.message}`);
    }
    
    return this.results;
  }

  async extractAllVersions(skillPath) {
    const versionData = {
      configYaml: null,
      metaJson: null,
      packageJson: null,
      changelog: null,
      skillPy: null,
      otherFiles: []
    };
    
    // 检查 config.yaml
    const configPath = path.join(skillPath, 'config.yaml');
    if (await this.fileExists(configPath)) {
      try {
        const content = await fs.readFile(configPath, 'utf8');
        const config = yaml.load(content);
        versionData.configYaml = config.version;
      } catch (error) {
        this.results.warnings.push(`无法解析 config.yaml: ${error.message}`);
      }
    }
    
    // 检查 _meta.json
    const metaPath = path.join(skillPath, '_meta.json');
    if (await this.fileExists(metaPath)) {
      try {
        const content = await fs.readFile(metaPath, 'utf8');
        const meta = JSON.parse(content);
        versionData.metaJson = meta.version;
      } catch (error) {
        this.results.warnings.push(`无法解析 _meta.json: ${error.message}`);
      }
    }
    
    // 检查 package.json
    const packagePath = path.join(skillPath, 'package.json');
    if (await this.fileExists(packagePath)) {
      try {
        const content = await fs.readFile(packagePath, 'utf8');
        const pkg = JSON.parse(content);
        versionData.packageJson = pkg.version;
      } catch (error) {
        this.results.warnings.push(`无法解析 package.json: ${error.message}`);
      }
    }
    
    // 检查 CHANGELOG.md
    const changelogPath = path.join(skillPath, 'CHANGELOG.md');
    if (await this.fileExists(changelogPath)) {
      try {
        const content = await fs.readFile(changelogPath, 'utf8');
        const latestVersion = this.extractLatestVersionFromChangelog(content);
        versionData.changelog = latestVersion;
      } catch (error) {
        this.results.warnings.push(`无法解析 CHANGELOG.md: ${error.message}`);
      }
    }
    
    // 检查 skill.py 中的版本
    const skillPathPy = path.join(skillPath, 'skill.py');
    if (await this.fileExists(skillPathPy)) {
      try {
        const content = await fs.readFile(skillPathPy, 'utf8');
        const versionMatch = content.match(/version\s*=\s*["']([^"']+)["']/);
        if (versionMatch) {
          versionData.skillPy = versionMatch[1];
        }
      } catch (error) {
        // 静默失败，skill.py可能没有版本信息
      }
    }
    
    // 检查其他文件中的版本引用
    const otherFiles = await this.findVersionReferences(skillPath);
    versionData.otherFiles = otherFiles;
    
    return versionData;
  }

  async validateVersions(versionData) {
    const versions = [];
    const sources = [];
    
    // 收集所有版本
    if (versionData.configYaml) {
      versions.push(versionData.configYaml);
      sources.push('config.yaml');
    }
    
    if (versionData.metaJson) {
      versions.push(versionData.metaJson);
      sources.push('_meta.json');
    }
    
    if (versionData.packageJson) {
      versions.push(versionData.packageJson);
      sources.push('package.json');
    }
    
    if (versionData.changelog) {
      versions.push(versionData.changelog);
      sources.push('CHANGELOG.md');
    }
    
    if (versionData.skillPy) {
      versions.push(versionData.skillPy);
      sources.push('skill.py');
    }
    
    // 检查版本一致性
    if (versions.length > 0) {
      const uniqueVersions = [...new Set(versions)];
      
      if (uniqueVersions.length === 1) {
        if (this.config.verbose) {
          console.log(chalk.green(`✅ 所有文件版本一致: ${uniqueVersions[0]}`));
        }
      } else {
        this.results.passed = false;
        
        // 创建版本映射
        const versionMap = {};
        for (let i = 0; i < versions.length; i++) {
          if (!versionMap[versions[i]]) {
            versionMap[versions[i]] = [];
          }
          versionMap[versions[i]].push(sources[i]);
        }
        
        // 构建错误消息
        let errorMessage = '版本号不一致:\n';
        Object.entries(versionMap).forEach(([version, files]) => {
          errorMessage += `  ${version}: ${files.join(', ')}\n`;
        });
        
        this.results.errors.push(errorMessage.trim());
        
        // 提供修复建议
        const mostCommonVersion = this.findMostCommonVersion(versions);
        if (mostCommonVersion) {
          this.results.warnings.push(
            `建议统一版本号为: ${mostCommonVersion}\n` +
            `使用命令: npx openclaw-consistency-checker . --fix`
          );
        }
      }
    } else {
      this.results.warnings.push('未找到版本信息，建议添加版本号到 config.yaml');
    }
    
    // 检查其他文件中的版本引用
    if (versionData.otherFiles.length > 0) {
      const mainVersion = versionData.configYaml || versionData.metaJson || versionData.packageJson;
      if (mainVersion) {
        for (const ref of versionData.otherFiles) {
          if (ref.version !== mainVersion) {
            this.results.warnings.push(
              `文件 ${ref.file} 中引用的版本 ${ref.version} 与主版本 ${mainVersion} 不一致`
            );
          }
        }
      }
    }
  }

  extractLatestVersionFromChangelog(content) {
    // 查找最新的版本号 (格式: ## [1.0.0] - 2026-04-02)
    const versionMatch = content.match(/##\s*\[([\d.]+)\]\s*-\s*\d{4}-\d{2}-\d{2}/);
    return versionMatch ? versionMatch[1] : null;
  }

  async findVersionReferences(skillPath) {
    const references = [];
    
    try {
      const files = await fs.readdir(skillPath);
      
      for (const file of files) {
        if (file === 'node_modules' || file.startsWith('.')) {
          continue;
        }
        
        const filePath = path.join(skillPath, file);
        const stat = await fs.stat(filePath);
        
        if (stat.isFile() && this.shouldCheckFile(file)) {
          try {
            const content = await fs.readFile(filePath, 'utf8');
            
            // 查找版本引用
            const versionMatches = content.matchAll(/v?(\d+\.\d+\.\d+)/g);
            for (const match of versionMatches) {
              references.push({
                file: file,
                version: match[1],
                line: content.substring(0, match.index).split('\n').length
              });
            }
          } catch (error) {
            // 忽略无法读取的文件
          }
        }
      }
    } catch (error) {
      // 忽略目录读取错误
    }
    
    return references;
  }

  findMostCommonVersion(versions) {
    const frequency = {};
    let maxCount = 0;
    let mostCommon = null;
    
    for (const version of versions) {
      frequency[version] = (frequency[version] || 0) + 1;
      if (frequency[version] > maxCount) {
        maxCount = frequency[version];
        mostCommon = version;
      }
    }
    
    return mostCommon;
  }

  shouldCheckFile(filename) {
    const ext = path.extname(filename).toLowerCase();
    return this.config.fileTypes.includes(ext);
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

module.exports = VersionConsistencyChecker;