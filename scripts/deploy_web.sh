#!/bin/bash
# 璧山好房 · 一键部署到 GitHub Pages
# 用法：bash scripts/deploy_web.sh "更新说明"

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MESSAGE="${1:-更新网站内容}"

echo "🚀 璧山好房 · 部署脚本"
echo "=========================="
echo ""

cd "$REPO_DIR"

# 检查 git 状态
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ 当前目录不是 git 仓库"
  echo "   请先运行：git init && git remote add origin <你的仓库地址>"
  exit 1
fi

# 添加变更
echo "📦 添加文件变更…"
git add web/ shared/ scripts/

# 提交
echo "💬 提交：$MESSAGE"
git commit -m "$MESSAGE" || echo "   无变更需要提交"

# 推送
echo "📤 推送到 GitHub…"
git push origin main

echo ""
echo "✅ 部署完成！等待 30 秒后网站自动更新"
echo "   网站地址：https://你的用户名.github.io/仓库名/"
