const fs = require('fs');
const path = require('path');

const PLUGIN_NAME = 'consistency-checker';
const PLUGIN_DIR = `openclaw-plugin-${PLUGIN_NAME}`;

// 确保目录存在
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

// 写入文件
function writeFile(filePath, content) {
  const fullPath = path.join(PLUGIN_DIR, filePath);
  ensureDir(path.dirname(fullPath));
  fs.writeFileSync(fullPath, content, 'utf8');
  console.log(`✅ 创建: ${filePath}`);
}

// 1. plugin.json
writeFile('plugin.json', JSON.stringify({
  name: "consistency-checker",
  version: "1.0.0",
  description: "检测文档-元数据矛盾，确保提交前一致性",
  author: "Your Name",
  main: "index.js",
  hooks: {
    "audit:pre": "runConsistencyChecks"
  },
  config: {
    strictMode: true,
    failOnWarning: false,
    scanPatterns: {
      networkTerms: ["port\\s+\\d+", "http://", "https://", "socket", "server", "listening on", "\\b\\d{1,5}\\b.*service"],
      urlPatterns: ["github\\.com", "gitlab\\.com", "bitbucket\\.org", "\\bhttps?://[^\\s]+\\b"],
      versionPatterns: ["version\\s*[=:]\\s*[\\d.]+", "v\\d+\\.\\d+\\.\\d+"]
    }
  }
}, null, 2));

// 2. package.json
writeFile('package.json', JSON.stringify({
  name: "@your-org/openclaw-consistency-checker",
  version: "1.0.0",
  description: "OpenClaw插件：检测文档-元数据矛盾",
  main: "index.js",
  keywords: ["openclaw", "plugin", "consistency", "audit"],
  author: "Your Name",
  license: "MIT",
  dependencies: {
    "js-yaml": "^4.1.0"
  },
  peerDependencies: {
    "openclaw": ">=1.0.0"
  }
}, null, 2));

// 3. index.js
writeFile('index.js', `const fs = require('fs').promises;
const path = require('path');
const NetworkConsistencyChecker = require('./checkers/network-consistency');
const MetadataConsistencyChecker = require('./checkers/metadata-consistency');
const ProvenanceChecker = require('./checkers/provenance-check');

class ConsistencyCheckerPlugin {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
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
    const lines = content.split('\\n');
    
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
        console.warn(\`无法读取文件: \${filePath}\`);
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
    console.log('\\n========== 一致性检查结果 ==========');
    
    if (this.results.errors.length > 0) {
      console.log('\\n❌ 错误:');
      this.results.errors.forEach(err => console.log(\`  - \${err}\`));
    }
    
    if (this.results.warnings.length > 0) {
      console.log('\\n⚠️  警告:');
      this.results.warnings.forEach(warn => console.log(\`  - \${warn}\`));
    }
    
    if (this.results.passed) {
      console.log('\\n✅ 所有检查通过！');
    } else {
      console.log('\\n❌ 检查失败，请修复上述问题后重新提交');
    }
    
    console.log('====================================\\n');
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
`);

// 4. checkers/network-consistency.js
writeFile('checkers/network-consistency.js', `const path = require('path');

class NetworkConsistencyChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
  }

  async check(metadata, docContents, docFiles) {
    console.log('[NetworkConsistency] 检查网络声明一致性...');
    
    const claimsNetwork = this.extractNetworkClaims(metadata);
    const detectedNetwork = this.detectNetworkInDocs(docContents);
    
    if (detectedNetwork.hasNetworkDescription && !claimsNetwork.allowsNetwork) {
      this.results.passed = false;
      this.results.errors.push(
        \`文档中检测到网络相关描述，但元数据声明 runtime_network_access=false\\n\` +
        \`检测到的网络术语: \${detectedNetwork.terms.join(', ')}\\n\` +
        \`涉及文件: \${detectedNetwork.files.join(', ')}\`
      );
    }
    
    if (detectedNetwork.ports.length > 0 && !claimsNetwork.allowsNetwork) {
      this.results.errors.push(
        \`文档中检测到端口描述 (\${detectedNetwork.ports.join(', ')})，\` +
        \`但声明为无网络访问\`
      );
    }
    
    if (detectedNetwork.externalServices.length > 0) {
      this.results.warnings.push(
        \`文档中引用了外部服务: \${detectedNetwork.externalServices.join(', ')}，\` +
        \`请确认这些服务是否实际需要\`
      );
    }
    
    return this.results;
  }

  extractNetworkClaims(metadata) {
    let allowsNetwork = false;
    
    if (metadata.package && metadata.package.permissions) {
      if (metadata.package.permissions.includes('network') ||
          metadata.package.permissions.includes('internet')) {
        allowsNetwork = true;
      }
    }
    
    if (metadata.config && metadata.config.runtime_network_access === true) {
      allowsNetwork = true;
    }
    
    if (metadata.skillInfo && metadata.skillInfo.network_access === true) {
      allowsNetwork = true;
    }
    
    return { allowsNetwork };
  }

  detectNetworkInDocs(docContents) {
    const detected = {
      hasNetworkDescription: false,
      terms: new Set(),
      files: new Set(),
      ports: new Set(),
      externalServices: new Set()
    };
    
    const networkPatterns = {
      terms: this.config.scanPatterns.networkTerms.map(p => new RegExp(p, 'i')),
      urls: this.config.scanPatterns.urlPatterns.map(p => new RegExp(p, 'i')),
      ports: /port\\s+(\\d{4,5})|:(\\d{4,5})\\b/gi,
      service: /(?:service|api|endpoint|server)\\s+([a-z0-9\\-\\.]+)/gi
    };
    
    for (const [filePath, content] of Object.entries(docContents)) {
      for (const pattern of networkPatterns.terms) {
        const matches = content.match(pattern);
        if (matches) {
          detected.hasNetworkDescription = true;
          matches.forEach(m => detected.terms.add(m));
          detected.files.add(path.basename(filePath));
        }
      }
      
      let portMatch;
      while ((portMatch = networkPatterns.ports.exec(content)) !== null) {
        const port = portMatch[1] || portMatch[2];
        detected.ports.add(port);
        detected.files.add(path.basename(filePath));
      }
      
      let serviceMatch;
      while ((serviceMatch = networkPatterns.service.exec(content)) !== null) {
        detected.externalServices.add(serviceMatch[1]);
        detected.files.add(path.basename(filePath));
      }
    }
    
    detected.terms = Array.from(detected.terms);
    detected.ports = Array.from(detected.ports);
    detected.externalServices = Array.from(detected.externalServices);
    detected.files = Array.from(detected.files);
    
    return detected;
  }
}

module.exports = NetworkConsistencyChecker;
`);

// 5. checkers/metadata-consistency.js
writeFile('checkers/metadata-consistency.js', `class MetadataConsistencyChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
  }

  async check(metadata, skillPath) {
    console.log('[MetadataConsistency] 检查元数据一致性...');
    
    const versions = this.extractVersions(metadata);
    const authors = this.extractAuthors(metadata);
    const names = this.extractNames(metadata);
    
    if (Object.keys(versions).length > 1) {
      const versionValues = Object.values(versions);
      const firstVersion = versionValues[0];
      const inconsistent = versionValues.some(v => v !== firstVersion);
      
      if (inconsistent) {
        this.results.passed = false;
        this.results.errors.push(
          \`版本号不一致:\\n\` +
          Object.entries(versions).map(([source, ver]) => \`  \${source}: \${ver}\`).join('\\n')
        );
      }
    }
    
    if (Object.keys(authors).length > 1) {
      const authorValues = Object.values(authors);
      const firstAuthor = authorValues[0];
      const inconsistent = authorValues.some(a => a !== firstAuthor);
      
      if (inconsistent) {
        this.results.warnings.push(
          \`作者信息不一致:\\n\` +
          Object.entries(authors).map(([source, author]) => \`  \${source}: \${author}\`).join('\\n')
        );
      }
    }
    
    if (Object.keys(names).length > 1) {
      const nameValues = Object.values(names);
      const firstName = nameValues[0];
      const inconsistent = nameValues.some(n => n !== firstName);
      
      if (inconsistent) {
        this.results.warnings.push(
          \`技能名称不一致:\\n\` +
          Object.entries(names).map(([source, name]) => \`  \${source}: \${name}\`).join('\\n')
        );
      }
    }
    
    return this.results;
  }

  extractVersions(metadata) {
    const versions = {};
    if (metadata.skillInfo?.version) versions.skill_info_json = metadata.skillInfo.version;
    if (metadata.package?.version) versions.package_json = metadata.package.version;
    if (metadata.skillMd?.version) versions.SKILL_md = metadata.skillMd.version;
    return versions;
  }

  extractAuthors(metadata) {
    const authors = {};
    if (metadata.skillInfo?.author) authors.skill_info_json = metadata.skillInfo.author;
    if (metadata.package?.author) {
      authors.package_json = typeof metadata.package.author === 'string' 
        ? metadata.package.author 
        : metadata.package.author.name;
    }
    if (metadata.skillMd?.author) authors.SKILL_md = metadata.skillMd.author;
    return authors;
  }

  extractNames(metadata) {
    const names = {};
    if (metadata.skillInfo?.name) names.skill_info_json = metadata.skillInfo.name;
    if (metadata.package?.name) names.package_json = metadata.package.name;
    return names;
  }
}

module.exports = MetadataConsistencyChecker;
`);

// 6. checkers/provenance-check.js
writeFile('checkers/provenance-check.js', `const https = require('https');

class ProvenanceChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
  }

  async check(metadata, docContents) {
    console.log('[Provenance] 检查来源完整性...');
    
    const provenance = this.extractProvenance(metadata, docContents);
    
    if (!provenance.explicitSource && provenance.githubUrls.length > 0) {
      this.results.warnings.push(
        \`文档中引用了GitHub (\${provenance.githubUrls[0]})，\` +
        \`但元数据中未设置 source 字段\\n\` +
        \`建议在 skill_info.json 中添加: "source": "\${provenance.githubUrls[0]}"\`
      );
    }
    
    if (provenance.explicitSource && provenance.explicitSource.includes('github.com')) {
      const isValid = await this.verifyGitHubRepo(provenance.explicitSource);
      if (!isValid) {
        this.results.warnings.push(
          \`声明的GitHub仓库无法访问: \${provenance.explicitSource}\\n\` +
          \`请确认仓库地址正确且仓库公开\`
        );
      }
    }
    
    if (provenance.author && provenance.githubUrls.length > 0) {
      const githubUser = this.extractGithubUser(provenance.githubUrls[0]);
      if (githubUser && provenance.author.toLowerCase() !== githubUser.toLowerCase()) {
        this.results.warnings.push(
          \`作者 "\${provenance.author}" 与GitHub用户名 "\${githubUser}" 不一致，\` +
          \`请确认作者身份\`
        );
      }
    }
    
    return this.results;
  }

  extractProvenance(metadata, docContents) {
    const provenance = {
      explicitSource: null,
      githubUrls: [],
      author: null,
      repoName: null
    };
    
    if (metadata.skillInfo?.source) provenance.explicitSource = metadata.skillInfo.source;
    if (metadata.skillInfo?.author) provenance.author = metadata.skillInfo.author;
    if (metadata.package?.author) {
      provenance.author = provenance.author || 
        (typeof metadata.package.author === 'string' ? metadata.package.author : metadata.package.author.name);
    }
    
    const githubPattern = /https?:\\/\\/github\\.com\\/[a-zA-Z0-9\\-_]+\\/[a-zA-Z0-9\\-_]+/g;
    for (const content of Object.values(docContents)) {
      const matches = content.match(githubPattern);
      if (matches) provenance.githubUrls.push(...matches);
    }
    
    provenance.githubUrls = [...new Set(provenance.githubUrls)];
    return provenance;
  }

  extractGithubUser(githubUrl) {
    const match = githubUrl.match(/github\\.com\\/([a-zA-Z0-9\\-_]+)/);
    return match ? match[1] : null;
  }

  async verifyGitHubRepo(repoUrl) {
    return new Promise((resolve) => {
      const match = repoUrl.match(/github\\.com\\/([^\\/]+\\/[^\\/]+)/);
      if (!match) {
        resolve(false);
        return;
      }
      
      const apiUrl = \`https://api.github.com/repos/\${match[1]}\`;
      const options = { headers: { 'User-Agent': 'OpenClaw-Consistency-Checker' } };
      
      const req = https.get(apiUrl, options, (res) => {
        resolve(res.statusCode === 200);
      });
      
      req.on('error', () => resolve(false));
      req.setTimeout(5000, () => {
        req.destroy();
        resolve(false);
      });
    });
  }
}

module.exports = ProvenanceChecker;
`);

// 7. utils/file-scanner.js
writeFile('utils/file-scanner.js', `const fs = require('fs').promises;
const path = require('path');

class FileScanner {
  constructor() {
    this.defaultExcludes = ['node_modules', '.git', 'dist', 'build', '.cache'];
  }

  async scanFiles(dir, extensions, excludeDirs = this.defaultExcludes) {
    const files = [];
    
    const scan = async (currentDir) => {
      const entries = await fs.readdir(currentDir);
      
      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry);
        const stat = await fs.stat(fullPath);
        
        if (stat.isDirectory()) {
          if (!excludeDirs.includes(entry) && !entry.startsWith('.')) {
            await scan(fullPath);
          }
        } else if (extensions.includes(path.extname(entry))) {
          files.push(fullPath);
        }
      }
    };
    
    await scan(dir);
    return files;
  }

  async readFiles(filePaths) {
    const contents = {};
    for (const filePath of filePaths) {
      try {
        contents[filePath] = await fs.readFile(filePath, 'utf8');
      } catch (err) {
        console.warn(\`无法读取文件: \${filePath}\`);
      }
    }
    return contents;
  }
}

module.exports = FileScanner;
`);

// 8. utils/pattern-matcher.js
writeFile('utils/pattern-matcher.js', `class PatternMatcher {
  constructor(patterns) {
    this.patterns = patterns.map(p => new RegExp(p, 'i'));
  }

  match(content) {
    const matches = [];
    for (const pattern of this.patterns) {
      const found = content.match(pattern);
      if (found) matches.push(...found);
    }
    return [...new Set(matches)];
  }

  matchAll(contents) {
    const results = {};
    for (const [filePath, content] of Object.entries(contents)) {
      const matches = this.match(content);
      if (matches.length > 0) {
        results[filePath] = matches;
      }
    }
    return results;
  }
}

module.exports = PatternMatcher;
`);

console.log('\n🎉 插件生成完成！');
console.log(`📁 位置: ${path.resolve(PLUGIN_DIR)}`);
console.log('\n下一步:');
console.log(`  cd ${PLUGIN_DIR}`);
console.log('  npm install');
console.log('  然后在 OpenClaw 配置中添加插件路径');