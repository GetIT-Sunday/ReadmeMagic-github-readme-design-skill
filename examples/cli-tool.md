<p align="center">
  <h1 align="center">🐙 GitHub CLI</h1>
  <p align="center">
    <strong>Your command line interface to GitHub</strong>
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
  <img src="https://img.shields.io/badge/version-2.40.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/go-1.21+-cyan?style=flat-square" alt="Go">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/github/stars/cli/cli?style=social" alt="Stars">
</p>

---

## ✨ Features

<table>
  <tr>
    <td width="50%">
      <h3>🔧 Git Integration</h3>
      <ul>
        <li>Clone repositories</li>
        <li>Create pull requests</li>
        <li>Manage issues</li>
      </ul>
    </td>
    <td width="50%">
      <h3>📝 PR Management</h3>
      <ul>
        <li>Create PRs</li>
        <li>Review PRs</li>
        <li>Merge PRs</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🐛 Issue Tracking</h3>
      <ul>
        <li>Create issues</li>
        <li>Assign issues</li>
        <li>Label issues</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🚀 Actions</h3>
      <ul>
        <li>View workflow runs</li>
        <li>Trigger workflows</li>
        <li>Download artifacts</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
choco install gh

# From script
curl -sL https://raw.githubusercontent.com/cli/cli/trunk/install.sh | bash
```

### Setup

```bash
# Login to GitHub
gh auth login

# Clone a repository
gh repo clone cli/cli

# Create a pull request
gh pr create --title "My PR" --body "Description"
```

---

## 📦 Installation

### Package Managers

| Platform | Command |
|----------|---------|
| macOS | `brew install gh` |
| Ubuntu/Debian | `sudo apt install gh` |
| Fedora | `sudo dnf install gh` |
| Windows | `choco install gh` |
| Arch | `sudo pacman -S github-cli` |

### Binary

```bash
# Download binary
GH_VERSION="2.40.0"
curl -sL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" | tar xz
sudo mv gh_${GH_VERSION}_linux_amd64/bin/gh /usr/local/bin/
```

### From Source

```bash
# Requires Go 1.21+
git clone https://github.com/cli/cli.git
cd cli
make install
```

---

## 🛠️ Commands

| Command | Description | Example |
|---------|-------------|---------|
| `gh auth` | Login/logout | `gh auth login` |
| `gh repo` | Repository operations | `gh repo create` |
| `gh pr` | Pull request operations | `gh pr create` |
| `gh issue` | Issue operations | `gh issue list` |
| `gh run` | Workflow run operations | `gh run list` |
| `gh gist` | Gist operations | `gh gist create` |
| `gh api` | GitHub API calls | `gh api repos/{owner}/{repo}` |
| `gh alias` | Shell aliases | `gh alias set prc 'pr create'` |

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `-h, --help` | Show help | - |
| `-R, --repo` | Specify repository | Current repo |
| `--as` | As user or organization | User |
| `--hostname` | GitHub hostname | github.com |

---

## 📖 Usage

### Repository Operations

```bash
# Clone a repository
gh repo clone cli/cli

# Create a new repository
gh repo create my-project --public

# View repository
gh repo view cli/cli

# Fork a repository
gh repo fork cli/cli
```

### Pull Request Operations

```bash
# Create a pull request
gh pr create --title "Add feature" --body "Description"

# List pull requests
gh pr list

# View a pull request
gh pr view 123

# Checkout a pull request
gh pr checkout 123

# Merge a pull request
gh pr merge 123
```

### Issue Operations

```bash
# Create an issue
gh issue create --title "Bug report" --body "Description"

# List issues
gh issue list

# View an issue
gh issue view 123

# Close an issue
gh issue close 123

# Reopen an issue
gh issue reopen 123
```

### Workflow Operations

```bash
# List workflow runs
gh run list

# View a workflow run
gh run view 123

# Trigger a workflow
gh workflow run deploy.yml

# Download artifacts
gh run download 123
```

---

## ⚙️ Configuration

### Config File

```yaml
# ~/.config/gh/config.yml
version: "1"
hosts:
  github.com:
    oauth_token: "your_token"
    user: "your_username"
editor: "code"
git_protocol: "ssh"
prompt: "enabled"
aliases:
  prc: "pr create"
  prs: "pr status"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GH_TOKEN` | GitHub token | - |
| `GH_HOST` | GitHub host | github.com |
| `GH_REPO` | Default repository | - |
| `GH_EDITOR` | Default editor | - |

### Shell Integration

```bash
# Bash
echo 'source <(gh completion bash)' >> ~/.bashrc

# Zsh
echo 'source <(gh completion zsh)' >> ~/.zshrc

# Fish
gh completion fish > ~/.config/fish/completions/gh.fish
```

---

## 🔌 Integrations

### VS Code

```json
{
  "terminal.integrated.env.linux": {
    "PATH": "${env:PATH}:/usr/local/bin"
  }
}
```

### JetBrains IDEs

Install the "GitHub Actions" plugin from the marketplace.

### tmux

```bash
# Add to tmux.conf
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-yank'
```

---

## 📁 Project Structure

```
cli/
├── cmd/
│   ├── root.go
│   ├── pr/
│   ├── issue/
│   ├── repo/
│   └── api/
├── pkg/
│   ├── ghrepo/
│   ├── ghpr/
│   └── ghissue/
├── api/
│   └── client.go
├── docs/
├── scripts/
├── main.go
└── go.mod
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

# Format
make fmt

# Release
make release
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Good First Issues

- [ ] Add new command
- [ ] Improve documentation
- [ ] Add tests
- [ ] Fix bugs

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- GitHub for the API
- The open source community

---

<p align="center">
  <strong>⭐ If GitHub CLI helps you, please give it a star!</strong>
</p>

<p align="center">
  <a href="https://star-history.com/#cli/cli&Date">
    <img src="https://api.star-history.com/svg?repos=cli/cli&type=Date" alt="Star History Chart" width="600">
  </a>
</p>
