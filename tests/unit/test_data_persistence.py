"""Tests for data persistence path and pickle safety."""

from __future__ import annotations

import pytest

from proxywhirl.data_persistence import DataPersistence


def test_save_json_rejects_path_traversal(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="escapes"):
        persistence.save_json("../outside", {"value": 1})

    assert not (tmp_path.parent / "outside.json").exists()


def test_save_json_rejects_absolute_name(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="relative"):
        persistence.save_json(str(tmp_path.parent / "outside"), {"value": 1})


@pytest.mark.parametrize("nested_name", ["nested/item", "nested\\item"])
def test_save_json_rejects_nested_name(tmp_path, nested_name: str) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="flat file name"):
        persistence.save_json(nested_name, {"value": 1})

    assert not (tmp_path / "nested").exists()


def test_load_json_rejects_nested_name(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="flat file name"):
        persistence.load_json("nested/item")


def test_delete_rejects_nested_name(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="flat file name"):
        persistence.delete("nested/item")


def test_delete_rejects_unknown_format(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="Unsupported persistence format"):
        persistence.delete("item", format_type="yaml")


def test_pickle_disabled_by_default(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)

    with pytest.raises(ValueError, match="disabled by default"):
        persistence.save_pickle("item", {"value": 1})

    with pytest.raises(ValueError, match="disabled by default"):
        persistence.load_pickle("item")


def test_pickle_requires_explicit_opt_in(tmp_path) -> None:
    persistence = DataPersistence(tmp_path, allow_pickle=True)

    persistence.save_pickle("item", {"value": 1})

    assert persistence.load_pickle("item") == {"value": 1}


def test_save_pickle_rejects_nested_name_when_pickle_allowed(tmp_path) -> None:
    persistence = DataPersistence(tmp_path, allow_pickle=True)

    with pytest.raises(ValueError, match="flat file name"):
        persistence.save_pickle("nested/item", {"value": 1})

    assert not (tmp_path / "nested").exists()


def test_list_files_returns_supported_root_files_only(tmp_path) -> None:
    persistence = DataPersistence(tmp_path, allow_pickle=True)
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (nested_dir / "child.json").write_text("{}")
    (tmp_path / "directory.json").mkdir()
    (tmp_path / "item.txt").write_text("ignored")

    persistence.save_json("config", {"value": 1})
    persistence.save_pickle("cache", {"value": 2})

    assert persistence.list_files() == ["cache", "config"]


def test_get_size_ignores_directories(tmp_path) -> None:
    persistence = DataPersistence(tmp_path)
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (nested_dir / "child.json").write_text("ignored")
    (tmp_path / "directory.json").mkdir()

    persistence.save_json("config", {"value": 1})

    assert persistence.get_size() == (tmp_path / "config.json").stat().st_size
