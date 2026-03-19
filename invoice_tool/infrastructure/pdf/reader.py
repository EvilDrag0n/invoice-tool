import pathlib
import pdfplumber
from invoice_tool.application.errors import UnreadablePDFError

def read_pdf_text(file_path: pathlib.Path) -> str:
    """
    Reads text from a local PDF file and returns it as a combined string.
    
    Args:
        file_path: Path to the PDF file.
        
    Returns:
        Combined text from all pages, separated by double newlines.
        
    Raises:
        UnreadablePDFError: If the file is not a PDF, cannot be opened, or contains no text.
    """
    # Ensure it's a Path object
    path = pathlib.Path(file_path)
    
    # 1. Reject non-PDF suffix
    if path.suffix.lower() != '.pdf':
        raise UnreadablePDFError(f"File '{path.name}' is not a PDF file.")

    try:
        # 2. Open PDF with pdfplumber (handles spaces and Chinese characters in Path objects)
        with pdfplumber.open(path) as pdf:
            page_texts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    page_texts.append(text.strip())
            
            # 3. Combine page text
            final_text = "\n\n".join(page_texts)
            
            # 4. Reject empty/falsy final text
            if not final_text:
                raise UnreadablePDFError(f"PDF file '{path.name}' contains no extractable text.")
                
            return final_text
            
    except Exception as e:
        # 5. Reject exceptions from pdfplumber
        if isinstance(e, UnreadablePDFError):
            raise
        raise UnreadablePDFError(f"Failed to read PDF file '{path.name}': {str(e)}")
