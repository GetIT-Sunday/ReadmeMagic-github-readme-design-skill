<a name="readmemagic"></a>
<p align="center">
  <img src="assets/banner.png" alt="ReadmeMagic banner" width="100%">
</p>

<p align="center">
  <h1 align="center">✨ ReadmeMagic</h1>
  <p align="center">
    <strong>一键生成专业 GitHub README，秒级完成</strong><br>
    <em>One spell, beautiful README — Generate professional GitHub READMEs in seconds</em>
  </p>
  <p align="center">
    <a href="#-功能特性">功能特性</a> •
    <a href="#-安装">安装</a> •
    <a href="#-使用方法">使用方法</a> •
    <a href="#-模板">模板</a> •
    <a href="#-语言支持">语言支持</a> •
    <a href="#-示例">示例</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.3.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/language-EN%20%7C%20ZH%20%7C%20Bilingual-purple?style=flat-square" alt="Language">
  <img src="https://img.shields.io/github/stars/GetIT-Sunday/ReadmeMagic-github-readme-design-skill?style=social" alt="Stars">
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>中文</strong>
</p>

---

## ✨ 功能特性

<table>
  <tr>
    <td width="50%">
      <h3>🌐 多语言支持</h3>
      <ul>
        <li>英文（<code>--lang en</code>）</li>
        <li>中文（<code>--lang zh</code>）</li>
        <li>中英双语（<code>--lang bilingual</code>）</li>
      </ul>
    </td>
    <td width="50%">
      <h3>📝 模板系统</h3>
      <ul>
        <li>5 种内置模板（standard、ai-project、cli-tool、library、personal）</li>
        <li>每个模板均提供英文 / 中文 / 双语三个变体</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🎨 美观设计</h3>
      <ul>
        <li>专业居中标题布局</li>
        <li>自定义徽章颜色主题</li>
        <li>Star History 增长图表集成</li>
        <li>contrib.rocks 贡献者头像墙</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🔧 简单易用</h3>
      <ul>
        <li>单条命令生成完整 README</li>
        <li><code>{{PLACEHOLDER}}</code> 占位符模板，轻松自定义</li>
        <li>支持 YAML 配置批量生成</li>
        <li>🖼️ <strong>Banner 支持</strong>：嵌入已有图片（<code>--banner</code>）或通过 GPT Image 自动生成（<code>--gen-banner</code>）</li>
      </ul>
    </td>
  </tr>
</table>

---

## 📦 安装

> **前置条件**：Python 3.8+

```bash
# 从源码安装
git clone https://github.com/GetIT-Sunday/ReadmeMagic-github-readme-design-skill.git
cd ReadmeMagic-github-readme-design-skill
pip install -e .
```

<details>
<summary><strong>📋 备选：通过 pip 安装</strong></summary>
<br>

```bash
# 通过 pip 安装（发布后可用）
pip install ReadmeMagic
```

</details>

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 🚀 使用方法

**① 生成基础 README**

```bash
# 英文 README（默认）
readme-magic generate --project-path ./my-project

# 中文 README
readme-magic generate --project-path ./my-project --lang zh

# 中英双语 README
readme-magic generate --project-path ./my-project --lang bilingual
```

**② 选择模板**

```bash
readme-magic generate --template ai-project --lang zh
readme-magic generate --template cli-tool --lang bilingual
readme-magic generate --template standard --lang en
```

**③ 自定义颜色、徽章与 Banner**

```bash
# 使用已有 Banner 图片
readme-magic generate \
  --template standard \
  --lang bilingual \
  --primary-color "#667eea" \
  --secondary-color "#764ba2" \
  --badges version,license,python,stars \
  --star-history --repo "owner/repo" \
  --banner assets/banner.png

# 通过 GPT Image 自动生成 Banner（dodo AI 沙箱环境）
readme-magic generate \
  --template standard \
  --lang zh \
  --repo "owner/repo" \
  --gen-banner
```

<details>
<summary><strong>④ 查看可用模板（可选）— 点击展开</strong></summary>
<br>

```bash
readme-magic templates
```

</details>

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 🌐 语言支持

ReadmeMagic 支持三种语言模式，通过 `--lang` 参数选择：

| 模式 | 参数 | 说明 |
|------|------|------|
| 英文 | `--lang en` | 所有章节标题和模板内容均为英文（默认） |
| 中文 | `--lang zh` | 所有章节标题和模板内容均为中文 |
| 双语 | `--lang bilingual` | 每个章节英文标题下附中文副标题 |

5 种模板均提供 EN / ZH / Bilingual 三个专属版本，目录结构如下：

```
templates/
├── en/          # 英文模板（同时作为默认模板）
│   ├── standard.md
│   ├── ai-project.md
│   ├── cli-tool.md
│   ├── library.md
│   └── personal.md
├── zh/          # 中文模板
│   ├── standard.md
│   ├── ai-project.md
│   ├── cli-tool.md
│   ├── library.md
│   └── personal.md
└── bilingual/   # 双语模板
    ├── standard.md
    ├── ai-project.md
    ├── cli-tool.md
    ├── library.md
    └── personal.md
```

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 📝 模板

<table>
<tr><th>模板名称</th><th>适用场景</th></tr>
<tr><td><code>standard</code></td><td>通用开源项目</td></tr>
<tr><td><code>ai-project</code></td><td>AI / ML / 深度学习项目</td></tr>
<tr><td><code>cli-tool</code></td><td>命令行工具</td></tr>
<tr><td><code>library</code></td><td>可复用库与框架</td></tr>
<tr><td><code>personal</code></td><td>个人作品集项目</td></tr>
</table>

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 🎨 颜色主题

<table>
<tr><th>主题</th><th>主色</th><th>辅色</th><th>适用场景</th></tr>
<tr><td>默认</td><td><code>#667eea</code></td><td><code>#764ba2</code></td><td>通用项目</td></tr>
<tr><td>深色</td><td><code>#1a1a2e</code></td><td><code>#16213e</code></td><td>技术类项目</td></tr>
<tr><td>海洋</td><td><code>#00b4db</code></td><td><code>#0083b0</code></td><td>现代风格项目</td></tr>
<tr><td>自然</td><td><code>#11998e</code></td><td><code>#38ef7d</code></td><td>开源工具</td></tr>
<tr><td>鲜明</td><td><code>#fc5c7d</code></td><td><code>#6a82fb</code></td><td>创意类项目</td></tr>
</table>

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 📁 项目结构

```
ReadmeMagic/
├── readme_magic/
│   ├── __init__.py
│   └── cli.py              # CLI 入口（readme-magic 命令）
├── templates/
│   ├── en/                 # 英文模板
│   ├── zh/                 # 中文模板
│   └── bilingual/          # 双语模板
├── examples/
│   ├── ai-project.md
│   ├── cli-tool.md
│   └── python-library.md
├── pyproject.toml
├── SKILL.md
└── README.md
```

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 🧪 开发

<details>
<summary><strong>开发环境搭建、测试与格式化 — 点击展开</strong></summary>
<br>

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black readme_magic/
```

</details>

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 🤝 贡献指南

欢迎所有形式的贡献，每一份参与都让 ReadmeMagic 变得更好！

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: add amazing feature'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 发起 Pull Request

详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。别忘了给项目点个 ⭐！

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 📄 许可证

本项目基于 **MIT 许可证** 分发。详情见 [LICENSE](LICENSE)。

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

## 🙏 致谢

- [shields.io](https://shields.io/) — 徽章生成
- [star-history.com](https://star-history.com/) — Star 增长图表
- [contrib.rocks](https://contrib.rocks/) — 贡献者头像墙

<div align="right"><a href="#readmemagic">↑ 返回顶部</a></div>

---

<p align="center">
  <sub>如果 ReadmeMagic 帮到了你，请给一个 ⭐ — 让更多人发现它！</sub>
</p>

<p align="center">
  <a href="https://star-history.com/#GetIT-Sunday/ReadmeMagic-github-readme-design-skill&Date">
    <img src="https://api.star-history.com/svg?repos=GetIT-Sunday/ReadmeMagic-github-readme-design-skill&type=Date" alt="Star History Chart" width="600">
  </a>
</p>
