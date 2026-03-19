class InvoiceToolError(Exception):
    """Base exception for all invoice tool errors."""
    pass

class UnreadablePDFError(InvoiceToolError):
    """Raised when a PDF file is non-text or otherwise unreadable."""
    pass

class MissingFieldError(InvoiceToolError):
    """Raised when one or more required invoice fields are missing."""
    pass

class DuplicateIdenticalError(InvoiceToolError):
    """Raised when a duplicate invoice is found with identical data."""
    pass

class DuplicateConflictError(InvoiceToolError):
    """Raised when a duplicate invoice is found with conflicting data."""
    pass

class EmptyInputError(InvoiceToolError):
    """Raised when the input folder contains no PDF files."""
    pass

class NoSuccessfulInvoicesError(InvoiceToolError):
    """Raised when processing completes but no invoice records can be exported."""
    pass

class MissingInputPathError(InvoiceToolError):
    """Raised when the provided input path does not exist."""
    pass

class InvalidInputTypeError(InvoiceToolError):
    """Raised when the provided input path is neither a PDF file nor a directory."""
    pass

class OverwriteRefusalError(InvoiceToolError):
    """Raised when the output file exists and overwrite is not allowed."""
    pass
