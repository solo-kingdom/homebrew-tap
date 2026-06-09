# solo-kingdom Homebrew Tap

**Language / 语言：** [中文](README.md) · English

Official Homebrew Tap for the [solo-kingdom](https://github.com/solo-kingdom) team. Install open-source tools from the team via Homebrew.

## Installation

```bash
# Add the tap
brew tap solo-kingdom/tap

# Install individual tools
brew install solo-kingdom/tap/senv
brew install solo-kingdom/tap/llmwiki
brew install solo-kingdom/tap/transit
brew install solo-kingdom/tap/grepom
brew install solo-kingdom/tap/mdserve
```

You can also install in one step (the tap is added automatically):

```bash
brew install solo-kingdom/tap/senv
```

## Available Formulae

| Formula | Description | Upstream |
|---------|-------------|----------|
| [senv](Formula/senv.rb) | Secure environment variable and config management CLI | [solo-kingdom/senv](https://github.com/solo-kingdom/senv) |
| [llmwiki](Formula/llmwiki.rb) | LLM knowledge base workspace CLI | [solo-kingdom/llmwiki](https://github.com/solo-kingdom/llmwiki) |
| [transit](Formula/transit.rb) | Cross-region file relay service | [solo-kingdom/transit](https://github.com/solo-kingdom/transit) |
| [grepom](Formula/grepom.rb) | Git repository batch management CLI | [sunzhenkai/grepom](https://github.com/sunzhenkai/grepom) |
| [mdserve](Formula/mdserve.rb) | Markdown live preview server | [sunzhenkai/mdserve](https://github.com/sunzhenkai/mdserve) |

## Brewfile Example

```ruby
tap "solo-kingdom/tap"
brew "senv"
brew "llmwiki"
brew "transit"
brew "grepom"
brew "mdserve"
```

## Maintenance

### Updating Formula Versions

Use `scripts/bump-formula.py` to pull the latest upstream release from GitHub, update `url` and `sha256` (and `llmwiki` commit ldflags), and create a git commit.

Resolution order: latest release → latest tag → default branch HEAD.

```bash
# Update one formula and commit
scripts/bump-formula.py senv

# Pin a release tag
scripts/bump-formula.py senv --ref v0.2.0

# Pin a commit and version
scripts/bump-formula.py llmwiki --version 0.2.0 --ref abc1234

# Update all formulae
scripts/bump-formula.py --all

# Update files only, no commit
scripts/bump-formula.py senv --no-commit

# Preview changes
scripts/bump-formula.py senv --dry-run
```

If the ref is a commit and `--version` is omitted, the existing `version` field in the formula is kept.

### Local Testing

```bash
# Syntax audit
brew audit --strict Formula/*.rb

# Install from source for testing
brew install --build-from-source ./Formula/senv.rb
```

### Publishing Bottles

1. Open a PR with formula changes
2. After CI passes, add the `pr-pull` label to the PR
3. GitHub Actions will build and upload bottles automatically

## Documentation

- [Homebrew Tap Documentation](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
