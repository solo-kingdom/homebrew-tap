# solo-kingdom Homebrew Tap

**语言 / Language：** 中文 · [English](README.en.md)

[solo-kingdom](https://github.com/solo-kingdom) 团队的官方 Homebrew Tap，用于通过 Homebrew 安装团队开源工具。

## 安装

```bash
# 添加 tap
brew tap solo-kingdom/tap

# 安装单个工具
brew install solo-kingdom/tap/senv
brew install solo-kingdom/tap/llmwiki
brew install solo-kingdom/tap/transit
brew install solo-kingdom/tap/grepom
brew install solo-kingdom/tap/mdserve
```

也可以一步安装（会自动添加 tap）：

```bash
brew install solo-kingdom/tap/senv
```

## 可用 Formula

| Formula | 说明 | 上游仓库 |
|---------|------|----------|
| [senv](Formula/senv.rb) | 安全的环境变量与配置管理 CLI | [solo-kingdom/senv](https://github.com/solo-kingdom/senv) |
| [llmwiki](Formula/llmwiki.rb) | LLM 知识库工作区 CLI | [solo-kingdom/llmwiki](https://github.com/solo-kingdom/llmwiki) |
| [transit](Formula/transit.rb) | 跨区域文件中转服务 | [solo-kingdom/transit](https://github.com/solo-kingdom/transit) |
| [grepom](Formula/grepom.rb) | Git 仓库批量管理 CLI | [sunzhenkai/grepom](https://github.com/sunzhenkai/grepom) |
| [mdserve](Formula/mdserve.rb) | Markdown 实时预览服务 | [sunzhenkai/mdserve](https://github.com/sunzhenkai/mdserve) |

## Brewfile 示例

```ruby
tap "solo-kingdom/tap"
brew "senv"
brew "llmwiki"
brew "transit"
brew "grepom"
brew "mdserve"
```

## 维护

### 更新 Formula 版本

使用 `scripts/bump-formula.py` 从上游 GitHub 仓库拉取最新版本，自动更新 `url`、`sha256`（以及 `llmwiki` 的 commit ldflags），并创建 git commit。

解析顺序：最新 Release → 最新 tag → 默认分支最新 commit。

```bash
# 更新单个 formula 并提交
scripts/bump-formula.py senv

# 指定 tag 发布
scripts/bump-formula.py senv --ref v0.2.0

# 指定 commit 和版本号
scripts/bump-formula.py llmwiki --version 0.2.0 --ref abc1234

# 更新所有 formula
scripts/bump-formula.py --all

# 只更新文件，不提交
scripts/bump-formula.py senv --no-commit

# 预览变更
scripts/bump-formula.py senv --dry-run
```

当 ref 为 commit 且未指定 `--version` 时，会保留 formula 中现有的 `version` 字段。

### 本地测试

```bash
# 语法检查
brew audit --strict Formula/*.rb

# 从源码安装测试
brew install --build-from-source ./Formula/senv.rb
```

### 发布 Bottle

1. 提交 PR 修改 formula
2. CI 通过后，给 PR 打上 `pr-pull` 标签
3. GitHub Actions 会自动构建并上传 bottle

## 文档

- [Homebrew Tap 文档](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
