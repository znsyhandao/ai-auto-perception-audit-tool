# OpenClaw Consistency Checker

A powerful OpenClaw plugin for detecting consistency issues and document-metadata contradictions in skill development.

## 🎯 Problems Solved

### Did you encounter these issues today?
- **Version inconsistency** - Different version numbers in config.yaml, _meta.json, CHANGELOG.md
- **Name inconsistency** - Different naming formats across files (kebab-case vs Title Case)
- **Content declaration contradictions** - Claims "no religious content" but includes "loving-kindness"
- **Cache file issues** - __pycache__/.pyc files causing ClawHub audit failures
- **Historical reference problems** - Old references like "sleep-rabbit" causing registry pollution

## ✨ Features

### Core Checkers:
1. **Version Consistency Checker** - Cross-file version number validation
2. **Name Consistency Checker** - Unified naming format verification
3. **Content Declaration Checker** - Semantic analysis for content contradictions
4. **Network Consistency Checker** - Network access declaration validation
5. **Provenance Checker** - Source code and dependency verification

### Advanced Features:
- **Automated fix suggestions** - Specific modification recommendations
- **Comprehensive reporting** - Detailed error explanations and solutions
- **Multiple output formats** - Console, JSON, Markdown reports
- **CI/CD integration** - GitHub Actions, GitLab CI, Jenkins support

## 🚀 Quick Start

### Installation from ClawHub:
```bash
npx clawhub install @znsyhandao/openclaw-consistency-checker
```

### Basic Usage:
```bash
# Check a skill directory
npx openclaw-consistency-checker /path/to/your-skill

# Generate detailed report
npx openclaw-consistency-checker /path/to/your-skill --report

# Try to auto-fix issues
npx openclaw-consistency-checker /path/to/your-skill --fix

# JSON output for CI/CD
npx openclaw-consistency-checker /path/to/your-skill --json
```

### Direct Usage (Node.js):
```javascript
const ConsistencyChecker = require('@znsyhandao/openclaw-consistency-checker');

const checker = new ConsistencyChecker({
  level: 'strict',
  verbose: true,
  autoFix: false
});

const results = await checker.runChecks('/path/to/skill');
console.log(JSON.stringify(results, null, 2));
```

## 📋 What This Tool Checks

### 1. Version Consistency
- config.yaml version vs _meta.json version
- Package version vs CHANGELOG.md versions
- File-internal version references

### 2. Name Consistency
- Skill name in config.yaml vs SKILL.md title
- Naming format consistency (kebab-case, Title Case, snake_case)
- Historical reference detection (e.g., "sleep-rabbit" references)

### 3. Content Declaration Validation
- "No religious content" but includes religious terms
- "No network access" but uses HTTP/API calls
- Security claim contradictions
- Privacy policy compliance

### 4. File Structure Validation
- Required files existence (skill.py, config.yaml, etc.)
- Cache file detection (__pycache__, *.pyc)
- File encoding and format validation

### 5. Metadata Consistency
- Author information consistency
- Description alignment across files
- Tag and category validation

## 🔧 Configuration

Create `consistency-checker.config.js`:
```javascript
module.exports = {
  level: 'strict', // 'basic' | 'strict' | 'paranoid'
  autoFix: false,
  verbose: true,
  quiet: false,
  
  ignore: [
    'node_modules',
    '__pycache__',
    '*.pyc',
    '*.log',
    '.git',
    '.vscode'
  ],
  
  checks: {
    metadata: true,
    network: true,
    provenance: true,
    version: true,
    content: true
  },
  
  rules: {
    versionConsistency: {
      enabled: true,
      strict: true
    },
    nameConsistency: {
      enabled: true,
      caseSensitive: false
    },
    contentContradictions: {
      enabled: true,
      checkReligious: true,
      checkNetwork: true,
      checkSecurity: true
    }
  }
};
```

## 📊 Integration Examples

### GitHub Actions:
```yaml
name: Consistency Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Consistency Check
        run: |
          npx @znsyhandao/openclaw-consistency-checker . --level strict
          if [ $? -ne 0 ]; then exit 1; fi
```

### Pre-commit Hook:
```bash
#!/bin/bash
# .git/hooks/pre-commit
npx openclaw-consistency-checker . --level basic
if [ $? -ne 0 ]; then
  echo "❌ Consistency check failed. Please fix issues before committing."
  exit 1
fi
```

### Build Script Integration:
```bash
#!/bin/bash
# build.sh
echo "🔨 Building OpenClaw skill..."

# Run consistency check
echo "📋 Running consistency check..."
npx openclaw-consistency-checker . --level strict

if [ $? -ne 0 ]; then
  echo "❌ Consistency check failed. Please fix issues."
  exit 1
fi

# Continue with build process...
```

## 🏗️ Project Structure

```
openclaw-consistency-checker/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── package.json                 # Node.js configuration
├── index.js                     # Main plugin entry point
├── cli.js                       # Command-line interface
├── checkers/                    # Checker modules
│   ├── metadata-consistency.js  # Metadata consistency
│   ├── network-consistency.js   # Network consistency
│   ├── provenance-check.js      # Source verification
│   ├── version-consistency.js   # Version consistency
│   └── content-consistency.js   # Content consistency
├── utils/                       # Utility functions
│   ├── file-scanner.js          # File scanning utilities
│   └── pattern-matcher.js       # Pattern matching
├── examples/                    # Usage examples
│   ├── config.example.json      # Configuration example
│   └── usage-example.js         # Usage examples
└── scripts/                     # Build and release scripts
    └── simple_release.js        # Release script
```

## 📈 Performance

- **Check time**: < 1 second (average)
- **Memory usage**: < 50MB
- **File support**: .yaml, .yml, .json, .md, .py, .js, .txt
- **Skill size**: Up to 1000 files, 100MB total

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup:
```bash
# Clone repository
git clone https://github.com/znsyhandao/openclaw-consistency-checker.git
cd openclaw-consistency-checker

# Install dependencies
npm install

# Run tests
npm test

# Run consistency check on itself
node cli.js . --level strict
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub**: https://github.com/znsyhandao/openclaw-consistency-checker
- **ClawHub**: `@znsyhandao/openclaw-consistency-checker`
- **Issues**: https://github.com/znsyhandao/openclaw-consistency-checker/issues
- **Discussions**: OpenClaw Discord #tools channel

## 🙏 Acknowledgments

This tool was born from real pain points encountered during OpenClaw skill development on April 2, 2026. Special thanks to the OpenClaw community for their feedback and support.

---

**Made with ❤️ for the OpenClaw community**