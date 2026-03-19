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

说明：

- 当前打包入口为 GUI
- `InvoiceTool.spec` 已显式收集 `tkinterdnd2` 相关资源
- 构建脚本会重建 `.venv-build`，避免打包环境污染
- 分发时应携带整个 `dist\InvoiceTool\` 目录，而不只是单个 `.exe`

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
