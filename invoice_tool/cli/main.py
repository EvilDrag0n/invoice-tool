import argparse

from invoice_tool.application.contracts import ProcessRequest
from invoice_tool.application.errors import InvoiceToolError
from invoice_tool.application.service import process_invoices
from invoice_tool.infrastructure.excel.exporter import export_records_to_excel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read invoice PDFs and export aggregated results to Excel.")
    parser.add_argument("--input", required=True, help="Path to a single PDF file or a directory containing PDF files")
    parser.add_argument("--output", default="./发票汇总.xlsx", help="Path to the output Excel workbook")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output workbook if it already exists")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    request = ProcessRequest(input_path=args.input, output_path=args.output, overwrite=args.overwrite)

    try:
        result = process_invoices(request)
        export_path = export_records_to_excel(result.records, args.output)
    except InvoiceToolError as exc:
        print(f"error: {exc}")
        return 1

    print(f"processed={result.processed_count}")
    print(f"exported={result.exported_count}")
    print(f"skipped_failed={len(result.failed_files)}")
    print(f"skipped_duplicate={result.duplicate_skips}")
    print(f"duplicate_conflicts={result.conflict_skips}")
    print(f"incomplete_exported={result.incomplete_count}")
    if result.failed_files:
        print("failed_files=")
        for failed_file in result.failed_files:
            print(f"- {failed_file}")
    if result.conflicts:
        print("conflicts=")
        for conflict_path, summary in result.conflicts.items():
            print(f"- {conflict_path}: {summary}")
    print(f"output={export_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
