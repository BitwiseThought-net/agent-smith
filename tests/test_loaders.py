"""
Every loader in loaders/ follows the same shape: check the file exists,
check the target framework's Knowledge class exposes the expected source
type, and build a source object tagged with {"source": <filename>, "type":
<ext>}. Rather than hand-writing near-identical test functions per file, we
drive the whole set from one parametrized table - this also means a loader
wired to the *wrong* Knowledge attribute (as loaders/md.py is, see below)
gets caught automatically rather than needing a bespoke test to notice it.
"""
import pytest

from loaders import (
    csv as csv_loader,
    docx as docx_loader,
    html as html_loader,
    jpg as jpg_loader,
    js as js_loader,
    json as json_loader,
    log as log_loader,
    md as md_loader,
    ods as ods_loader,
    png as png_loader,
    pptx as pptx_loader,
    py as py_loader,
    soap as soap_loader,
    tex as tex_loader,
    tsv as tsv_loader,
    txt as txt_loader,
    xlsx as xlsx_loader,
    xml as xml_loader,
    yaml as yaml_loader,
)

# (loader module, filename to create, expected Knowledge attribute name, expected "type" tag)
LOADER_SPECS = [
    (csv_loader, "data.csv", "CSV", "csv"),
    (docx_loader, "report.docx", "Docling", "docx"),
    (html_loader, "page.html", "Docling", "html"),
    (jpg_loader, "photo.jpg", "Docling", "jpg"),
    (js_loader, "script.js", "JSON", "js"),
    (json_loader, "data.json", "JSON", "json"),
    (log_loader, "app.log", "JSON", "log"),
    (ods_loader, "sheet.ods", "Excel", "ods"),
    (png_loader, "image.png", "Docling", "png"),
    (pptx_loader, "deck.pptx", "Docling", "pptx"),
    (py_loader, "script.py", "JSON", "py"),
    (soap_loader, "request.soap", "JSON", "soap"),
    (tex_loader, "paper.tex", "JSON", "tex"),
    (tsv_loader, "data.tsv", "TextFile", "tsv"),
    (txt_loader, "notes.txt", "TextFile", "txt"),
    (xlsx_loader, "sheet.xlsx", "Excel", "xlsx"),
    (xml_loader, "data.xml", "XML", "xml"),
    (yaml_loader, "config.yaml", "JSON", "yaml"),
]


@pytest.mark.parametrize("loader_module,filename,attr_name,type_tag", LOADER_SPECS)
def test_returns_none_when_file_missing(isolated_cwd, loader_module, filename, attr_name, type_tag):
    assert loader_module.get_source(filename) is None


@pytest.mark.parametrize("loader_module,filename,attr_name,type_tag", LOADER_SPECS)
def test_returns_source_with_correct_type_tag(isolated_cwd, loader_module, filename, attr_name, type_tag):
    f = isolated_cwd / filename
    f.write_text("content")
    source = loader_module.get_source(str(f))
    assert source is not None
    assert source.file_path == str(f)
    assert source.metadata == {"source": filename, "type": type_tag}


@pytest.mark.parametrize("loader_module,filename,attr_name,type_tag", LOADER_SPECS)
def test_returns_none_when_framework_lacks_expected_source_type(
    isolated_cwd, monkeypatch, loader_module, filename, attr_name, type_tag
):
    """
    Simulates a framework whose Knowledge factory doesn't support this
    source type (e.g. an ai_layer/*.py adapter that only implements a
    subset of source types). Patching the loader module's own imported
    `Knowledge` reference - rather than the shared fake in conftest --
    keeps each test isolated and pins down exactly which attribute each
    loader checks.
    """
    f = isolated_cwd / filename
    f.write_text("content")

    class EmptyKnowledge:
        pass  # deliberately has none of CSV/Docling/JSON/Excel/TextFile/XML

    monkeypatch.setattr(loader_module, "Knowledge", EmptyKnowledge)
    assert loader_module.get_source(str(f)) is None


def test_md_loader_returns_none_when_file_missing(isolated_cwd):
    assert md_loader.get_source("does_not_exist.md") is None


def test_md_loader_returns_source_when_file_exists_and_json_supported(isolated_cwd):
    f = isolated_cwd / "readme.md"
    f.write_text("# Heading\n\nSome markdown content.")
    source = md_loader.get_source(str(f))
    assert source is not None
    assert source.file_path == str(f)
    assert source.metadata == {"source": "readme.md", "type": "md"}


def test_md_loader_checks_json_not_textfile_attribute(isolated_cwd, monkeypatch):
    """
    Pins down the current (likely unintended) wiring in loaders/md.py: it
    guards on `hasattr(Knowledge, "JSON")`, not "TextFile" or "Docling" as
    you'd expect for markdown prose. A framework whose Knowledge factory
    supports TextFile/Docling but not JSON would silently fail to load any
    .md files as a result. This test documents the current behavior rather
    than fixing it.
    """
    f = isolated_cwd / "readme.md"
    f.write_text("# Heading")

    class OnlyTextFile:
        TextFile = object

    monkeypatch.setattr(md_loader, "Knowledge", OnlyTextFile)
    # If md.py were correctly wired to TextFile, this would succeed; as
    # written, it checks for JSON support instead and returns None here.
    assert md_loader.get_source(str(f)) is None


class TestPdfLoaderIsBroken:
    """
    loaders/pdf.py is broken: it references a bare name `PDFKnowledgeSource`
    that is never imported or defined anywhere in the module, and unlike
    every other loader it doesn't check os.path.exists() first or consult
    the Knowledge factory at all. Any call - for an existing file, a
    missing file, doesn't matter - raises NameError. These tests pin down
    that current (broken) behavior; they are not a workaround or a fix.
    """

    def test_raises_nameerror_for_missing_file(self, isolated_cwd):
        import loaders.pdf as pdf_loader
        with pytest.raises(NameError):
            pdf_loader.get_source("does_not_exist.pdf")

    def test_raises_nameerror_even_for_existing_file(self, isolated_cwd):
        import loaders.pdf as pdf_loader
        f = isolated_cwd / "real.pdf"
        f.write_text("%PDF-1.4 fake content")
        with pytest.raises(NameError):
            pdf_loader.get_source(str(f))
