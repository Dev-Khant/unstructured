import os
import pathlib

from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Table, Text
from unstructured.partition.epub import partition_epub
from unstructured.partition.json import partition_json
from unstructured.partition.utils.constants import UNSTRUCTURED_INCLUDE_DEBUG_METADATA
from unstructured.staging.base import elements_to_json

DIRECTORY = pathlib.Path(__file__).parent.resolve()
expected_sections = {
    "CHAPTER I THE SUN-SEEKER",
    "CHAPTER II RINKS AND SKATERS",
    "CHAPTER III TEES AND CRAMPITS",
    "CHAPTER IV TOBOGGANING",
    # not included in expected sections because TOC doesn't perfectly match with EpubHtml items
    # 'CHAPTER V ICE-HOCKEY',
    "CHAPTER VI SKI-ING",
    "CHAPTER VII NOTES ON WINTER RESORTS",
    "CHAPTER VIII FOR PARENTS AND GUARDIANS",
    "THE FULL PROJECT GUTENBERG LICENSE",
}


def test_partition_epub_from_filename():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename)
    assert len(elements) > 0
    assert elements[0].text.startswith("The Project Gutenberg eBook of Winter Sports")
    all_sections = set()
    for element in elements:
        assert element.metadata.filename == "winter-sports.epub"
        assert element.metadata.section is not None
        all_sections.add(element.metadata.section)
    assert all_sections == expected_sections
    if UNSTRUCTURED_INCLUDE_DEBUG_METADATA:
        assert {element.metadata.detection_origin for element in elements} == {"epub"}


def test_partition_epub_from_filename_returns_table_in_elements():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename)
    assert len(elements) > 0
    assert elements[14] == Table(
        text="Contents. \n List of Illustrations   "
        "(In certain versions of this etext [in certain browsers]"
        "\nclicking on the image will bring up a larger version.) "
        "\n (etext transcriber's note)",
    )


def test_partition_epub_from_filename_returns_uns_elements():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename)
    assert len(elements) > 0
    assert isinstance(elements[0], Text)


def test_partition_epub_from_filename_with_metadata_filename():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename, metadata_filename="test")
    assert len(elements) > 0
    assert all(element.metadata.filename == "test" for element in elements)
    assert all(element.metadata.section is not None for element in elements)


def test_partition_epub_from_file():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    with open(filename, "rb") as f:
        elements = partition_epub(file=f)
    assert len(elements) > 0
    assert elements[0].text.startswith("The Project Gutenberg eBook of Winter Sports")
    all_sections = set()
    for element in elements:
        assert element.metadata.filename is None
        all_sections.add(element.metadata.section)
    assert all_sections == expected_sections


def test_partition_epub_from_file_with_metadata_filename():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    with open(filename, "rb") as f:
        elements = partition_epub(file=f, metadata_filename="test")
    assert len(elements) > 0
    for element in elements:
        assert element.metadata.filename == "test"


def test_partition_epub_from_filename_exclude_metadata():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename, include_metadata=False)
    assert elements[0].metadata.filetype is None
    assert elements[0].metadata.page_name is None
    assert elements[0].metadata.filename is None
    assert elements[0].metadata.section is None


def test_partition_epub_from_file_exlcude_metadata():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    with open(filename, "rb") as f:
        elements = partition_epub(file=f, include_metadata=False)
    assert elements[0].metadata.filetype is None
    assert elements[0].metadata.page_name is None
    assert elements[0].metadata.filename is None
    assert elements[0].metadata.section is None


def test_partition_epub_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"
    mocker.patch(
        "unstructured.partition.epub.get_last_modified_date",
        return_value=mocked_last_modification_date,
    )
    elements = partition_epub(filename=filename)

    assert elements[0].metadata.last_modified == mocked_last_modification_date


def test_partition_epub_custom_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"
    expected_last_modification_date = "2020-07-05T09:24:28"

    mocker.patch(
        "unstructured.partition.html.get_last_modified_date",
        return_value=mocked_last_modification_date,
    )

    elements = partition_epub(
        filename=filename,
        metadata_last_modified=expected_last_modification_date,
    )

    assert elements[0].metadata.last_modified == expected_last_modification_date


def test_partition_epub_from_file_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"

    mocker.patch(
        "unstructured.partition.epub.get_last_modified_date_from_file",
        return_value=mocked_last_modification_date,
    )

    with open(filename, "rb") as f:
        elements = partition_epub(file=f)

    assert elements[0].metadata.last_modified == mocked_last_modification_date


def test_partition_epub_from_file_custom_metadata_date(
    mocker,
    filename="example-docs/winter-sports.epub",
):
    mocked_last_modification_date = "2029-07-05T09:24:28"
    expected_last_modification_date = "2020-07-05T09:24:28"

    mocker.patch(
        "unstructured.partition.html.get_last_modified_date_from_file",
        return_value=mocked_last_modification_date,
    )

    with open(filename, "rb") as f:
        elements = partition_epub(file=f, metadata_last_modified=expected_last_modification_date)

    assert elements[0].metadata.last_modified == expected_last_modification_date


def test_partition_epub_with_json(
    filename=os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub"),
):
    elements = partition_epub(filename=filename)
    test_elements = partition_json(text=elements_to_json(elements))

    assert len(elements) == len(test_elements)
    assert elements[0].metadata.filename == test_elements[0].metadata.filename
    assert elements[0].metadata.section == test_elements[0].metadata.section
    for i in range(len(elements)):
        elements[i] == test_elements[i]


def test_add_chunking_strategy_on_partition_epub(
    filename=os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub"),
):
    elements = partition_epub(filename=filename)
    chunk_elements = partition_epub(filename, chunking_strategy="by_title")
    chunks = chunk_by_title(elements)
    assert chunk_elements != elements
    assert chunk_elements == chunks


def test_add_chunking_strategy_on_partition_epub_non_default(
    filename=os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub"),
):
    elements = partition_epub(filename=filename)
    chunk_elements = partition_epub(
        filename,
        chunking_strategy="by_title",
        max_characters=5,
        new_after_n_chars=5,
        combine_text_under_n_chars=0,
    )
    chunks = chunk_by_title(
        elements,
        max_characters=5,
        new_after_n_chars=5,
        combine_text_under_n_chars=0,
    )
    assert chunk_elements != elements
    assert chunk_elements == chunks


def test_partition_epub_element_metadata_has_languages():
    filename = os.path.join(DIRECTORY, "..", "..", "..", "example-docs", "winter-sports.epub")
    elements = partition_epub(filename=filename)
    assert elements[0].metadata.languages == ["eng"]


def test_partition_epub_respects_detect_language_per_element():
    filename = "example-docs/language-docs/eng_spa_mult.epub"
    elements = partition_epub(filename=filename, detect_language_per_element=True)
    langs = [element.metadata.languages for element in elements]
    assert langs == [["eng"], ["eng"], ["spa", "eng"], ["eng"], ["eng"], ["spa"]]
