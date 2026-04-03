const path = require('path');

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
    console.log('[ConsistencyChecker] Checking 网络声明一致性...');
    
    const claimsNetwork = this.extractNetworkClaims(metadata);
    const detectedNetwork = this.detectNetworkInDocs(docContents);
    
    if (detectedNetwork.hasNetworkDescription && !claimsNetwork.allowsNetwork) {
      this.results.passed = false;
      this.results.errors.push(
        `文档中检测到网络相关描述，但元数据声明 runtime_network_access=false\n` +
        `检测到的网络术语: ${detectedNetwork.terms.join(', ')}\n` +
        `涉及文件: ${detectedNetwork.files.join(', ')}`
      );
    }
    
    if (detectedNetwork.ports.length > 0 && !claimsNetwork.allowsNetwork) {
      this.results.errors.push(
        `文档中检测到端口描述 (${detectedNetwork.ports.join(', ')})，` +
        `但声明为无网络访问`
      );
    }
    
    if (detectedNetwork.externalServices.length > 0) {
      this.results.warnings.push(
        `文档中引用了外部服务: ${detectedNetwork.externalServices.join(', ')}，` +
        `请确认这些服务是否实际需要`
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
      ports: /port\s+(\d{4,5})|:(\d{4,5})\b/gi,
      service: /(?:service|api|endpoint|server)\s+([a-z0-9\-\.]+)/gi
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


