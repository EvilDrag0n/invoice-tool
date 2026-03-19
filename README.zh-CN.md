# 发票提取工具

[English](./README.md)

从可读取文本的 PDF 发票中提取结构化字段，并汇总导出为 Excel。项目同时提供适合批量处理的命令行工具，以及支持拖放的桌面图形界面，方便日常使用。

## 功能特性

- 从文本型 PDF 发票中提取关键字段
- 使用 `openpyxl` 导出标准化的 `.xlsx` 文件
- 支持单个 PDF 或整个文件夹的批量处理
- 支持命令行方式接入自动化流程
- 提供基于 Tkinter 的拖放式桌面 GUI
- 支持通过 PyInstaller 打包为 Windows 可执行程序

## 环境要求

- Python 3.8+
- 输入文件需要是可提取文本的 PDF 发票

## 安装

```bash
pip install -r requirements.txt
```

当前运行时依赖：

- `pdfplumber`
- `openpyxl`
- `tkinterdnd2`

## 使用方式

本项目同时提供 CLI 和 GUI 两种入口。

### 命令行 CLI

运行方式：

```bash
python -m invoice_tool.cli --input <input_path> --output <output_path> [--overwrite]
```

示例：

```bash
python -m invoice_tool.cli --input ./samples --output ./out/invoices.xlsx --overwrite
```

参数说明：

- `--input`：单个 PDF 文件路径，或包含 PDF 的目录路径
- `--output`：输出 Excel 工作簿路径
- `--overwrite`：若输出文件已存在，允许覆盖

### 图形界面 GUI

启动方式：

```bash
python -m invoice_tool.gui
```

界面特性：

- 支持一次拖放一个 PDF 文件或一个文件夹
- 可在界面中直接选择输入与输出路径
- 实时显示处理进度与当前状态
- 可在界面内查看失败文件和重复冲突详情

#### GUI 界面预览

初始化界面：

![发票提取工具初始化界面](./img/invoice-tool-start.png)

处理中界面：

![发票提取工具处理中界面](./img/invoice-tool-progresing.png)

处理完成界面：

![发票提取工具处理完成界面](./img/invoice-tool-finish.png)

#### 导出结果预览

导出的 Excel 表格示意：

![导出 Excel 表格预览](./img/invoice-tool-export-excel.png)

## 构建 Windows EXE

仓库中已包含基于 PyInstaller 的 Windows 打包配置。

执行：

```bat
build_exe.bat
```

构建成功后，可执行文件位于：

```text
dist\InvoiceTool\InvoiceTool.exe
```

如果需要构建面向 Windows 7 / 8 / 8.1 的兼容版，请执行：

```bat
build_exe_legacy_win7_8.bat
```

兼容版输出目录为：

```text
dist-win7-8\InvoiceTool\InvoiceTool.exe
```

说明：

- 当前打包入口为 GUI
- `InvoiceTool.spec` 已显式收集 `tkinterdnd2` 相关资源
- 构建脚本会重建 `.venv-build`，避免打包环境污染
- 分发时应携带整个 `dist\InvoiceTool\` 目录，而不只是单个 `.exe`

### Windows 兼容性说明

打包产物使用 `build_exe.bat` 或 `build_exe_legacy_win7_8.bat` 所调用的本地 Python 解释器构建。

- **当前现代版打包目标**：Windows 10 / Windows 11
- **现代版大概率不支持**：Windows 7 / Windows 8 / Windows 8.1
- 如果接收方启动时看到 `api-ms-win-core-path-l1-1-0.dll` 缺失之类的报错，通常表示目标机器系统版本过旧，或缺少当前 Python 运行时所需的现代 Windows 运行组件

对于接收方机器，建议优先检查以下项目：

1. 使用 Windows 10 或 Windows 11，并安装较新的系统更新。
2. 安装 **Microsoft Visual C++ Redistributable 2015-2022（x64）**。
3. 从解压后的目录中启动 `dist\InvoiceTool\InvoiceTool.exe`。

### 如需兼容旧版 Windows

如果必须支持 Windows 7 / 8 / 8.1，请不要使用 Python 3.14 构建兼容包。

- 应使用 **Python 3.8.x** 作为兼容版打包解释器。
- 最理想的方式是在你希望支持的最旧 Windows 系统，或对应虚拟机中完成最终打包与验证。
- 运行 `build_exe_legacy_win7_8.bat` 会使用 `py -3.8` 构建旧系统兼容版。
- 对外分发时应使用 `dist-win7-8\InvoiceTool\` 整个目录。
- 兼容版会使用 `requirements-legacy-win7-8.txt`，将核心二进制依赖控制在对 Windows 7 / 8 更友好的版本范围内。

## 项目结构

```text
invoice_tool/
├─ application/      # 应用层编排逻辑
├─ cli/              # 命令行入口
├─ domain/           # 领域模型
├─ gui/              # Tkinter 图形界面
└─ infrastructure/   # PDF 与 Excel 适配层
```

## 当前限制

- 目前更适合处理可直接提取文本的 PDF，而不是纯扫描图片型 PDF
- GUI 一次只支持拖放一个输入项
- 当前字段设计主要围绕中文发票汇总场景

## License

正式发布到 GitHub 前，建议补充开源许可证，例如 MIT 或 Apache-2.0。
