<p align="center">
  <h1 align="center">🎨 GitHub README Design Skill</h1>
  <p align="center">
    <strong>Create professional, beautiful, high-converting README.md files</strong>
  </p>
  <p align="center">
    <a href="#-features">Features</a> • 
    <a href="#-installation">Installation</a> • 
    <a href="#-usage">Usage</a> • 
    <a href="#-templates">Templates</a> • 
    <a href="#-examples">Examples</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/github/stars/GetIT-Sunday/ReadmeMagic?style=social" alt="Stars">
</p>

---

## ✨ Features

<table>
  <tr>
    <td width="50%">
      <h3>🎨 Beautiful Design</h3>
      <ul>
        <li>Professional header layouts</li>
        <li>Custom color themes</li>
        <li>Responsive design</li>
      </ul>
    </td>
    <td width="50%">
      <h3>📊 Dynamic Elements</h3>
      <ul>
        <li>Star History charts</li>
        <li>Badge systems</li>
        <li>Stats cards</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📝 Template System</h3>
      <ul>
        <li>Multiple pre-built templates</li>
        <li>Customizable placeholders</li>
        <li>Easy to extend</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🔧 Tool Integration</h3>
      <ul>
        <li>shields.io badges</li>
        <li>star-history.com</li>
        <li>contrib.rocks</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/GetIT-Sunday/ReadmeMagic.git
cd ReadmeMagic

# Install dependencies
pip install -e .
```

### Usage

```bash
# Generate README for a project
readme-magic generate --project-path /path/to/project

# Use a specific template
readme-magic generate --template ai-project --project-path /path/to/project

# Preview the result
readme-magic preview --output preview.html
```

---

## 📦 Installation

### Option 1: pip

```bash
pip install ReadmeMagic
```

### Option 2: From Source

```bash
git clone https://github.com/GetIT-Sunday/ReadmeMagic.git
cd ReadmeMagic
pip install -e .
```

### Option 3: Codex Skill

```bash
codex skill install readme-magic
```

---

## 📝 Templates

### Standard Template

适用于大多数开源项目。包含：
- 精美头部设计
- 徽章系统
- 功能特性表格
- 快速开始指南
- Star History 图表

### AI/ML Project Template

针对机器学习项目优化。包含：
- 模型下载表格
- 训练配置说明
- 推理示例
- 性能基准对比

### CLI Tool Template

命令行工具专用。包含：
- 安装方法（多种方式）
- 命令表格
- 配置说明
- Shell 集成

### Library/Framework Template

可复用组件库。包含：
- API 文档链接
- 使用示例
- 贡献指南
- 版本更新日志

### Personal Project Template

个人作品集展示。包含：
- 项目截图展示
- 技术栈徽章
- 在线演示链接
- 联系方式

---

## 🎨 Customization

### Color Themes

```bash
# Use built-in theme
readme-magic generate --theme dark

# Custom colors
readme-magic generate --primary-color "#667eea" --secondary-color "#764ba2"
```

### Badges

```bash
# Add specific badges
readme-magic generate --badges version,license,python,stars

# Custom badge
readme-magic generate --custom-badge "Made with ❤️"
```

### Star History

```bash
# Add Star History
readme-magic generate --star-history --repo "owner/repo"

# Multi-project comparison
readme-magic generate --star-history --repos "project1,project2"
```

---

## 📚 Examples

### Example 1: Python Library

```bash
readme-magic generate \
  --template standard \
  --project-path ./my-library \
  --badges version,license,python,stars,tests
```

### Example 2: AI Project

```bash
readme-magic generate \
  --template ai-project \
  --project-path ./my-ai-project \
  --star-history --repo "myuser/my-ai-project"
```

### Example 3: CLI Tool

```bash
readme-magic generate \
  --template cli-tool \
  --project-path ./my-cli \
  --badges version,license,platform
```

---

## 🔧 Advanced Usage

### Batch Generation

```yaml
# projects.yaml
projects:
  - path: ./project1
    template: standard
    badges: version,license,python
  - path: ./project2
    template: ai-project
    star-history: true
  - path: ./project3
    template: cli-tool
    badges: version,platform
```

```bash
readme-magic batch --config projects.yaml
```

### Custom Templates

```bash
# Create custom template
readme-magic create-template --name my-template --from standard

# Edit template
vim templates/my-template.md

# Use custom template
readme-magic generate --template my-template --project-path ./project
```

### Integration with CI/CD

```yaml
# .github/workflows/update-readme.yml
name: Update README

on:
  push:
    branches: [main]

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install ReadmeMagic
      - run: readme-magic generate --project-path . --star-history
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: update README"
```

---

## 📁 Project Structure

```
ReadmeMagic/
├── SKILL.md                    # Skill documentation
├── README.md                   # This file
├── templates/
│   ├── standard.md             # Standard template
│   ├── ai-project.md           # AI/ML project template
│   ├── cli-tool.md             # CLI tool template
│   ├── library.md              # Library template
│   └── personal.md             # Personal project template
├── src/
│   ├── __init__.py
│   ├── generator.py            # README generator
│   ├── templates.py            # Template loader
│   ├── badges.py               # Badge generator
│   └── star_history.py         # Star History generator
├── examples/
│   ├── python-library/         # Example: Python library
│   ├── ai-project/             # Example: AI project
│   └── cli-tool/               # Example: CLI tool
├── tests/
│   ├── test_generator.py
│   └── test_templates.py
└── setup.py
```

---

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 src/

# Format code
black src/

# Build package
python setup.py sdist bdist_wheel
```

---

## 🤝 Contributing

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/ReadmeMagic.git
cd ReadmeMagic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [shields.io](https://shields.io/) - Badge generation
- [star-history.com](https://star-history.com/) - Star History charts
- [contrib.rocks](https://contrib.rocks/) - Contributor avatars
- [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats) - Stats cards

---

## 📚 Resources

- [Awesome GitHub Profile README](https://github.com/abhisheknaiidu/awesome-github-profile-readme)
- [GitHub README Best Practices](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Markdown Guide](https://www.markdownguide.org/)

---

<p align="center">
  <strong>⭐ If this project helps you, please give it a star!</strong>
</p>

<p align="center">
  <a href="https://star-history.com/#GetIT-Sunday/ReadmeMagic&Date">
    <img src="https://api.star-history.com/svg?repos=GetIT-Sunday/ReadmeMagic&type=Date" alt="Star History Chart" width="600">
  </a>
</p>

