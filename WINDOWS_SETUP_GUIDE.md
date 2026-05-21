# Windows 环境下运行项目的解决方案

## 问题说明

当前系统提示 `npm` 命令无法识别，这通常是因为：
1. Node.js 没有安装
2. Node.js 没有添加到系统 PATH 环境变量

## 解决方案

### 方案 1: 安装 Node.js（推荐）

1. 访问 https://nodejs.org/ 下载并安装 LTS 版本
2. 安装后重新打开 PowerShell 终端
3. 验证安装：
   ```powershell
   node --version
   npm --version
   ```
4. 在项目目录运行：
   ```powershell
   cd "e:\AAA熊猫出行\5.20社区前端"
   npm install
   npm run dev
   ```

### 方案 2: 使用 CDN 版本的简化预览

我将为您创建一个可以直接在浏览器打开的 HTML 预览版本，不需要任何依赖。

---

## 如果 Node.js 已安装但仍无法识别

尝试使用完整路径运行：

```powershell
# 查找 Node.js 安装路径（通常在以下位置之一）
# C:\Program Files\nodejs\npm.cmd
# C:\Users\<您的用户名>\AppData\Roaming\npm

# 使用完整路径运行
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev
```

或者重新启动计算机后再次尝试。
