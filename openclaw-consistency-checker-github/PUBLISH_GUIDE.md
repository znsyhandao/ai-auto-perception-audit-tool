# 发布指南

## 🚀 发布到ClawHub

### 前提条件：
1. 已安装 Node.js 和 npm
2. 已注册 ClawHub 账户
3. 已登录 ClawHub CLI

### 步骤：

#### 1. 登录 ClawHub
```bash
npx clawhub login
```

#### 2. 准备发布包
确保已创建发布包：
```bash
# 运行发布脚本
node scripts/simple_release.js

# 或手动创建ZIP包
# 包含所有必需文件，排除node_modules等
```

#### 3. 发布到 ClawHub
```bash
# 发布当前目录
npx clawhub publish

# 或发布指定ZIP包
npx clawhub publish openclaw-consistency-checker-1.0.0.zip
```

#### 4. 验证发布
```bash
# 搜索你的插件
npx clawhub search consistency-checker

# 查看插件信息
npx clawhub info @your-org/openclaw-consistency-checker
```

#### 5. 测试安装
```bash
# 从ClawHub安装
npx clawhub install @your-org/openclaw-consistency-checker

# 测试插件
npx openclaw-consistency-checker --help
```

## 📦 版本管理

### 语义化版本：
- **MAJOR** (X.0.0): 不兼容的API修改
- **MINOR** (1.X.0): 向下兼容的功能性新增
- **PATCH** (1.0.X): 向下兼容的问题修正

### 发布新版本：
1. 更新 `package.json` 中的版本号
2. 更新 `CHANGELOG.md`
3. 创建 Git tag
4. 运行发布脚本
5. 发布到 ClawHub

## 🔄 持续集成

### GitHub Actions 自动发布：
当创建 Git tag 时自动：
1. 运行测试
2. 创建发布包
3. 发布到 ClawHub (需要配置密钥)

### 配置 GitHub Secrets：
1. `CLAWHUB_TOKEN`: ClawHub API 令牌
2. `NPM_TOKEN`: npm 发布令牌 (如果需要)

## 📝 更新日志要求

### CHANGELOG.md 格式：
```markdown
# Changelog

## [1.0.0] - 2026-04-02
### Added
- 初始版本发布
- 一致性检查核心功能

### Fixed
- 修复依赖问题
- 改进错误处理

### Changed
- 更新文档
- 优化性能
```

## 🛡️ 质量保证

### 发布前检查清单：
- [ ] 所有测试通过
- [ ] 文档完整且准确
- [ ] 版本号一致
- [ ] 无敏感信息泄露
- [ ] 许可证文件正确
- [ ] 依赖项已更新

### 发布后验证：
- [ ] 插件能正常安装
- [ ] 基本功能正常工作
- [ ] 文档链接有效
- [ ] 示例代码可运行

## 🤝 社区发布

### 推广渠道：
1. **OpenClaw Discord** - 官方社区
2. **GitHub Discussions** - 项目讨论
3. **技术博客** - 教程文章
4. **社交媒体** - Twitter, LinkedIn

### 收集反馈：
1. **GitHub Issues** - 问题报告
2. **Discord 频道** - 实时讨论
3. **用户调查** - 使用体验

## 🔧 故障排除

### 常见问题：

#### 发布失败：
```bash
# 检查网络连接
ping clawhub.com

# 检查登录状态
npx clawhub whoami

# 检查包大小限制
# ClawHub可能有文件大小限制
```

#### 安装失败：
```bash
# 清理缓存
npx clawhub cache clean

# 重新安装
npx clawhub install @your-org/openclaw-consistency-checker --force
```

#### 插件不工作：
```bash
# 检查依赖
npm list

# 运行测试
npm test

# 查看日志
npx openclaw-consistency-checker --verbose
```

## 📞 支持

### 获取帮助：
1. **ClawHub 文档**: https://docs.clawhub.com
2. **OpenClaw Discord**: https://discord.gg/clawd
3. **GitHub Issues**: 项目问题跟踪

### 紧急联系：
- 安全问题: security@your-org.com
- 法律问题: legal@your-org.com
- 技术支持: support@your-org.com

---

**祝发布顺利！** 🚀