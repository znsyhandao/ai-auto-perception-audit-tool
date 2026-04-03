const fs = require('fs').promises;
const path = require('path');

// Simple color output
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
    
    // Content declaration contradiction detection rules
    this.contradictionRules = [
      {
        name: 'religious_content_contradiction',
        description: 'Claims "no religious content" but includes religious terms',
        positiveClaims: ['no religious content', 'secular', 'non-religious'],
        negativeTerms: ['loving-kindness', 'buddhist', 'christian', 'islamic', 'hindu', 'spiritual'],
        severity: 'error'
      },
      {
        name: 'network_access_contradiction',
        description: 'Claims "no network access" but includes network calls',
        positiveClaims: ['no network access', 'runtime_network_access: false', '100% local'],
        negativePatterns: ['http://', 'https://', 'fetch(', 'axios', 'request(', 'api.'],
        severity: 'error'
      },
      {
        name: 'security_contradiction',
        description: 'Claims "secure" but uses dangerous functions',
        positiveClaims: ['secure', 'safe', 'no vulnerabilities'],
        negativePatterns: ['eval(', 'exec(', 'system(', 'subprocess.', 'dangerous'],
        severity: 'warning'
      }
    ];
  }

  async check(metadata, skillPath) {
    console.log(color.blue('[ContentConsistency] Checking content declarations...'));
    
    try {
      // Check config.yaml declarations
      await this.checkConfigDeclarations(metadata);
      
      // Check SKILL.md content
      await this.checkSkillDocumentation(skillPath);
      
      // Check source code for contradictions
      await this.checkSourceCode(skillPath);
      
    } catch (error) {
      console.error(`[ContentConsistency] Error: ${error.message}`);
      this.results.errors.push(`Content consistency check failed: ${error.message}`);
      this.results.passed = false;
    }
    
    return this.results;
  }

  async checkConfigDeclarations(metadata) {
    if (!metadata || !metadata.security || !metadata.security.claims) {
      return;
    }
    
    const claims = metadata.security.claims;
    
    // Check each contradiction rule
    for (const rule of this.contradictionRules) {
      const hasPositiveClaim = claims.some(claim => 
        rule.positiveClaims.some(positive => 
          claim.toLowerCase().includes(positive.toLowerCase())
        )
      );
      
      if (hasPositiveClaim) {
        // This skill claims something positive, check for contradictions
        console.log(color.blue(`[ContentConsistency] Checking: ${rule.description}`));
      }
    }
  }

  async checkSkillDocumentation(skillPath) {
    const skillMdPath = path.join(skillPath, 'SKILL.md');
    
    try {
      const content = await fs.readFile(skillMdPath, 'utf8');
      const lowerContent = content.toLowerCase();
      
      // Check for contradictions in documentation
      for (const rule of this.contradictionRules) {
        const hasPositiveClaim = rule.positiveClaims.some(claim => 
          lowerContent.includes(claim.toLowerCase())
        );
        
        if (hasPositiveClaim) {
          // Check for negative terms
          if (rule.negativeTerms) {
            for (const term of rule.negativeTerms) {
              if (lowerContent.includes(term.toLowerCase())) {
                this.addContradiction(rule, term, 'SKILL.md');
              }
            }
          }
          
          if (rule.negativePatterns) {
            for (const pattern of rule.negativePatterns) {
              if (content.includes(pattern)) {
                this.addContradiction(rule, pattern, 'SKILL.md');
              }
            }
          }
        }
      }
    } catch (error) {
      // SKILL.md might not exist, that's okay
    }
  }

  async checkSourceCode(skillPath) {
    // Check Python files
    const pyFiles = await this.findFiles(skillPath, '.py');
    
    for (const file of pyFiles) {
      try {
        const content = await fs.readFile(file, 'utf8');
        
        for (const rule of this.contradictionRules) {
          if (rule.negativePatterns) {
            for (const pattern of rule.negativePatterns) {
              if (content.includes(pattern)) {
                const relativePath = path.relative(skillPath, file);
                this.addContradiction(rule, pattern, relativePath);
              }
            }
          }
        }
      } catch (error) {
        // Skip files we can't read
      }
    }
  }

  addContradiction(rule, foundItem, location) {
    const message = `${rule.description}: Found "${foundItem}" in ${location}`;
    
    if (rule.severity === 'error') {
      this.results.errors.push(message);
      this.results.passed = false;
    } else {
      this.results.warnings.push(message);
    }
    
    console.log(color.blue(`[ContentConsistency] ${rule.severity.toUpperCase()}: ${message}`));
  }

  async findFiles(directory, extension) {
    const files = [];
    
    async function traverse(dir) {
      try {
        const items = await fs.readdir(dir);
        
        for (const item of items) {
          const fullPath = path.join(dir, item);
          const stat = await fs.stat(fullPath).catch(() => null);
          
          if (!stat) continue;
          
          if (stat.isDirectory()) {
            // Skip certain directories
            if (!['node_modules', '__pycache__', '.git'].includes(item)) {
              await traverse(fullPath);
            }
          } else if (item.endsWith(extension)) {
            files.push(fullPath);
          }
        }
      } catch (error) {
        // Skip directories we can't access
      }
    }
    
    await traverse(directory);
    return files;
  }
}

module.exports = ContentConsistencyChecker;