import os
import sys
import types
import pytest

import knowledge_manager as km


class TestValidateLoaders:
    def test_returns_empty_set_when_loaders_dir_missing(self, isolated_cwd):
        assert km.validate_loaders(["a.txt"]) == set()

    def test_returns_empty_set_when_loaders_dir_empty(self, isolated_cwd):
        (isolated_cwd / "loaders").mkdir()
        assert km.validate_loaders(["a.txt"]) == set()

    def test_flags_missing_loader_for_extension(self, isolated_cwd):
        loaders_dir = isolated_cwd / "loaders"
        loaders_dir.mkdir()
        (loaders_dir / "txt.py").write_text("")
        missing = km.validate_loaders(["a.txt", "b.weirdext"])
        assert missing == {"weirdext"}

    def test_no_missing_when_all_extensions_covered(self, isolated_cwd):
        loaders_dir = isolated_cwd / "loaders"
        loaders_dir.mkdir()
        (loaders_dir / "txt.py").write_text("")
        (loaders_dir / "csv.py").write_text("")
        assert km.validate_loaders(["a.txt", "b.csv"]) == set()

    def test_skips_directories_and_extensionless_files(self, isolated_cwd):
        loaders_dir = isolated_cwd / "loaders"
        loaders_dir.mkdir()
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "subdir").mkdir()
        assert km.validate_loaders(["subdir", "README"]) == set()


class TestGetAllKnowledgeSources:
    def test_warns_and_returns_empty_when_dir_missing(self, isolated_cwd):
        assert km.get_all_knowledge_sources() == []

    def test_returns_empty_when_dir_empty(self, isolated_cwd):
        (isolated_cwd / "knowledge").mkdir()
        assert km.get_all_knowledge_sources() == []

    def test_ignores_hidden_files(self, isolated_cwd):
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / ".hidden").write_text("secret")
        assert km.get_all_knowledge_sources() == []

    def test_loads_source_via_matching_loader_module(self, isolated_cwd, monkeypatch):
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "notes.qux").write_text("data")

        loaders_dir = isolated_cwd / "loaders"
        loaders_dir.mkdir()
        (loaders_dir / "qux.py").write_text("")  # existence is enough for validate_loaders

        # Inject a fake loaders.qux module so get_all_knowledge_sources's
        # importlib.import_module("loaders.qux") call resolves to it, without
        # needing a real file on sys.path.
        fake_loader = types.ModuleType("loaders.qux")
        fake_loader.get_source = lambda file: f"SOURCE::{file}"
        monkeypatch.setitem(sys.modules, "loaders.qux", fake_loader)

        sources = km.get_all_knowledge_sources()
        assert sources == ["SOURCE::notes.qux"]

    def test_loader_returning_none_is_excluded(self, isolated_cwd, monkeypatch):
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "empty.qux").write_text("")

        loaders_dir = isolated_cwd / "loaders"
        loaders_dir.mkdir()
        (loaders_dir / "qux.py").write_text("")

        fake_loader = types.ModuleType("loaders.qux")
        fake_loader.get_source = lambda file: None
        monkeypatch.setitem(sys.modules, "loaders.qux", fake_loader)

        assert km.get_all_knowledge_sources() == []

    def test_loader_exception_is_caught_and_skips_file(self, isolated_cwd, monkeypatch):
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "broken.qux").write_text("")
        (knowledge_dir / "fine.qux2").write_text("")

        loaders_dir = isolated_cwd / "loaders"
        loaders_dir.mkdir()
        (loaders_dir / "qux.py").write_text("")
        (loaders_dir / "qux2.py").write_text("")

        def raise_loader(file):
            raise ValueError("boom")

        fake_broken = types.ModuleType("loaders.qux")
        fake_broken.get_source = raise_loader
        fake_fine = types.ModuleType("loaders.qux2")
        fake_fine.get_source = lambda file: f"OK::{file}"
        monkeypatch.setitem(sys.modules, "loaders.qux", fake_broken)
        monkeypatch.setitem(sys.modules, "loaders.qux2", fake_fine)

        sources = km.get_all_knowledge_sources()
        assert sources == ["OK::fine.qux2"]

    def test_files_with_unrecognized_extension_are_skipped(self, isolated_cwd):
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "notes.unknownext").write_text("data")
        # loaders/ dir doesn't even exist -> validate_loaders returns set(),
        # but get_all_knowledge_sources should still skip the file gracefully
        # rather than crashing on a missing "loaders.unknownext" module.
        assert km.get_all_knowledge_sources() == []

    def test_subdirectories_inside_knowledge_are_skipped(self, isolated_cwd):
        knowledge_dir = isolated_cwd / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "subdir").mkdir()
        assert km.get_all_knowledge_sources() == []
