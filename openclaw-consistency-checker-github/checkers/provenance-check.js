const https = require('https');

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
        `文档中引用了GitHub (${provenance.githubUrls[0]})，` +
        `但元数据中未设置 source 字段\n` +
        `建议在 skill_info.json 中添加: "source": "${provenance.githubUrls[0]}"`
      );
    }
    
    if (provenance.explicitSource && provenance.explicitSource.includes('github.com')) {
      const isValid = await this.verifyGitHubRepo(provenance.explicitSource);
      if (!isValid) {
        this.results.warnings.push(
          `声明的GitHub仓库无法访问: ${provenance.explicitSource}\n` +
          `请确认仓库地址正确且仓库公开`
        );
      }
    }
    
    if (provenance.author && provenance.githubUrls.length > 0) {
      const githubUser = this.extractGithubUser(provenance.githubUrls[0]);
      if (githubUser && provenance.author.toLowerCase() !== githubUser.toLowerCase()) {
        this.results.warnings.push(
          `作者 "${provenance.author}" 与GitHub用户名 "${githubUser}" 不一致，` +
          `请确认作者身份`
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
    
    const githubPattern = /https?:\/\/github\.com\/[a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-_]+/g;
    for (const content of Object.values(docContents)) {
      const matches = content.match(githubPattern);
      if (matches) provenance.githubUrls.push(...matches);
    }
    
    provenance.githubUrls = [...new Set(provenance.githubUrls)];
    return provenance;
  }

  extractGithubUser(githubUrl) {
    const match = githubUrl.match(/github\.com\/([a-zA-Z0-9\-_]+)/);
    return match ? match[1] : null;
  }

  async verifyGitHubRepo(repoUrl) {
    return new Promise((resolve) => {
      const match = repoUrl.match(/github\.com\/([^\/]+\/[^\/]+)/);
      if (!match) {
        resolve(false);
        return;
      }
      
      const apiUrl = `https://api.github.com/repos/${match[1]}`;
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
