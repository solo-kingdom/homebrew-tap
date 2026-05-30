# solo-kingdom Homebrew Tap

[solo-kingdom](https://github.com/solo-kingdom) 团队的官方 Homebrew Tap，用于通过 Homebrew 安装团队开源工具。

## 安装

```bash
# 添加 tap
brew tap solo-kingdom/tap

# 安装单个工具
brew install solo-kingdom/tap/senv
brew install solo-kingdom/tap/llmwiki
brew install solo-kingdom/tap/transit
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

## Brewfile 示例

```ruby
tap "solo-kingdom/tap"
brew "senv"
brew "llmwiki"
brew "transit"
```

## 维护

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
