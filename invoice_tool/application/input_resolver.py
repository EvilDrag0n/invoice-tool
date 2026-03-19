from pathlib import Path
from typing import Union

from invoice_tool.application.contracts import ResolvedInput
from invoice_tool.application.errors import (
    EmptyInputError,
    InvalidInputTypeError,
    MissingInputPathError,
    OverwriteRefusalError,
)


def resolve_input(input_path: Union[str, Path], output_path: Union[str, Path], overwrite: bool = False) -> ResolvedInput:
    source_path = Path(input_path)
    target_path = Path(output_path)

    if not source_path.exists():
        raise MissingInputPathError(f"Input path does not exist: {source_path}")

    if target_path.exists() and not overwrite:
        raise OverwriteRefusalError(f"Output file already exists and overwrite is disabled: {target_path}")

    parent = target_path.parent
    if parent.exists() and not parent.is_dir():
        raise InvalidInputTypeError(f"Output parent path is not a directory: {parent}")

    if source_path.is_file():
        if source_path.suffix.lower() != ".pdf":
            raise InvalidInputTypeError(f"Input file is not a PDF: {source_path}")
        return ResolvedInput(
            mode="file",
            input_path=source_path,
            output_path=target_path,
            pdf_paths=(source_path,),
        )

    if source_path.is_dir():
        pdf_paths = tuple(sorted((path for path in source_path.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"), key=lambda path: path.name))
        if not pdf_paths:
            raise EmptyInputError(f"Input directory contains no PDF files: {source_path}")
        return ResolvedInput(
            mode="directory",
            input_path=source_path,
            output_path=target_path,
            pdf_paths=pdf_paths,
        )

    raise InvalidInputTypeError(f"Input path is neither a file nor a directory: {source_path}")
