from pathlib import Path

from invoice_tool.application.contracts import ProcessRequest, ProcessResult
from invoice_tool.application.errors import InvoiceToolError, NoSuccessfulInvoicesError
from invoice_tool.application.extractor import extract_invoice_record
from invoice_tool.application.input_resolver import resolve_input
from invoice_tool.infrastructure.pdf.reader import read_pdf_text


def process_invoices(request: ProcessRequest) -> ProcessResult:
    if request.progress_callback:
        request.progress_callback("validating", 0, 0, "Resolving inputs...")
        
    resolved_input = resolve_input(request.input_path, request.output_path, request.overwrite)

    total_files = len(resolved_input.pdf_paths)
    if request.progress_callback:
        request.progress_callback("processing", 0, total_files, f"Found {total_files} files...")

    processed_count = 0
    failed_files: list[str] = []
    duplicate_skips = 0
    conflict_skips = 0
    conflicts: dict[str, str] = {}
    records_by_invoice_number: dict[str, object] = {}

    for pdf_path in resolved_input.pdf_paths:
        processed_count += 1
        if request.progress_callback:
            request.progress_callback("processing", processed_count, total_files, f"Processing {pdf_path.name}...")
        try:
            raw_text = read_pdf_text(pdf_path)
            record = extract_invoice_record(raw_text, pdf_path)
        except (InvoiceToolError, ValueError) as exc:
            failed_files.append(f"{pdf_path}: {exc}")
            continue

        dedup_key = record.发票号码 or f"__missing_invoice__::{pdf_path}"
        existing = records_by_invoice_number.get(dedup_key)
        if existing is None:
            records_by_invoice_number[dedup_key] = record
            continue

        if existing == record:
            duplicate_skips += 1
            continue

        conflict_skips += 1
        conflicts[str(pdf_path)] = _build_conflict_summary(existing, record)

    records = list(records_by_invoice_number.values())
    if not records:
        raise NoSuccessfulInvoicesError("No invoices were successfully extracted")

    if request.progress_callback:
        request.progress_callback("exporting", processed_count, total_files, f"Sorting and exporting {len(records)} records...")

    incomplete_count = sum(1 for item in records if not item.是否完整)
    records.sort(key=lambda item: (not item.是否完整, item.开票日期 == "", item.开票日期, item.发票号码, item.文件名))

    if request.progress_callback:
        request.progress_callback("complete", processed_count, total_files, "Done")

    return ProcessResult(
        processed_count=processed_count,
        exported_count=len(records),
        failed_files=failed_files,
        duplicate_skips=duplicate_skips,
        conflict_skips=conflict_skips,
        incomplete_count=incomplete_count,
        output_path=str(Path(request.output_path)),
        records=records,
        conflicts=conflicts,
    )


def _build_conflict_summary(existing_record, incoming_record) -> str:
    differing_fields: list[str] = []
    for field_name in (
        "文件名",
        "开票日期",
        "购买方名称",
        "购买方税号",
        "销售方名称",
        "销售方税号",
        "金额",
        "税额",
        "价税合计",
    ):
        existing_value = getattr(existing_record, field_name)
        incoming_value = getattr(incoming_record, field_name)
        if existing_value != incoming_value:
            differing_fields.append(f"{field_name}: '{existing_value}' != '{incoming_value}'")
    joined_fields = "; ".join(differing_fields) if differing_fields else "no differing fields captured"
    return f"invoice={incoming_record.发票号码}; {joined_fields}"
