import llm
import pytest
from llm_plugin_pdf import pdf_loader
from unittest.mock import patch, MagicMock
from pathlib import Path
import requests

# Define the path to the test directory and dummy PDF
TESTS_DIR = Path(__file__).parent
DUMMY_PDF_PATH = TESTS_DIR / "dummy.pdf"
NOT_A_PDF_PATH = TESTS_DIR / "not_a_pdf.txt"

# Ensure the dummy PDF exists (it should have been downloaded)
@pytest.fixture(autouse=True)
def check_dummy_pdf():
    if not DUMMY_PDF_PATH.exists():
        pytest.fail(f"Dummy PDF file not found at {DUMMY_PDF_PATH}. Please download it.")
    # Create a dummy non-PDF file for testing
    if not NOT_A_PDF_PATH.exists():
        NOT_A_PDF_PATH.write_text("This is not a PDF.")
    yield
    # Clean up dummy text file
    if NOT_A_PDF_PATH.exists():
        NOT_A_PDF_PATH.unlink()

def test_pdf_loader_local_file_success():
    """Test loading text from a local PDF file."""
    fragment = pdf_loader(str(DUMMY_PDF_PATH))
    assert isinstance(fragment, llm.Fragment)
    assert "Dummy PDF file" in str(fragment) # Check for expected text
    assert fragment.source == str(DUMMY_PDF_PATH.resolve())

@patch("llm_plugin_pdf.requests.get")
def test_pdf_loader_url_success(mock_get):
    """Test loading text from a PDF URL."""
    test_url = "https://example.com/dummy.pdf"
    # Read content from the local dummy PDF to use in the mock response
    dummy_content = DUMMY_PDF_PATH.read_bytes()

    # Configure the mock response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {'content-type': 'application/pdf'}
    mock_response.content = dummy_content
    mock_get.return_value = mock_response

    fragment = pdf_loader(test_url)

    assert isinstance(fragment, llm.Fragment)
    assert "Dummy PDF file" in str(fragment)
    assert fragment.source == test_url
    mock_get.assert_called_once_with(test_url, stream=True, timeout=30)

def test_pdf_loader_local_file_not_found():
    """Test error when local file does not exist."""
    non_existent_path = str(TESTS_DIR / "non_existent.pdf")
    with pytest.raises(FileNotFoundError) as excinfo:
        pdf_loader(non_existent_path)
    assert f"Local file not found: {non_existent_path}" in str(excinfo.value)

def test_pdf_loader_local_file_not_pdf():
    """Test error when local file is not a PDF extension."""
    # Create the dummy file for this test
    NOT_A_PDF_PATH.write_text("This is not a PDF.")
    try:
        with pytest.raises(ValueError) as excinfo:
            pdf_loader(str(NOT_A_PDF_PATH))
        assert f"File does not have a .pdf extension: {NOT_A_PDF_PATH}" in str(excinfo.value)
    finally:
        # Clean up the dummy file
        if NOT_A_PDF_PATH.exists():
            NOT_A_PDF_PATH.unlink()

@patch("llm_plugin_pdf.requests.get")
def test_pdf_loader_url_download_error(mock_get):
    """Test error during URL download."""
    test_url = "https://example.com/dummy.pdf"
    mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

    with pytest.raises(ValueError) as excinfo:
        pdf_loader(test_url)
    assert f"Failed to download PDF from URL {test_url}: Connection failed" in str(excinfo.value)

@patch("llm_plugin_pdf.requests.get")
def test_pdf_loader_url_not_pdf(mock_get):
    """Test error when URL does not point to a PDF content type."""
    test_url = "https://example.com/not_a_pdf.html"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.content = b"<html><body>Test</body></html>"
    mock_get.return_value = mock_response

    with pytest.raises(ValueError) as excinfo:
        pdf_loader(test_url)
    assert "URL does not point to a PDF (Content-Type: text/html)" in str(excinfo.value)

@patch("llm_plugin_pdf.fitz.open")
def test_pdf_loader_pdf_processing_error(mock_fitz_open):
    """Test error during PDF text extraction."""
    mock_fitz_open.side_effect = Exception("Corrupted PDF structure")

    with pytest.raises(ValueError) as excinfo:
        pdf_loader(str(DUMMY_PDF_PATH)) # Use local file path
    
    # Check the wrapped error message
    expected_source = str(DUMMY_PDF_PATH.resolve())
    assert f"Failed to extract text from PDF {expected_source}: Corrupted PDF structure" in str(excinfo.value)
