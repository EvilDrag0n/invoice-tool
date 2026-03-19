from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from invoice_tool.domain.models import InvoiceRecord


@dataclass(frozen=True)
class ProcessRequest:
    """
    Request object for processing invoices.
    """
    input_path: str
    output_path: str
    overwrite: bool = False
    progress_callback: Optional[Callable[[str, int, int, str], None]] = None

@dataclass(frozen=True)
class ProcessResult:
    """
    Result object representing the outcome of a processing run.
    Contains counters for successes and different failure types.
    """
    processed_count: int = 0
    exported_count: int = 0
    failed_files: List[str] = field(default_factory=list)
    duplicate_skips: int = 0
    conflict_skips: int = 0
    incomplete_count: int = 0
    output_path: Optional[str] = None
    records: List[InvoiceRecord] = field(default_factory=list)

    conflicts: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedInput:
    mode: str
    input_path: Path
    output_path: Path
    pdf_paths: tuple[Path, ...]
