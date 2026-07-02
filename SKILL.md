# GitHub Readme Design Skill

> 为 GitHub 项目创建专业、美观、高转化率的 README.md

## 功能特性

### 🎨 设计能力

- **精美头部设计**：Logo + 标题 + 一句话介绍 + 导航链接
- **徽章系统**：版本、许可证、技术栈、Star 数量等动态徽章
- **功能展示**：表格布局、图标、要点列表
- **代码示例**：语法高亮、分步骤说明
- **项目结构**：可视化目录树
- **Star History**：增长曲线图表
- **贡献指南**：标准贡献流程

### 📐 模板系统

提供多种预设模板：

1. **标准模板** - 适用于大多数开源项目
2. **AI/ML 项目模板** - 针对机器学习项目优化
3. **CLI 工具模板** - 命令行工具专用
4. **库/框架模板** - 可复用组件库
5. **个人项目模板** - 个人作品集展示

### 🔧 工具集成

- **shields.io** - 徽章生成
- **star-history.com** - Star 历史图表
- **contrib.rocks** - 贡献者头像墙
- **GitHub Readme Stats** - 动态统计卡片
- **Typing SVG** - 打字动画效果

## 使用方法

### 基础用法

```bash
# 为现有项目生成 README
readme-magic generate --project-path /path/to/project

# 使用特定模板
readme-magic generate --template ai-project --project-path /path/to/project

# 预览生成结果
readme-magic preview --output preview.html
```

### 高级用法

```bash
# 自定义主题颜色
readme-magic generate --primary-color "#667eea" --secondary-color "#764ba2"

# 添加特定徽章
readme-magic generate --badges version,license,python,stars

# 生成 Star History
readme-magic generate --star-history --repo "owner/repo"

# 批量生成多个项目
readme-magic batch --config projects.yaml
```

## 模板结构

### 标准 README 结构

```markdown
<!-- 1. 头部区域 -->
<p align="center">
  <h1 align="center">项目名称</h1>
  <p align="center">一句话介绍</p>
  <p align="center">导航链接</p>
</p>

<!-- 2. 徽章区域 -->
<p align="center">
  <img src="badges" alt="Badges">
</p>

<!-- 3. 功能特性 -->
## ✨ 功能特性
<!-- 功能表格或列表 -->

<!-- 4. 快速开始 -->
## 🚀 快速开始
<!-- 安装和使用示例 -->

<!-- 5. 详细文档 -->
## 📖 文档
<!-- 完整文档链接 -->

<!-- 6. 贡献指南 -->
## 🤝 贡献
<!-- 贡献流程 -->

<!-- 7. Star History -->
## ⭐ Star History
<!-- 增长图表 -->

<!-- 8. 贡献者 -->
## 👥 贡献者
<!-- 贡献者头像墙 -->
```

## 徽章配置

### 常用徽章列表

| 类型 | 徽章代码 | 说明 |
|------|----------|------|
| 版本 | `![Version](https://img.shields.io/badge/version-1.0.0-blue)` | 项目版本 |
| 许可证 | `![License](https://img.shields.io/badge/license-MIT-green)` | 开源协议 |
| Python | `![Python](https://img.shields.io/badge/python-3.10+-yellow)` | Python 版本 |
| Stars | `![Stars](https://img.shields.io/github/stars/owner/repo?style=social)` | GitHub Stars |
| Forks | `![Forks](https://img.shields.io/github/forks/owner/repo?style=social)` | GitHub Forks |
| Issues | `![Issues](https://img.shields.io/github/issues/owner/repo)` | Issues 数量 |
| Pull Requests | `![PRs](https://img.shields.io/github/pull-requests/owner/repo)` | PR 数量 |
| Last Commit | `![Last Commit](https://img.shields.io/github/last-commit/owner/repo)` | 最后提交 |
| Build Status | `![Build](https://img.shields.io/github/actions/workflow/status/owner/repo/ci.yml)` | 构建状态 |
| Coverage | `![Coverage](https://img.shields.io/codecov/c/github/owner/repo)` | 测试覆盖率 |

### 自定义徽章

```markdown
<!-- 自定义颜色和文本 -->
![Custom](https://img.shields.io/badge/自定义文本-值-颜色)

<!-- 示例 -->
![Made with](https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat&logo=python&logoColor=white)
![Powered by](https://img.shields.io/badge/Powered%20by-OpenAI-412991?style=flat&logo=openai&logoColor=white)
```

## Star History 集成

### 基础用法

```markdown
## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=owner/repo&type=Date)](https://star-history.com/#owner/repo&Date)
```

### 多项目对比

```markdown
## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=project1/project1,project2/project2&type=Date)](https://star-history.com/#project1/project1&Date)
```

### 自定义样式

```markdown
<p align="center">
  <a href="https://star-history.com/#owner/repo&Date">
    <img src="https://api.star-history.com/svg?repos=owner/repo&type=Date&theme=dark" alt="Star History Chart" width="600">
  </a>
</p>
```

## 功能展示表格

### 基础表格

```markdown
<table>
  <tr>
    <td width="50%">
      <h3>功能 1</h3>
      <ul>
        <li>特性 A</li>
        <li>特性 B</li>
      </ul>
    </td>
    <td width="50%">
      <h3>功能 2</h3>
      <ul>
        <li>特性 C</li>
        <li>特性 D</li>
      </ul>
    </td>
  </tr>
</table>
```

### 带图标的表格

```markdown
<table>
  <tr>
    <td width="50%">
      <img src="icon1.png" width="40">
      <h3>功能 1</h3>
      <p>描述文字</p>
    </td>
    <td width="50%">
      <img src="icon2.png" width="40">
      <h3>功能 2</h3>
      <p>描述文字</p>
    </td>
  </tr>
</table>
```

## 项目结构展示

### 基础结构树

```markdown
## 📁 项目结构

```
project/
├── src/
│   ├── module1/
│   └── module2/
├── tests/
├── docs/
├── README.md
└── LICENSE
```
```

### 带注释的结构树

```markdown
## 📁 项目结构

```
project/
├── src/
│   ├── module1/          # 模块 1 说明
│   └── module2/          # 模块 2 说明
├── tests/                # 测试文件
├── docs/                 # 文档
├── README.md             # 项目说明
└── LICENSE               # 开源协议
```
```

## 贡献者展示

### 基础贡献者

```markdown
## 👥 贡献者

<a href="https://github.com/owner/repo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=owner/repo" />
</a>
```

### 贡献者列表

```markdown
## 👥 贡献者

感谢所有贡献者！

<a href="https://github.com/owner/repo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=owner/repo" />
</a>
```

## 主题和样式

### 预设主题

| 主题 | 主色 | 副色 | 适用场景 |
|------|------|------|----------|
| 默认 | #667eea | #764ba2 | 通用项目 |
| 深色 | #1a1a2e | #16213e | 技术项目 |
| 渐变 | #00b4db | #0083b0 | 现代项目 |
| 自然 | #11998e | #38ef7d | 环保/健康项目 |
| 活力 | #fc5c7d | #6a82fb | 创意项目 |

### 自定义颜色

```markdown
<!-- 使用 CSS 变量 -->
<style>
  :root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
  }
</style>
```

## 最佳实践

### ✅ 推荐做法

1. **简洁明了** - 一句话说清项目是什么
2. **视觉层次** - 使用标题、表格、代码块创建层次
3. **徽章选择** - 只展示最重要的徽章
4. **代码示例** - 提供可直接运行的示例
5. **快速开始** - 让用户 3 分钟内跑起来
6. **Star History** - 展示项目增长趋势
7. **贡献指南** - 降低贡献门槛

### ❌ 避免事项

1. **过度装饰** - 避免过多动画和特效
2. **信息过载** - 不要把所有信息都堆在 README
3. **徽章过多** - 5-8 个徽章足够
4. **缺少截图** - GUI 项目必须有截图
5. **无快速开始** - 用户找不到如何使用

## 集成到 Codex

### 作为 Skill 使用

```bash
# 安装 skill
codex skill install readme-magic

# 使用 skill
codex "为我的项目生成 README"
```

### 作为 MCP 工具

```bash
# 启动 MCP 服务器
python -m github_readme_design.mcp_server

# 可用工具
- generate_readme
- preview_readme
- add_badges
- generate_star_history
```

## 示例项目

### 项目 1: Python 库

```markdown
# NumPy

<p align="center">
  <img src="numpy_logo.png" width="200">
</p>

<p align="center">
  <strong>The fundamental package for scientific computing with Python</strong>
</p>

<p align="center">
  <a href="https://numpy.org/doc/">Docs</a> • 
  <a href="https://numpy.org/install/">Install</a> • 
  <a href="https://numpy.org/contribute/">Contribute</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.24.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-BSD-green" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow" alt="Python">
  <img src="https://img.shields.io/github/stars/numpy/numpy?style=social" alt="Stars">
</p>
```

### 项目 2: CLI 工具

```markdown
# GitHub CLI

<p align="center">
  <strong>GitHub official command line tool</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.30.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/github/stars/cli/cli?style=social" alt="Stars">
</p>

## 🚀 Quick Start

```bash
# Install
brew install gh

# Login
gh auth login

# Use
gh repo clone cli/cli
```
```

## 更新日志

### v1.0.0 (2024-01-01)

- 🎉 初始发布
- ✨ 支持 5 种模板
- 🎨 自定义主题颜色
- 📊 Star History 集成
- 🏷️ 徽章系统

### v1.1.0 (2024-02-01)

- ✨ 批量生成功能
- 🎨 新增 3 种模板
- 📊 动态统计卡片
- 🔧 MCP 服务器支持

## 许可证

MIT License

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 支持

- 📧 Email: support@example.com
- 💬 Discord: [加入社区](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/owner/repo/issues)

