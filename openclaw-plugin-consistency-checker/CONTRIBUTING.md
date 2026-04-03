# 贡献指南

感谢您考虑为OpenClaw一致性检查插件做出贡献！

## 🎯 贡献方式

### 1. 报告问题
- 使用 [GitHub Issues](https://github.com/your-org/openclaw-consistency-checker/issues)
- 描述清晰的问题复现步骤
- 包含错误信息和截图

### 2. 提交功能请求
- 描述您需要的功能
- 解释为什么这个功能有用
- 提供使用场景示例

### 3. 提交代码
- Fork 项目仓库
- 创建功能分支
- 提交清晰的提交信息
- 创建 Pull Request

## 🛠️ 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/your-org/openclaw-consistency-checker.git
cd openclaw-consistency-checker
```

### 2. 安装依赖
```bash
npm install
```

### 3. 运行测试
```bash
# 运行所有测试
npm test

# 运行特定测试
node test/index.test.js
```

### 4. 开发模式
```bash
# 监视文件变化并运行测试
npm run dev
```

## 📁 项目结构

```
openclaw-plugin-consistency-checker/
├── index.js                    # 主插件入口
├── cli_fixed.js               # 命令行界面
├── test_simple.js             # 简化测试
├── checkers/                  # 检查器模块
│   ├── metadata-consistency.js
│   ├── network-consistency.js
│   ├── provenance-check.js
│   ├── version-consistency.js
│   └── content-consistency.js
├── utils/                     # 工具函数
├── test/                      # 测试文件
├── scripts/                   # 构建脚本
├── docs/                      # 文档
└── examples/                  # 使用示例
```

## 🔧 添加新的检查器

### 1. 创建检查器文件
在 `checkers/` 目录中创建新的检查器文件：

```javascript
// checkers/new-checker.js
class NewChecker {
  constructor(config) {
    this.config = config;
    this.results = {
      passed: true,
      errors: [],
      warnings: []
    };
  }

  async check(metadata, skillPath) {
    // 实现检查逻辑
    return this.results;
  }
}

module.exports = NewChecker;
```

### 2. 注册检查器
在 `index.js` 中注册新的检查器：

```javascript
const NewChecker = require('./checkers/new-checker');

// 在构造函数中添加
this.checkers = [
  // ... 其他检查器
  new NewChecker(this.config)
];
```

### 3. 编写测试
为新的检查器编写测试：

```javascript
// test/new-checker.test.js
describe('NewChecker', () => {
  it('should detect specific issues', async () => {
    // 测试逻辑
  });
});
```

## 📝 代码规范

### 1. 代码风格
- 使用 2 空格缩进
- 使用单引号
- 添加必要的注释
- 遵循现有的代码风格

### 2. 提交信息
使用约定式提交：
- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 代码重构
- `chore:` 构建过程或辅助工具

示例：
```
feat: add version consistency checker
fix: resolve chalk dependency issue
docs: update README with usage examples
```

### 3. 测试要求
- 新功能必须包含测试
- 修复问题必须包含回归测试
- 测试覆盖率不低于 80%

## 🚀 发布流程

### 1. 版本管理
使用语义化版本：
- `MAJOR` 不兼容的API修改
- `MINOR` 向下兼容的功能性新增
- `PATCH` 向下兼容的问题修正

### 2. 发布步骤
```bash
# 1. 更新版本号
npm version patch  # 或 minor, major

# 2. 运行测试
npm test

# 3. 创建发布包
node scripts/release.js

# 4. 发布到ClawHub
npx clawhub publish
```

### 3. 更新文档
- 更新 README.md
- 更新 CHANGELOG.md
- 更新 API 文档

## 🤝 行为准则

### 1. 尊重他人
- 保持友好和专业的交流
- 尊重不同的观点和经验
- 建设性地提出批评

### 2. 包容性
- 欢迎来自不同背景的贡献者
- 使用包容性语言
- 为所有人创造友好的环境

### 3. 责任
- 对自己的贡献负责
- 及时回应问题和反馈
- 帮助维护项目质量

## 📞 获取帮助

### 1. 文档
- [README.md](README.md) - 基本使用
- [API文档](docs/api.md) - 详细API说明
- [示例](examples/) - 使用示例

### 2. 社区
- [GitHub Discussions](https://github.com/your-org/openclaw-consistency-checker/discussions)
- [OpenClaw Discord](https://discord.com/invite/clawd)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/openclaw)

### 3. 问题跟踪
- [GitHub Issues](https://github.com/your-org/openclaw-consistency-checker/issues)
- [功能请求](https://github.com/your-org/openclaw-consistency-checker/issues/new?template=feature_request.md)
- [Bug报告](https://github.com/your-org/openclaw-consistency-checker/issues/new?template=bug_report.md)

## 🙏 致谢

感谢所有为这个项目做出贡献的人！您的帮助让OpenClaw生态更加强大。

---

**让我们一起构建更好的OpenClaw工具！** 🚀