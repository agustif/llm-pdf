import llm
import click
import fitz  # PyMuPDF
import requests
import tempfile
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Union # Keep Union for now

# Placeholder for potential future image handling
# import base64 

@llm.hookimpl
def register_fragment_loaders(register):
    register("pdf", pdf_loader)

def is_url(path_or_url: str) -> bool:
    """Check if the provided string is a URL."""
    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def pdf_loader(argument: str) -> llm.Fragment: # Return single fragment for now
    """
    Load text content from a PDF file (local path or URL).

    Argument is a local file path or a web URL pointing to a PDF.
    """
    source_display = argument # For display in errors or fragment source

    pdf_bytes = None
    if is_url(argument):
        # Handle URL
        try:
            response = requests.get(argument, stream=True, timeout=30)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            # Check content type - optional but recommended
            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type:
                 raise ValueError(f"URL does not point to a PDF (Content-Type: {content_type})")

            # Read content into memory (consider temp file for very large PDFs later)
            pdf_bytes = response.content
            source_display = argument # Keep URL as source
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to download PDF from URL {argument}: {e}") from e
        except ValueError as e: # Catch our content-type error
             raise e

    else:
        # Handle local file path
        pdf_path = Path(argument)
        if not pdf_path.is_file():
            raise FileNotFoundError(f"Local file not found: {argument}")
        if pdf_path.suffix.lower() != '.pdf':
             raise ValueError(f"File does not have a .pdf extension: {argument}")
        
        source_display = str(pdf_path.resolve()) # Use resolved path as source

    # Process the PDF (either from bytes or path)
    full_text = ""
    doc = None # Initialize doc to None
    try:
        if pdf_bytes:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        else: # Must be local path
             doc = fitz.open(pdf_path)

        for page in doc:
            full_text += page.get_text()
        doc.close()
    
    except Exception as e:
        if doc and doc.is_open:
            doc.close()
        # Distinguish between download/file errors and PDF processing errors
        if pdf_bytes or pdf_path.exists(): # Check if we got the file/data
             raise ValueError(f"Failed to extract text from PDF {source_display}: {e}") from e
        else: 
             # This 'else' branch might now be less relevant if the initial FileNotFoundError
             # propagates directly. If an error occurs here, it's likely a fitz processing error.
             # Let's keep the specific ValueError for extraction failure.
             # Consider if just raising e is better? Let's stick with the specific ValueError for now.
             raise ValueError(f"Failed to extract text from PDF {source_display}: {e}") from e
             # Original re-raise: raise e

    # Create the text fragment
    return llm.Fragment(full_text, source=source_display)

# Remove the example register_commands hook if it exists
@llm.hookimpl
def register_commands(cli):
    pass # No extra commands needed for this plugin
