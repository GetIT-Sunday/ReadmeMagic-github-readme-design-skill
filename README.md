<a name="readmemagic"></a>
<p align="center">
  <h1 align="center">✨ ReadmeMagic</h1>
  <p align="center">
    <strong>One spell, beautiful README — Generate professional GitHub READMEs in seconds</strong><br>
    <em>一键生成专业 GitHub README，支持中文 / 英文 / 双语三种模式</em>
  </p>
  <p align="center">
    <a href="#-features">Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-usage">Usage</a> •
    <a href="#-templates">Templates</a> •
    <a href="#-language-support">Language Support</a> •
    <a href="#-examples">Examples</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.3.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/language-EN%20%7C%20ZH%20%7C%20Bilingual-purple?style=flat-square" alt="Language">
  <img src="https://img.shields.io/github/stars/GetIT-Sunday/ReadmeMagic-github-readme-design-skill?style=social" alt="Stars">
</p>

---

## ✨ Features

<table>
  <tr>
    <td width="50%">
      <h3>🌐 Bilingual Support</h3>
      <ul>
        <li>English (<code>--lang en</code>)</li>
        <li>Chinese (<code>--lang zh</code>)</li>
        <li>Bilingual side-by-side (<code>--lang bilingual</code>)</li>
      </ul>
    </td>
    <td width="50%">
      <h3>📝 Template System</h3>
      <ul>
        <li>5 pre-built templates (standard, ai-project, cli-tool, library, personal)</li>
        <li>Each template available in EN / ZH / Bilingual</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🎨 Beautiful Design</h3>
      <ul>
        <li>Professional centered headers</li>
        <li>Custom color themes for badges</li>
        <li>Star History chart integration</li>
        <li>Contributor wall via contrib.rocks</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🔧 Easy to Use</h3>
      <ul>
        <li>Single CLI command generates a complete README</li>
        <li><code>{{PLACEHOLDER}}</code>-based templates, easy to customize</li>
        <li>Batch generation via YAML config</li>
        <li>🖼️ <strong>Banner support</strong>: embed an existing image (<code>--banner</code>) or auto-generate one via GPT Image (<code>--gen-banner</code>)</li>
      </ul>
    </td>
  </tr>
</table>

---

## 📦 Installation

> **Prerequisites**: Python 3.8+

```bash
# From source
git clone https://github.com/GetIT-Sunday/ReadmeMagic-github-readme-design-skill.git
cd ReadmeMagic-github-readme-design-skill
pip install -e .
```

<details>
<summary><strong>📋 Alternative: install via pip</strong></summary>
<br>

```bash
# Via pip (when published)
pip install ReadmeMagic
```

</details>

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 🚀 Usage

**① Generate a basic README**

```bash
# English README (default)
readme-magic generate --project-path ./my-project

# Chinese README
readme-magic generate --project-path ./my-project --lang zh

# Bilingual README (English + Chinese)
readme-magic generate --project-path ./my-project --lang bilingual
```

**② Choose a template**

```bash
readme-magic generate --template ai-project --lang zh
readme-magic generate --template cli-tool --lang bilingual
readme-magic generate --template standard --lang en
```

**③ Customize colors, badges, and banner**

```bash
# With an existing banner image
readme-magic generate \
  --template standard \
  --lang bilingual \
  --primary-color "#667eea" \
  --secondary-color "#764ba2" \
  --badges version,license,python,stars \
  --star-history --repo "owner/repo" \
  --banner assets/banner.png

# Auto-generate banner via GPT Image (dodo AI sandbox)
readme-magic generate \
  --template standard \
  --lang en \
  --repo "owner/repo" \
  --gen-banner
```

<details>
<summary><strong>④ List available templates (optional) — click to expand</strong></summary>
<br>

```bash
readme-magic templates
```

</details>

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 🌐 Language Support

ReadmeMagic supports three language modes, selectable via `--lang`:

| Mode | Flag | Description |
|------|------|-------------|
| English | `--lang en` | All section headings and template prose in English (default) |
| Chinese | `--lang zh` | All section headings and template prose in Chinese (中文) |
| Bilingual | `--lang bilingual` | English heading + Chinese subtitle for each section |

Each of the 5 templates ships with dedicated EN / ZH / Bilingual variants under:

```
templates/
├── en/          # English templates (also used as default)
│   ├── standard.md
│   ├── ai-project.md
│   ├── cli-tool.md
│   ├── library.md
│   └── personal.md
├── zh/          # Chinese templates
│   ├── standard.md
│   ├── ai-project.md
│   ├── cli-tool.md
│   ├── library.md
│   └── personal.md
└── bilingual/   # Bilingual templates
    ├── standard.md
    ├── ai-project.md
    ├── cli-tool.md
    ├── library.md
    └── personal.md
```

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 📝 Templates

<table>
<tr><th>Template</th><th>Best for</th></tr>
<tr><td><code>standard</code></td><td>General open-source projects</td></tr>
<tr><td><code>ai-project</code></td><td>AI / ML / deep learning projects</td></tr>
<tr><td><code>cli-tool</code></td><td>Command-line tools</td></tr>
<tr><td><code>library</code></td><td>Reusable libraries and frameworks</td></tr>
<tr><td><code>personal</code></td><td>Personal portfolio projects</td></tr>
</table>

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 🎨 Color Themes

<table>
<tr><th>Theme</th><th>Primary</th><th>Secondary</th><th>Best for</th></tr>
<tr><td>Default</td><td><code>#667eea</code></td><td><code>#764ba2</code></td><td>General projects</td></tr>
<tr><td>Dark</td><td><code>#1a1a2e</code></td><td><code>#16213e</code></td><td>Technical projects</td></tr>
<tr><td>Ocean</td><td><code>#00b4db</code></td><td><code>#0083b0</code></td><td>Modern projects</td></tr>
<tr><td>Nature</td><td><code>#11998e</code></td><td><code>#38ef7d</code></td><td>Open source tools</td></tr>
<tr><td>Vivid</td><td><code>#fc5c7d</code></td><td><code>#6a82fb</code></td><td>Creative projects</td></tr>
</table>

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 📁 Project Structure

```
ReadmeMagic/
├── readme_magic/
│   ├── __init__.py
│   └── cli.py              # CLI entry point (readme-magic command)
├── templates/
│   ├── en/                 # English templates
│   ├── zh/                 # Chinese templates (中文模板)
│   └── bilingual/          # Bilingual templates (中英双语模板)
├── examples/
│   ├── ai-project.md
│   ├── cli-tool.md
│   └── python-library.md
├── pyproject.toml
├── SKILL.md
└── README.md
```

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 🧪 Development

<details>
<summary><strong>Dev setup, tests, and formatting — click to expand</strong></summary>
<br>

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black readme_magic/
```

</details>

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 🤝 Contributing

Contributions are welcome and greatly appreciated! Every contribution helps make ReadmeMagic better.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details. Don't forget to give the project a ⭐!

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

## 🙏 Acknowledgments

- [shields.io](https://shields.io/) — badge generation
- [star-history.com](https://star-history.com/) — Star History charts
- [contrib.rocks](https://contrib.rocks/) — contributor avatar wall

<div align="right"><a href="#readmemagic">↑ back to top</a></div>

---

<p align="center">
  <sub>If ReadmeMagic saved you time, consider giving it a ⭐ — it helps others discover it too.</sub>
</p>

<p align="center">
  <a href="https://star-history.com/#GetIT-Sunday/ReadmeMagic-github-readme-design-skill&Date">
    <img src="https://api.star-history.com/svg?repos=GetIT-Sunday/ReadmeMagic-github-readme-design-skill&type=Date" alt="Star History Chart" width="600">
  </a>
</p>
