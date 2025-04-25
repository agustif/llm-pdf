# llm-plugin-pdf

[![PyPI](https://img.shields.io/pypi/v/llm-plugin-pdf.svg)](https://pypi.org/project/llm-plugin-pdf/)
[![Changelog](https://img.shields.io/github/v/release/agustif/llm-pdf?include_prereleases&label=changelog)](https://github.com/agustif/llm-pdf/releases)
[![Tests](https://github.com/agustif/llm-pdf/actions/workflows/test.yml/badge.svg)](https://github.com/agustif/llm-pdf/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/agustif/llm-pdf/blob/main/LICENSE)

LLM plugin for loading text from PDF files (local or URL) using PyMuPDF.

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-plugin-pdf
```

This plugin requires the `PyMuPDF` and `requests` packages.

## Usage

This plugin adds support for the `pdf:` fragment prefix. You can use it to load the full text content of a PDF from a local file path or a web URL.

```bash
# Load from a local file
llm fragment pdf:/path/to/your/document.pdf

# Load from a URL
llm fragment pdf:https://example.com/some-document.pdf
```

You can pipe the output to LLM commands:

```bash
llm fragment pdf:https://arxiv.org/pdf/2310.06825.pdf | llm -s "Summarize this PDF"
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-pdf
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
# Install in editable mode with test dependencies
python -m pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```
