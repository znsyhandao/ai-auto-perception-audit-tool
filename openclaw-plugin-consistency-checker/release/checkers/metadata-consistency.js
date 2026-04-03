class MetadataConsistencyChecker {
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
          `版本号不一致:\n` +
          Object.entries(versions).map(([source, ver]) => `  ${source}: ${ver}`).join('\n')
        );
      }
    }
    
    if (Object.keys(authors).length > 1) {
      const authorValues = Object.values(authors);
      const firstAuthor = authorValues[0];
      const inconsistent = authorValues.some(a => a !== firstAuthor);
      
      if (inconsistent) {
        this.results.warnings.push(
          `作者信息不一致:\n` +
          Object.entries(authors).map(([source, author]) => `  ${source}: ${author}`).join('\n')
        );
      }
    }
    
    if (Object.keys(names).length > 1) {
      const nameValues = Object.values(names);
      const firstName = nameValues[0];
      const inconsistent = nameValues.some(n => n !== firstName);
      
      if (inconsistent) {
        this.results.warnings.push(
          `技能名称不一致:\n` +
          Object.entries(names).map(([source, name]) => `  ${source}: ${name}`).join('\n')
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
