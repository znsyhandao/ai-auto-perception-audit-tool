# Publishing Guide

## 🚀 Publishing to ClawHub

### Prerequisites:
1. Node.js and npm installed
2. ClawHub account registered
3. Logged into ClawHub CLI

### Steps:

#### 1. Login to ClawHub
```bash
npx clawhub login
```

#### 2. Prepare Release Package
Ensure release package is created:
```bash
# Run release script
node scripts/simple_release.js

# Or create ZIP manually
# Include all required files, exclude node_modules, etc.
```

#### 3. Publish to ClawHub
```bash
# Publish current directory
npx clawhub publish

# Or publish specific ZIP package
npx clawhub publish openclaw-consistency-checker-1.0.0.zip
```

#### 4. Verify Publication
```bash
# Search for your plugin
npx clawhub search consistency-checker

# View plugin information
npx clawhub info @znsyhandao/openclaw-consistency-checker
```

#### 5. Test Installation
```bash
# Install from ClawHub
npx clawhub install @znsyhandao/openclaw-consistency-checker

# Test the plugin
npx openclaw-consistency-checker --help
```

## 📦 Version Management

### Semantic Versioning:
- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (1.X.0): Backward-compatible functionality additions
- **PATCH** (1.0.X): Backward-compatible bug fixes

### Releasing New Version:
1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Create Git tag
4. Run release script
5. Publish to ClawHub

## 🔄 Continuous Integration

### GitHub Actions Auto-release:
Automatically when Git tag is created:
1. Run tests
2. Create release package
3. Publish to ClawHub (requires secret configuration)

### Configure GitHub Secrets:
1. `CLAWHUB_TOKEN`: ClawHub API token
2. `NPM_TOKEN`: npm publish token (if needed)

## 📝 Changelog Requirements

### CHANGELOG.md Format:
```markdown
# Changelog

## [1.0.0] - 2026-04-02
### Added
- Initial release
- Core consistency check functionality

### Fixed
- Dependency issues
- Improved error handling

### Changed
- Updated documentation
- Performance optimizations
```

## 🛡️ Quality Assurance

### Pre-release Checklist:
- [ ] All tests pass
- [ ] Documentation complete and accurate
- [ ] Version numbers consistent
- [ ] No sensitive information leaked
- [ ] License file correct
- [ ] Dependencies updated

### Post-release Verification:
- [ ] Plugin installs correctly
- [ ] Basic functionality works
- [ ] Documentation links valid
- [ ] Example code runs

## 🤝 Community Publishing

### Promotion Channels:
1. **OpenClaw Discord** - Official community
2. **GitHub Discussions** - Project discussions
3. **Technical Blogs** - Tutorial articles
4. **Social Media** - Twitter, LinkedIn

### Collecting Feedback:
1. **GitHub Issues** - Problem reports
2. **Discord Channels** - Real-time discussions
3. **User Surveys** - Usage experience

## 🔧 Troubleshooting

### Common Issues:

#### Publication Failure:
```bash
# Check network connection
ping clawhub.com

# Check login status
npx clawhub whoami

# Check package size limits
# ClawHub may have file size limits
```

#### Installation Failure:
```bash
# Clear cache
npx clawhub cache clean

# Reinstall
npx clawhub install @znsyhandao/openclaw-consistency-checker --force
```

#### Plugin Not Working:
```bash
# Check dependencies
npm list

# Run tests
npm test

# View logs
npx openclaw-consistency-checker --verbose
```

## 📞 Support

### Getting Help:
1. **ClawHub Documentation**: https://docs.clawhub.com
2. **OpenClaw Discord**: https://discord.gg/clawd
3. **GitHub Issues**: Project issue tracking

### Emergency Contact:
- Security issues: security@your-org.com
- Legal issues: legal@your-org.com
- Technical support: support@your-org.com

---

**Happy Publishing!** 🚀