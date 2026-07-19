<p align="center">
  <h1 align="center">{{PROJECT_NAME}}</h1>
  <p align="center">
    <strong>{{ONE_LINER}}</strong>
  </p>
  <p align="center">
    <a href="#-features">Features</a> • 
    <a href="#-installation">Installation</a> • 
    <a href="#-usage">Usage</a> • 
    <a href="#-commands">Commands</a> • 
    <a href="#-configuration">Configuration</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-{{VERSION}}-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-{{LICENSE}}-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/{{LANGUAGE}}-{{LANG_VERSION}}-yellow?style=flat-square" alt="{{LANGUAGE}}">
  <img src="https://img.shields.io/github/stars/{{OWNER}}/{{REPO}}?style=social" alt="Stars">
</p>

---

## ✨ Features

{{FEATURES_TABLE}}

---

## 🚀 Quick Start

### Installation

```bash
{{INSTALL_COMMAND}}
```

### One-liner

```bash
{{ONE_LINER_COMMAND}}
```

---

## 📦 Installation

### Option 1: Package Manager

```bash
# macOS
brew install {{PACKAGE_NAME}}

# Ubuntu/Debian
sudo apt install {{PACKAGE_NAME}}

# Windows
choco install {{PACKAGE_NAME}}
```

### Option 2: Binary

```bash
# Download binary
curl -sL {{DOWNLOAD_URL}} | tar xz
sudo mv {{BINARY_NAME}} /usr/local/bin/
```

### Option 3: From Source

```bash
git clone https://github.com/{{OWNER}}/{{REPO}}.git
cd {{REPO}}
make install
```

---

## 🛠️ Commands

| Command | Description | Example |
|---------|-------------|---------|
{{COMMANDS_TABLE}}

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `-h, --help` | Show help | - |
| `-v, --version` | Show version | - |
| `-V, --verbose` | Verbose output | `false` |
| `-q, --quiet` | Quiet mode | `false` |
| `--config <path>` | Config file | `~/.config/{{CONFIG_FILE}}` |

---

## 📖 Usage

### Basic Usage

```bash
# {{USE_CASE_1}}
{{EXAMPLE_COMMAND_1}}

# {{USE_CASE_2}}
{{EXAMPLE_COMMAND_2}}
```

### Advanced Usage

```bash
# {{ADVANCED_USE_CASE}}
{{ADVANCED_COMMAND}}
```

### Examples

```bash
# Example 1: {{EXAMPLE_1_DESC}}
{{EXAMPLE_1_COMMAND}}

# Example 2: {{EXAMPLE_2_DESC}}
{{EXAMPLE_2_COMMAND}}

# Example 3: {{EXAMPLE_3_DESC}}
{{EXAMPLE_3_COMMAND}}
```

---

## ⚙️ Configuration

### Config File

```yaml
# ~/.config/{{CONFIG_FILE}}
{{CONFIG_YAML}}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `{{ENV_VAR_1}}` | {{ENV_DESC_1}} | {{ENV_DEFAULT_1}} |
| `{{ENV_VAR_2}}` | {{ENV_DESC_2}} | {{ENV_DEFAULT_2}} |

### Command Line Options

```bash
# Override config with CLI options
{{CLI_OVERRIDE_COMMAND}}
```

---

## 🔌 Integrations

### Shell Integration

```bash
# Bash
echo 'source <({{CLI}} completion bash)' >> ~/.bashrc

# Zsh
echo 'source <({{CLI}} completion zsh)' >> ~/.zshrc

# Fish
{{CLI}} completion fish > ~/.config/fish/completions/{{CLI}}.fish
```

### Editor Integration

#### VS Code

```json
{
  "terminal.integrated.env.linux": {
    "PATH": "${env:PATH}:{{INSTALL_PATH}}"
  }
}
```

#### Vim/Neovim

```lua
-- init.lua
vim.api.nvim_create_user_command('{{COMMAND_NAME}}', function()
  vim.fn.system('{{CLI}} ' .. vim.fn.expand('<args>'))
end, { nargs = '*' })
```

---

## 📁 Project Structure

```
{{PROJECT_STRUCTURE}}
```

---

## 🧪 Development

```bash
# Build
make build

# Test
make test

# Lint
make lint

# Release
make release
```

---

## 🤝 Contributing

{{CONTRIBUTING_GUIDE}}

---

## 📄 License

{{LICENSE_INFO}}

---

## 🙏 Acknowledgments

{{ACKNOWLEDGMENTS}}

---

<p align="center">
  <strong>⭐ If this project helps you, please give it a star!</strong>
</p>

<p align="center">
  <a href="https://star-history.com/#{{OWNER}}/{{REPO}}&Date">
    <img src="https://api.star-history.com/svg?repos={{OWNER}}/{{REPO}}&type=Date" alt="Star History Chart" width="600">
  </a>
</p>
