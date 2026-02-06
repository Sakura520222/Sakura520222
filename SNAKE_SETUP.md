# 🐍 贪吃蛇动画设置说明

## 📝 设置步骤

### 1. 提交文件到 GitHub

已为你创建了以下文件：
- ✅ `readme.md` - 包含贪吃蛇动画代码
- ✅ `.github/workflows/snake-game.yml` - 自动生成动画的 workflow

### 2. 手动运行 Workflow

1. 将这两个文件提交到你的 GitHub 仓库
2. 进入仓库的 **Actions** 标签页
3. 在左侧找到 **"generate snake animation"** workflow
4. 点击 **"Run workflow"** 按钮
5. 选择 **master** 分支，点击绿色的 **"Run workflow"** 确认

### 3. 等待生成

- Workflow 会自动运行（大约 1-2 分钟）
- 运行成功后，会创建一个名为 **output** 的新分支
- 该分支包含生成的贪吃蛇动画 SVG 文件

### 4. 查看效果

- 回到仓库主页
- 你的 README 现在应该显示贪吃蛇动画了！
- 动画会根据你的 GitHub 主题（深色/浅色）自动切换

## 🔄 自动更新

- 贪吃蛇动画会**每 2 小时**自动更新一次
- 每次向 master 分支推送代码时也会触发更新
- 也可以随时手动触发 workflow 运行

## 🎨 动画效果

- 贪吃蛇会"吃掉"你 GitHub 贡献图中的绿点
- 支持深色和浅色主题自动切换
- 非常有趣且个性化！

## 📚 技术说明

- 使用 [Platane/snk](https://github.com/Platane/snk) 工具生成
- GitHub Actions 自动化工作流
- SVG 格式，加载速度快

---

**享受你的个性化 GitHub 主页吧！** 🎉