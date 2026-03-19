import re
from pathlib import Path

from invoice_tool.application.normalizer import collapse_whitespace, normalize_date, normalize_decimal
from invoice_tool.domain.models import InvoiceRecord


FIELD_NAMES = (
    "发票号码",
    "开票日期",
    "购买方名称",
    "购买方税号",
    "销售方名称",
    "销售方税号",
    "金额",
    "税额",
    "价税合计",
)


def extract_invoice_record(text: str, file_path: str | Path) -> InvoiceRecord:
    normalized_text = text.replace("：", ":")
    normalized_text = normalized_text.replace("（", "(").replace("）", ")")
    source_path = Path(file_path)

    extracted_values: dict[str, str] = {}
    missing_fields: list[str] = []

    invoice_number = _optional_match(normalized_text, r"发票号码[:\s]*([0-9]{8,})")
    issue_date_raw = _optional_match(normalized_text, r"开票日期[:\s]*([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)")
    buyer_name, seller_name = _extract_counterparty_names(normalized_text)
    buyer_tax, seller_tax = _extract_counterparty_tax_ids(normalized_text)
    amount_raw, tax_raw = _extract_totals(normalized_text)
    total_raw = _extract_total_amount(normalized_text)

    extracted_values["发票号码"] = collapse_whitespace(invoice_number) if invoice_number else ""
    extracted_values["开票日期"] = _normalize_or_blank(normalize_date, issue_date_raw)
    extracted_values["购买方名称"] = collapse_whitespace(buyer_name) if buyer_name else ""
    extracted_values["购买方税号"] = collapse_whitespace(buyer_tax) if buyer_tax else ""
    extracted_values["销售方名称"] = collapse_whitespace(seller_name) if seller_name else ""
    extracted_values["销售方税号"] = collapse_whitespace(seller_tax) if seller_tax else ""
    extracted_values["金额"] = _normalize_or_blank(normalize_decimal, amount_raw)
    extracted_values["税额"] = _normalize_or_blank(normalize_decimal, tax_raw)
    extracted_values["价税合计"] = _normalize_or_blank(normalize_decimal, total_raw)

    for field_name in FIELD_NAMES:
        if not extracted_values[field_name]:
            missing_fields.append(field_name)

    return InvoiceRecord(
        文件名=source_path.name,
        发票号码=extracted_values["发票号码"],
        开票日期=extracted_values["开票日期"],
        购买方名称=extracted_values["购买方名称"],
        购买方税号=extracted_values["购买方税号"],
        销售方名称=extracted_values["销售方名称"],
        销售方税号=extracted_values["销售方税号"],
        金额=extracted_values["金额"],
        税额=extracted_values["税额"],
        价税合计=extracted_values["价税合计"],
        是否完整=not missing_fields,
        缺失字段=tuple(missing_fields),
    )


def _optional_match(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_counterparty_names(text: str) -> tuple[str, str]:
    line_patterns = (
        r"买\s*名\s*称\s*([^\n]+?)\s*售\s*名\s*称\s*([^\n]+)",
        r"购\s*名称\s*([^\n]+?)\s*销\s*名称\s*([^\n]+)",
        r"购买方名称[:\s]*([^\n]+?)\s*销售方名称[:\s]*([^\n]+)",
    )
    for pattern in line_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            buyer_name = _clean_counterparty_name(match.group(1))
            seller_name = _clean_counterparty_name(match.group(2))
            if buyer_name and seller_name:
                return buyer_name, seller_name
    return "", ""


def _clean_counterparty_name(value: str) -> str:
    cleaned = collapse_whitespace(value)
    cleaned = cleaned.lstrip(":： ")
    return cleaned.strip()


def _extract_counterparty_tax_ids(text: str) -> tuple[str, str]:
    tax_ids = re.findall(r"([0-9A-Z]{10,})", text)
    unique_tax_ids: list[str] = []
    for tax_id in tax_ids:
        if tax_id not in unique_tax_ids:
            unique_tax_ids.append(tax_id)
    if len(unique_tax_ids) >= 3:
        return unique_tax_ids[1], unique_tax_ids[2]
    if len(unique_tax_ids) >= 2:
        return unique_tax_ids[0], unique_tax_ids[1]
    return "", ""


def _extract_totals(text: str) -> tuple[str, str]:
    match = re.search(r"合\s*计\s*¥?(-?[0-9]+(?:\.[0-9]+)?)\s+([*¥]?-?[0-9]+(?:\.[0-9]+)?|\*)", text)
    if not match:
        return "", ""
    amount_raw = match.group(1)
    tax_raw = match.group(2)
    if tax_raw == "*":
        tax_raw = "0"
    return amount_raw, tax_raw.replace("¥", "")


def _extract_total_amount(text: str) -> str:
    patterns = (
        r"价税合计.*?[（(]小写[)）]\s*¥?(-?[0-9]+(?:\.[0-9]+)?)",
        r"票价[:：]?\s*￥?(-?[0-9]+(?:\.[0-9]+)?)",
        r"￥(-?[0-9]+(?:\.[0-9]+)?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1)
    return ""


def _normalize_or_blank(normalizer, value: str) -> str:
    if not value:
        return ""
    try:
        return normalizer(value)
    except ValueError:
        return ""
