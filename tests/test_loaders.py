import pytest

from loaders import json as json_loader
from loaders import csv as csv_loader
from loaders import txt as txt_loader
from loaders import md as md_loader


@pytest.mark.parametrize("loader_module,filename", [
    (json_loader, "missing.json"),
    (csv_loader, "missing.csv"),
    (txt_loader, "missing.txt"),
    (md_loader, "missing.md"),
])
def test_returns_none_for_nonexistent_file(isolated_cwd, loader_module, filename):
    assert loader_module.get_source(filename) is None


def test_json_loader_returns_source_with_correct_metadata(isolated_cwd):
    f = isolated_cwd / "data.json"
    f.write_text("{}")
    source = json_loader.get_source(str(f))
    assert source is not None
    assert source.file_path == str(f)
    assert source.metadata == {"source": "data.json", "type": "json"}


def test_csv_loader_returns_source_with_correct_metadata(isolated_cwd):
    f = isolated_cwd / "data.csv"
    f.write_text("a,b\n1,2")
    source = csv_loader.get_source(str(f))
    assert source is not None
    assert source.metadata == {"source": "data.csv", "type": "csv"}


def test_txt_loader_returns_source_with_correct_metadata(isolated_cwd):
    f = isolated_cwd / "notes.txt"
    f.write_text("hello")
    source = txt_loader.get_source(str(f))
    assert source is not None
    assert source.metadata == {"source": "notes.txt", "type": "txt"}


def test_md_loader_uses_json_knowledge_source_not_text_or_markdown(isolated_cwd):
    """
    Documents current (likely unintended) behavior: loaders/md.py routes
    markdown files through Knowledge.JSON rather than Knowledge.TextFile.
    In this test suite's fake orchestrator, Knowledge.JSON and
    Knowledge.TextFile are the same stand-in class, so this test can't
    detect the mismatch by itself -- it only pins the metadata "type" tag
    and file handling. See README/PR notes: worth checking against the
    real CrewAI Knowledge class whether JSONKnowledgeSource can actually
    parse markdown content, since as written a real .md file would be
    handed to a JSON parser.
    """
    f = isolated_cwd / "readme.md"
    f.write_text("# Heading\n\nSome markdown content.")
    source = md_loader.get_source(str(f))
    assert source is not None
    assert source.metadata == {"source": "readme.md", "type": "md"}
