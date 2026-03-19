import enum
import queue
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

from invoice_tool.application.contracts import ProcessRequest, ProcessResult
from invoice_tool.application.service import process_invoices
from invoice_tool.infrastructure.excel.exporter import export_records_to_excel


class AppPhase(enum.Enum):
    IDLE = "idle"
    VALIDATING = "validating"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILURE = "failure"


class InputMode(enum.Enum):
    NONE = "none"
    FILE = "file"
    FOLDER = "folder"


@dataclass
class SummaryMetrics:
    processed: int = 0
    exported: int = 0
    incomplete_exported: int = 0
    skipped_failed: int = 0
    skipped_duplicate: int = 0
    duplicate_conflicts: int = 0


@dataclass
class ProcessingDetails:
    failed_files: List[str] = field(default_factory=list)
    conflict_lines: List[str] = field(default_factory=list)


@dataclass
class GuiState:
    input_path: str = ""
    input_mode: InputMode = InputMode.NONE
    output_path: str = ""
    overwrite: bool = False
    
    phase: AppPhase = AppPhase.IDLE
    
    # Progress
    progress_current: int = 0
    progress_total: int = 0
    
    # Results
    summary: SummaryMetrics = field(default_factory=SummaryMetrics)
    details: ProcessingDetails = field(default_factory=ProcessingDetails)
    
    # Global error message
    error_message: str = ""


@dataclass
class ProgressEvent:
    phase: str
    completed: int
    total: int
    message: str


def map_process_result_to_gui_data(result: ProcessResult) -> Tuple[SummaryMetrics, ProcessingDetails]:
    """Maps domain ProcessResult to GUI-friendly summary and details."""
    summary = SummaryMetrics(
        processed=result.processed_count,
        exported=result.exported_count,
        incomplete_exported=result.incomplete_count,
        skipped_failed=len(result.failed_files),
        skipped_duplicate=result.duplicate_skips,
        duplicate_conflicts=result.conflict_skips
    )
    
    conflict_lines = [
        f"{file_path}: {conflict_msg}" 
        for file_path, conflict_msg in result.conflicts.items()
    ]
    
    details = ProcessingDetails(
        failed_files=result.failed_files.copy(),
        conflict_lines=conflict_lines
    )
    
    return summary, details


class Controller:
    def __init__(self, root):
        self.root = root
        self.state = GuiState()
        self.event_queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None

    def set_input(self, path_str: str) -> Tuple[bool, str]:
        """Validates and sets the input path in the state."""
        if not path_str:
            self.state.input_path = ""
            self.state.input_mode = InputMode.NONE
            return False, "未提供路径。"

        path = Path(path_str)
        if not path.exists():
            return False, f"路径不存在：{path_str}"

        if path.is_file():
            if path.suffix.lower() != ".pdf":
                return False, "文件不是 PDF。"
            self.state.input_path = str(path.absolute())
            self.state.input_mode = InputMode.FILE
            return True, "已选择有效 PDF 文件。"
        
        if path.is_dir():
            # In V1 GUI, we allow selecting any directory. 
            # If it has no PDFs, the backend will surface an error during processing.
            self.state.input_path = str(path.absolute())
            self.state.input_mode = InputMode.FOLDER
            pdf_files = list(path.glob("*.pdf"))
            return True, f"已选择文件夹（共 {len(pdf_files)} 个 PDF）。"

        return False, "输入类型无效。"

    def set_output(self, path_str: str) -> Tuple[bool, str]:
        """Sets the output path in the state."""
        if not path_str:
            return False, "未提供路径。"
        self.state.output_path = path_str
        return True, "输出路径已设置。"

    def run_pipeline_sync(self, progress_callback: Optional[Callable[[ProgressEvent], None]] = None) -> ProcessResult:
        """
        GUI-safe backend adapter running the existing processing pipeline.
        Currently blocking (sync) but designed so a background worker thread can just 
        wrap this call.
        """
        def _service_callback(phase: str, completed: int, total: int, message: str) -> None:
            if progress_callback:
                progress_callback(ProgressEvent(phase, completed, total, message))

        req = ProcessRequest(
            input_path=self.state.input_path,
            output_path=self.state.output_path,
            overwrite=self.state.overwrite,
            progress_callback=_service_callback
        )
        result = process_invoices(req)
        export_records_to_excel(result.records, self.state.output_path)
        return result

    def start_processing(self):
        """Starts the processing pipeline in a background thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._worker_thread = threading.Thread(target=self._run_worker, daemon=True)
        self._worker_thread.start()

    def _run_worker(self):
        """Worker thread target."""
        try:
            def _progress_callback(event: ProgressEvent):
                self.event_queue.put(("progress", event))

            result = self.run_pipeline_sync(progress_callback=_progress_callback)
            self.event_queue.put(("result", result))
        except Exception as e:
            # Wrap error in ProgressEvent for explicit phase semantics
            self.event_queue.put(("error", ProgressEvent(
                phase="error", 
                completed=0, 
                total=0, 
                message=str(e)
            )))
