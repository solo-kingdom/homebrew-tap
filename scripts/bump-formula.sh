#!/usr/bin/env bash
# 兼容入口，实际逻辑见 bump-formula.py
set -euo pipefail
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bump-formula.py" "$@"
