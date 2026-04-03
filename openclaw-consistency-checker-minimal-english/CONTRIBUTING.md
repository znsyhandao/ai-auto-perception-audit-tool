# Contributing Guide

Thank you for considering contributing to the OpenClaw Consistency Checker! This document provides guidelines and instructions for contributing.

## 🎯 Contribution Methods

### 1. Report Issues
Found a bug or have a feature request? Please create an issue:
- **Bug reports**: Include steps to reproduce, expected vs actual behavior
- **Feature requests**: Describe the use case and benefits
- **Documentation issues**: Report unclear or missing documentation

### 2. Submit Pull Requests
Want to fix a bug or add a feature? Submit a PR:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 3. Improve Documentation
Help improve our documentation:
- Fix typos and grammatical errors
- Add examples and tutorials
- Translate documentation (English only for now)

### 4. Share Feedback
- Use the tool and share your experience
- Suggest improvements on Discord
- Share success stories and use cases

## 🛠️ Development Setup

### Prerequisites:
- Node.js 18.x or higher
- npm 8.x or higher
- Git

### Setup Steps:
```bash
# 1. Clone the repository
git clone https://github.com/znsyhandao/openclaw-consistency-checker.git
cd openclaw-consistency-checker

# 2. Install dependencies
npm install

# 3. Run tests
npm test

# 4. Run consistency check on itself
node cli.js . --level strict
```

### Project Structure:
```
checkers/          # Checker modules
utils/             # Utility functions
examples/          # Usage examples
scripts/           # Build and release scripts
test/              # Test files
```

## 📝 Code Guidelines

### JavaScript/Node.js:
- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use async/await for asynchronous operations
- Add JSDoc comments for public APIs

### Testing:
- Write unit tests for new features
- Maintain test coverage > 80%
- Use Jest testing framework
- Test both success and failure cases

### Documentation:
- Keep all documentation in English
- Use clear, concise language
- Include code examples
- Update documentation when code changes

### Commit Messages:
Follow Conventional Commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

Example: `feat: add version consistency checker`

## 🔍 Code Review Process

### Pull Request Requirements:
1. **Tests pass**: All tests must pass
2. **Code quality**: Follow style guidelines
3. **Documentation**: Update relevant documentation
4. **Backward compatibility**: Don't break existing functionality
5. **Performance**: Consider performance implications

### Review Checklist:
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance considered

### Review Timeline:
- Initial review within 48 hours
- Feedback provided within 3 days
- Merge within 7 days if no issues

## 🧪 Testing

### Running Tests:
```bash
# Run all tests
npm test

# Run specific test file
npm test -- checkers/version-consistency.test.js

# Run with coverage
npm run test:coverage
```

### Test Structure:
- Unit tests for individual functions
- Integration tests for checker modules
- End-to-end tests for CLI functionality
- Mock file systems for file operations

### Adding Tests:
1. Create test file next to source file
2. Test both success and failure cases
3. Use descriptive test names
4. Mock external dependencies

## 📦 Release Process

### Versioning:
Follow Semantic Versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps:
1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Create Git tag (`git tag v1.0.0`)
4. Push tag (`git push origin v1.0.0`)
5. Create GitHub release
6. Publish to ClawHub (`npx clawhub publish`)

### Changelog Format:
```markdown
# Changelog

## [1.0.0] - 2026-04-02
### Added
- Initial release
- Core consistency checkers

### Fixed
- Dependency issues
- Error handling improvements

### Changed
- Documentation updates
- Performance optimizations
```

## 🐛 Issue Triage

### Issue Labels:
- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation issues
- `question`: Questions about usage
- `help wanted`: Extra attention needed
- `good first issue`: Good for newcomers

### Issue Priority:
- **P0**: Critical bug affecting core functionality
- **P1**: Important bug or feature
- **P2**: Nice-to-have improvements
- **P3**: Documentation or minor issues

## 🏆 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation
- Community announcements

## ❓ Getting Help

### Resources:
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time discussion (#tools channel)
- **Documentation**: This file and README.md
- **Examples**: `examples/` directory

### Contact:
- Open an issue for technical questions
- Join OpenClaw Discord for community support
- Check existing issues before creating new ones

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to the OpenClaw ecosystem!** 🚀