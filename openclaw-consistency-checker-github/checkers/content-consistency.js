const fs = require('fs').promises;
const path = require('path');

// 简单的颜色输出
const color = {
  blue: (text) => `\x1b[34m${text}\x1b[0m`
};

class ContentConsistencyChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
    
    // 内容声明矛盾检测规则
    this.contradictionRules = [
      {
        name: '宗教内容排除矛盾',
        exclusionKeywords: ['buddhist', 'buddhism', 'religious', 'religion', 'spiritual'],
        contradictionKeywords: ['loving-kindness', 'metta', 'compassion meditation'],
        message: '声明排除宗教内容但包含宗教相关术语'
      },
      {
        name: '网络访问声明矛盾',
        exclusionKeywords: ['no network', 'local only', 'offline', 'no internet'],
        contradictionKeywords: ['api', 'http', 'https', 'fetch', 'request', 'download'],
        message: '声明无网络访问但包含网络相关术语'
      },
      {
        name: '安全声明矛盾',
        securityKeywords: ['secure', 'safe', 'encrypted', 'protected'],
        vulnerabilityKeywords: ['eval', 'exec', 'subprocess', 'shell', 'dangerous'],
        message: '声明安全但包含危险函数'
      }
    ];
  }

  async check(metadata, skillPath) {
    if (this.config.verbose) {
      console.log(color.blue('[ContentConsistency] 检查内容声明一致性...'));
    }
    
    try {
      // 提取元数据中的声明
      const declarations = await this.extractDeclarations(metadata, skillPath);
      
      // 扫描文档内容
      const docContent = await this.scanDocumentation(skillPath);
      
      // 检查声明矛盾
      await this.checkContradictions(declarations, docContent);
      
      // 检查内容一致性
      await this.checkContentConsistency(skillPath);
      
    } catch (error) {
      this.results.passed = false;
      this.results.errors.push(`内容检查失败: ${error.message}`);
    }
    
    return this.results;
  }

  async extractDeclarations(metadata, skillPath) {
    const declarations = {
      religiousExclusion: false,
      networkAccess: false,
      securityClaims: [],
      privacyClaims: []
    };
    
    // 从config.yaml提取声明
    if (metadata.config) {
      const config = metadata.config;
      
      // 检查宗教内容排除
      if (config.description && config.description.toLowerCase().includes('no religious')) {
        declarations.religiousExclusion = true;
      }
      
      if (config.tags && Array.isArray(config.tags)) {
        if (config.tags.some(tag => tag.toLowerCase().includes('secular') || tag.toLowerCase().includes('non-religious'))) {
          declarations.religiousExclusion = true;
        }
      }
      
      // 检查网络访问
      if (config.runtime_network_access === false) {
        declarations.networkAccess = false;
      } else if (config.runtime_network_access === true) {
        declarations.networkAccess = true;
      }
      
      // 检查安全声明
      if (config.security && config.security.claims) {
        declarations.securityClaims = config.security.claims;
      }
    }
    
    // 从SKILL.md提取声明
    const skillMdPath = path.join(skillPath, 'SKILL.md');
    if (await this.fileExists(skillMdPath)) {
      try {
        const content = await fs.readFile(skillMdPath, 'utf8');
        declarations.skillMdContent = content;
        
        // 提取SKILL.md中的声明
        if (content.toLowerCase().includes('no religious content')) {
          declarations.religiousExclusion = true;
        }
        
        if (content.toLowerCase().includes('100% local') || content.toLowerCase().includes('no network')) {
          declarations.networkAccess = false;
        }
      } catch (error) {
        this.results.warnings.push(`无法读取SKILL.md: ${error.message}`);
      }
    }
    
    return declarations;
  }

  async scanDocumentation(skillPath) {
    const docContent = {
      files: [],
      text: '',
      keywords: {}
    };
    
    try {
      const files = await fs.readdir(skillPath);
      
      for (const file of files) {
        if (this.shouldCheckDocumentationFile(file)) {
          const filePath = path.join(skillPath, file);
          try {
            const content = await fs.readFile(filePath, 'utf8');
            docContent.files.push({
              name: file,
              content: content
            });
            docContent.text += content + '\n';
            
            // 提取关键词
            this.extractKeywords(content, file, docContent.keywords);
          } catch (error) {
            // 忽略无法读取的文件
          }
        }
      }
    } catch (error) {
      this.results.warnings.push(`文档扫描失败: ${error.message}`);
    }
    
    return docContent;
  }

  async checkContradictions(declarations, docContent) {
    // 检查宗教内容排除矛盾
    if (declarations.religiousExclusion) {
      for (const rule of this.contradictionRules) {
        if (rule.name === '宗教内容排除矛盾') {
          const foundKeywords = this.findKeywordsInText(docContent.text, rule.contradictionKeywords);
          if (foundKeywords.length > 0) {
            this.results.passed = false;
            this.results.errors.push(
              `${rule.message}:\n` +
              `检测到的术语: ${foundKeywords.join(', ')}\n` +
              `建议: 使用非宗教替代术语 (如将 'loving-kindness' 替换为 'compassion_meditation')`
            );
          }
        }
      }
    }
    
    // 检查网络访问声明矛盾
    if (declarations.networkAccess === false) {
      for (const rule of this.contradictionRules) {
        if (rule.name === '网络访问声明矛盾') {
          const foundKeywords = this.findKeywordsInText(docContent.text, rule.contradictionKeywords);
          if (foundKeywords.length > 0) {
            this.results.passed = false;
            this.results.errors.push(
              `${rule.message}:\n` +
              `检测到的网络术语: ${foundKeywords.join(', ')}\n` +
              `建议: 移除网络相关描述或更新网络访问声明`
            );
          }
        }
      }
    }
    
    // 检查安全声明矛盾
    if (declarations.securityClaims && declarations.securityClaims.length > 0) {
      for (const rule of this.contradictionRules) {
        if (rule.name === '安全声明矛盾') {
          const foundKeywords = this.findKeywordsInText(docContent.text, rule.vulnerabilityKeywords);
          if (foundKeywords.length > 0) {
            this.results.warnings.push(
              `${rule.message}:\n` +
              `检测到的危险函数: ${foundKeywords.join(', ')}\n` +
              `建议: 审查代码安全性或更新安全声明`
            );
          }
        }
      }
    }
  }

  async checkContentConsistency(skillPath) {
    // 检查技能名称一致性
    await this.checkSkillNameConsistency(skillPath);
    
    // 检查描述一致性
    await this.checkDescriptionConsistency(skillPath);
    
    // 检查标签一致性
    await this.checkTagsConsistency(skillPath);
  }

  async checkSkillNameConsistency(skillPath) {
    const names = new Set();
    
    // 从不同文件提取技能名称
    const filesToCheck = [
      { file: 'config.yaml', extractor: this.extractNameFromConfigYaml },
      { file: '_meta.json', extractor: this.extractNameFromMetaJson },
      { file: 'SKILL.md', extractor: this.extractNameFromSkillMd },
      { file: 'README.md', extractor: this.extractNameFromReadmeMd }
    ];
    
    for (const { file, extractor } of filesToCheck) {
      const filePath = path.join(skillPath, file);
      if (await this.fileExists(filePath)) {
        try {
          const content = await fs.readFile(filePath, 'utf8');
          const name = await extractor.call(this, content);
          if (name) {
            names.add(name.trim().toLowerCase());
          }
        } catch (error) {
          // 忽略解析错误
        }
      }
    }
    
    if (names.size > 1) {
      this.results.passed = false;
      this.results.errors.push(
        `技能名称不一致:\n` +
        `发现的不同名称: ${Array.from(names).join(', ')}\n` +
        `建议: 统一所有文件中的技能名称`
      );
    }
  }

  extractNameFromConfigYaml(content) {
    try {
      const yaml = require('js-yaml');
      const config = yaml.load(content);
      return config.name;
    } catch {
      return null;
    }
  }

  extractNameFromMetaJson(content) {
    try {
      const meta = JSON.parse(content);
      return meta.name || meta.slug;
    } catch {
      return null;
    }
  }

  extractNameFromSkillMd(content) {
    // 查找标题中的名称
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1] : null;
  }

  extractNameFromReadmeMd(content) {
    // 查找标题中的名称
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1] : null;
  }

  async checkDescriptionConsistency(skillPath) {
    // 实现描述一致性检查
    // 可以比较不同文件中的描述是否一致
  }

  async checkTagsConsistency(skillPath) {
    // 实现标签一致性检查
  }

  findKeywordsInText(text, keywords) {
    const found = [];
    const lowerText = text.toLowerCase();
    
    for (const keyword of keywords) {
      if (lowerText.includes(keyword.toLowerCase())) {
        found.push(keyword);
      }
    }
    
    return found;
  }

  extractKeywords(content, filename, keywordMap) {
    const words = content.toLowerCase().split(/\W+/);
    
    for (const word of words) {
      if (word.length > 3) { // 只考虑长度大于3的单词
        if (!keywordMap[word]) {
          keywordMap[word] = [];
        }
        if (!keywordMap[word].includes(filename)) {
          keywordMap[word].push(filename);
        }
      }
    }
  }

  shouldCheckDocumentationFile(filename) {
    const docExtensions = ['.md', '.txt', '.rst', '.yaml', '.yml', '.json'];
    const ext = path.extname(filename).toLowerCase();
    return docExtensions.includes(ext);
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

module.exports = ContentConsistencyChecker;