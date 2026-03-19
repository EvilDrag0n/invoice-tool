# Invoice Tool

[简体中文](./README.zh-CN.md)

Extract structured data from text-based PDF invoices and export aggregated results to Excel. The project provides both a command-line interface for batch processing and a drag-and-drop desktop GUI for everyday use.

## Features

- Extract invoice fields from text-based PDF files
- Export normalized results to `.xlsx` with `openpyxl`
- Batch-process a single PDF or an entire folder
- Use the CLI for automation workflows
- Use the Tkinter GUI with drag-and-drop support for manual operation
- Package the GUI as a Windows executable with PyInstaller

## Requirements

- Python 3.8+
- A text-based PDF invoice source

## Installation

```bash
pip install -r requirements.txt
```

Current runtime dependencies:

- `pdfplumber`
- `openpyxl`
- `tkinterdnd2`

## Usage

This project provides both CLI and GUI entrypoints.

### CLI

Run the command-line tool:

```bash
python -m invoice_tool.cli --input <input_path> --output <output_path> [--overwrite]
```

Example:

```bash
python -m invoice_tool.cli --input ./samples --output ./out/invoices.xlsx --overwrite
```

Parameters:

- `--input`: Path to a single PDF file or a directory containing PDF files
- `--output`: Path to the output Excel workbook
- `--overwrite`: Overwrite the output file if it already exists

### GUI

Launch the desktop application:

```bash
python -m invoice_tool.gui
```

GUI highlights:

- Drag and drop one PDF file or one folder at a time
- Browse for input and output paths from the interface
- Track progress and processing status in real time
- Review failed files and duplicate conflicts inside the app

## Build a Windows EXE

This repository includes a PyInstaller-based Windows packaging setup.

Run:

```bat
build_exe.bat
```

After a successful build, the GUI executable is generated at:

```text
dist\InvoiceTool\InvoiceTool.exe
```

Notes:

- The build is based on the GUI entrypoint only
- `InvoiceTool.spec` explicitly collects `tkinterdnd2` resources
- The build script recreates `.venv-build` to keep packaging isolated
- Distribute the full `dist\InvoiceTool\` folder, not only the `.exe`

## Project Structure

```text
invoice_tool/
├─ application/      # Application orchestration
├─ cli/              # Command-line entrypoint
├─ domain/           # Domain models
├─ gui/              # Tkinter desktop interface
└─ infrastructure/   # PDF and Excel adapters
```

## Limitations

- The extractor targets text-based PDFs rather than scanned image-only documents
- The current GUI accepts one dropped item at a time
- The project is optimized around Chinese invoice export fields

## License

Choose an open-source license before publishing to GitHub, for example MIT or Apache-2.0.
