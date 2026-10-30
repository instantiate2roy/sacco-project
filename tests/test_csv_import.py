import pytest

from src.csv_import import CsvImport
from src.exceptions import ImportFileError


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_load_keeps_header_and_rows(tmp_path):
    importer = CsvImport()
    rows = importer.load(write(tmp_path / "loans.csv", "code,name\nA,School fees\nB,Business\n"))

    assert rows == [["code", "name"], ["A", "School fees"], ["B", "Business"]]
    assert importer.header == ["code", "name"]
    assert importer.records() == [{"code": "A", "name": "School fees"}, {"code": "B", "name": "Business"}]


def test_load_without_header_and_skips_blank_lines(tmp_path):
    rows = CsvImport().load(write(tmp_path / "loans.csv", "code,name\n\nA,School fees\n,\n"), include_header=False)

    assert rows == [["A", "School fees"]]


def test_load_reads_excel_byte_order_mark(tmp_path):
    path = tmp_path / "loans.csv"
    path.write_bytes("﻿code,name\nA,School fees\n".encode("utf-8"))

    importer = CsvImport()
    importer.load(path)

    assert importer.header == ["code", "name"]


@pytest.mark.parametrize("name, text, message", [
    ("empty.csv", "\n\n", "is empty"),
    ("blank.csv", "code,\nA,B\n", "blank column name"),
    ("dupes.csv", "code,code\nA,B\n", "duplicate column names: code"),
    ("ragged.csv", "code,name\nA\n", "row 2: expected 2 values, found 1"),
])
def test_load_rejects_badly_formed_files(tmp_path, name, text, message):
    with pytest.raises(ImportFileError, match=message):
        CsvImport().load(write(tmp_path / name, text))


def test_load_rejects_missing_file_folder_and_other_extensions(tmp_path):
    importer = CsvImport()
    with pytest.raises(ImportFileError, match="File not found"):
        importer.load(tmp_path / "missing.csv")
    with pytest.raises(ImportFileError, match="Not a file"):
        importer.load(tmp_path)
    with pytest.raises(ImportFileError, match="Expected a .csv file"):
        importer.load(write(tmp_path / "loans.txt", "code\nA\n"))


def test_records_before_load_is_an_error():
    with pytest.raises(ImportFileError, match="call load"):
        CsvImport().records()


def test_load_dir_data_reads_subfolders_by_file_name(tmp_path):
    (tmp_path / "ref").mkdir()
    write(tmp_path / "case.csv", "uuid,status\nc1,OPEN\n")
    write(tmp_path / "ref" / "loan_types.csv", "code\nSF\n")

    data = CsvImport().load_dir_data(tmp_path)

    assert set(data) == {"case", "loan_types"}
    assert data["case"] == {"header": ["uuid", "status"], "rows": [{"uuid": "c1", "status": "OPEN"}]}


def test_load_dir_data_rejects_two_files_with_one_name(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    write(tmp_path / "a" / "case.csv", "uuid\nc1\n")
    write(tmp_path / "b" / "case.csv", "uuid\nc2\n")

    with pytest.raises(ImportFileError, match="both called case.csv"):
        CsvImport().load_dir_data(tmp_path)


def test_load_dir_data_rejects_missing_or_empty_folders(tmp_path):
    with pytest.raises(ImportFileError, match="Folder not found"):
        CsvImport().load_dir_data(tmp_path / "missing")
    with pytest.raises(ImportFileError, match="No CSV files"):
        CsvImport().load_dir_data(tmp_path)
