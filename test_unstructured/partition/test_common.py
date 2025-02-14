import pytest
from PIL import Image
from unstructured_inference.inference import layout
from unstructured_inference.inference.layout import LayoutElement
from unstructured_inference.inference.layoutelement import LocationlessLayoutElement

from unstructured.documents.coordinates import PixelSpace
from unstructured.documents.elements import (
    CheckBox,
    ElementMetadata,
    FigureCaption,
    Header,
    ListItem,
    NarrativeText,
    Text,
    Title,
)
from unstructured.partition import common
from unstructured.partition.common import (
    _get_page_image_metadata,
    contains_emoji,
    document_to_element_list,
)


class MockPageLayout(layout.PageLayout):
    def __init__(self, number: int, image: Image):
        self.number = number
        self.image = image

    @property
    def elements(self):
        return [
            LocationlessLayoutElement(
                type="Headline",
                text="Charlie Brown and the Great Pumpkin",
            ),
            LocationlessLayoutElement(
                type="Subheadline",
                text="The Beginning",
            ),
            LocationlessLayoutElement(
                type="Text",
                text="This time Charlie Brown had it really tricky...",
            ),
            LocationlessLayoutElement(
                type="Title",
                text="Another book title in the same page",
            ),
        ]


class MockDocumentLayout(layout.DocumentLayout):
    @property
    def pages(self):
        return [
            MockPageLayout(number=1, image=Image.new("1", (1, 1))),
        ]


def test_normalize_layout_element_dict():
    layout_element = {
        "type": "Title",
        "coordinates": [[1, 2], [3, 4], [5, 6], [7, 8]],
        "coordinate_system": None,
        "text": "Some lovely text",
    }
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == Title(
        text="Some lovely text",
        coordinates=[[1, 2], [3, 4], [5, 6], [7, 8]],
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_dict_caption():
    layout_element = {
        "type": "Figure",
        "coordinates": [[1, 2], [3, 4], [5, 6], [7, 8]],
        "text": "Some lovely text",
    }
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == FigureCaption(
        text="Some lovely text",
        coordinates=[[1, 2], [3, 4], [5, 6], [7, 8]],
        coordinate_system=coordinate_system,
    )


@pytest.mark.parametrize(
    ("element_type", "expected_type", "expected_depth"),
    [
        ("Title", Title, None),
        ("Headline", Title, 1),
        ("Subheadline", Title, 2),
        ("Header", Header, None),
    ],
)
def test_normalize_layout_element_headline(element_type, expected_type, expected_depth):
    layout_element = {
        "type": element_type,
        "coordinates": [[1, 2], [3, 4], [5, 6], [7, 8]],
        "text": "Some lovely text",
    }
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(layout_element, coordinate_system=coordinate_system)
    assert element.metadata.category_depth == expected_depth
    assert isinstance(element, expected_type)


def test_normalize_layout_element_dict_figure_caption():
    layout_element = {
        "type": "FigureCaption",
        "coordinates": [[1, 2], [3, 4], [5, 6], [7, 8]],
        "text": "Some lovely text",
    }
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == FigureCaption(
        text="Some lovely text",
        coordinates=[[1, 2], [3, 4], [5, 6], [7, 8]],
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_dict_misc():
    layout_element = {
        "type": "Misc",
        "coordinates": [[1, 2], [3, 4], [5, 6], [7, 8]],
        "text": "Some lovely text",
    }
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == Text(
        text="Some lovely text",
        coordinates=[[1, 2], [3, 4], [5, 6], [7, 8]],
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_layout_element():
    layout_element = LayoutElement(
        type="Text",
        x1=1,
        y1=2,
        x2=3,
        y2=4,
        text="Some lovely text",
    )
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == NarrativeText(
        text="Some lovely text",
        coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_layout_element_narrative_text():
    layout_element = LayoutElement(
        type="NarrativeText",
        x1=1,
        y1=2,
        x2=3,
        y2=4,
        text="Some lovely text",
    )
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == NarrativeText(
        text="Some lovely text",
        coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_checked_box():
    layout_element = LayoutElement(
        type="Checked",
        x1=1,
        y1=2,
        x2=3,
        y2=4,
        text="",
    )
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == CheckBox(
        checked=True,
        coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_unchecked_box():
    layout_element = LayoutElement(
        type="Unchecked",
        x1=1,
        y1=2,
        x2=3,
        y2=4,
        text="",
    )
    coordinate_system = PixelSpace(width=10, height=20)
    element = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert element == CheckBox(
        checked=False,
        coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
        coordinate_system=coordinate_system,
    )


def test_normalize_layout_element_enumerated_list():
    layout_element = LayoutElement(
        type="List",
        x1=1,
        y1=2,
        x2=3,
        y2=4,
        text="1. I'm so cool! 2. You're cool too. 3. We're all cool!",
    )
    coordinate_system = PixelSpace(width=10, height=20)
    elements = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert elements == [
        ListItem(
            text="I'm so cool!",
            coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
            coordinate_system=coordinate_system,
        ),
        ListItem(
            text="You're cool too.",
            coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
            coordinate_system=coordinate_system,
        ),
        ListItem(
            text="We're all cool!",
            coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
            coordinate_system=coordinate_system,
        ),
    ]


def test_normalize_layout_element_bulleted_list():
    layout_element = LayoutElement(
        type="List",
        x1=1,
        y1=2,
        x2=3,
        y2=4,
        text="* I'm so cool! * You're cool too. * We're all cool!",
    )
    coordinate_system = PixelSpace(width=10, height=20)
    elements = common.normalize_layout_element(
        layout_element,
        coordinate_system=coordinate_system,
    )
    assert elements == [
        ListItem(
            text="I'm so cool!",
            coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
            coordinate_system=coordinate_system,
        ),
        ListItem(
            text="You're cool too.",
            coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
            coordinate_system=coordinate_system,
        ),
        ListItem(
            text="We're all cool!",
            coordinates=((1, 2), (1, 4), (3, 4), (3, 2)),
            coordinate_system=coordinate_system,
        ),
    ]


class MockPopenWithError:
    def __init__(self, *args, **kwargs):
        pass

    def communicate(self):
        return b"", b"an error occurred"


def test_convert_office_doc_captures_errors(monkeypatch, caplog):
    import subprocess

    monkeypatch.setattr(subprocess, "Popen", MockPopenWithError)
    common.convert_office_doc("no-real.docx", "fake-directory", target_format="docx")
    assert "an error occurred" in caplog.text


class MockDocxEmptyTable:
    def __init__(self):
        self.rows = []


def test_convert_ms_office_table_to_text_works_with_empty_tables():
    table = MockDocxEmptyTable()
    assert common.convert_ms_office_table_to_text(table, as_html=True) == ""
    assert common.convert_ms_office_table_to_text(table, as_html=False) == ""


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("<table><tbody><tr><td>👨\\U+1F3FB🔧</td></tr></tbody></table>", True),
        ("<table><tbody><tr><td>Hello!</td></tr></tbody></table>", False),
    ],
)
def test_contains_emoji(text, expected):
    assert contains_emoji(text) is expected


def test_document_to_element_list_omits_coord_system_when_coord_points_absent():
    layout_elem_absent_coordinates = MockDocumentLayout()
    elements = document_to_element_list(layout_elem_absent_coordinates)
    assert elements[0].metadata.coordinates is None


def test_get_page_image_metadata_and_coordinate_system():
    doc = MockDocumentLayout()
    metadata = _get_page_image_metadata(doc.pages[0])
    assert isinstance(metadata, dict)


def test_set_element_hierarchy():
    elements_to_set = [
        Title(text="Title"),  # 0
        NarrativeText(text="NarrativeText"),  # 1
        FigureCaption(text="FigureCaption"),  # 2
        ListItem(text="ListItem"),  # 3
        ListItem(text="ListItem", metadata=ElementMetadata(category_depth=1)),  # 4
        ListItem(text="ListItem", metadata=ElementMetadata(category_depth=1)),  # 5
        ListItem(text="ListItem"),  # 6
        CheckBox(element_id="some-id-1", checked=True),  # 7
        Title(text="Title 2"),  # 8
        ListItem(text="ListItem"),  # 9
        ListItem(text="ListItem"),  # 10
        Text(text="Text"),  # 11
    ]
    elements = common.set_element_hierarchy(elements_to_set)

    assert (
        elements[1].metadata.parent_id == elements[0].id
    ), "NarrativeText should be child of Title"
    assert (
        elements[2].metadata.parent_id == elements[0].id
    ), "FigureCaption should be child of Title"
    assert elements[3].metadata.parent_id == elements[0].id, "ListItem should be child of Title"
    assert elements[4].metadata.parent_id == elements[3].id, "ListItem should be child of Title"
    assert elements[5].metadata.parent_id == elements[3].id, "ListItem should be child of Title"
    assert elements[6].metadata.parent_id == elements[0].id, "ListItem should be child of Title"
    assert (
        elements[7].metadata.parent_id is None
    ), "CheckBox should be None, as it's not a Text based element"
    assert elements[8].metadata.parent_id is None, "Title 2 should be child of None"
    assert elements[9].metadata.parent_id == elements[8].id, "ListItem should be child of Title 2"
    assert elements[10].metadata.parent_id == elements[8].id, "ListItem should be child of Title 2"
    assert elements[11].metadata.parent_id == elements[8].id, "Text should be child of Title 2"


def test_set_element_hierarchy_custom_rule_set():
    elements_to_set = [
        Header(text="Header"),  # 0
        Title(text="Title"),  # 1
        NarrativeText(text="NarrativeText"),  # 2
        Text(text="Text"),  # 3
        Title(text="Title 2"),  # 4
        FigureCaption(text="FigureCaption"),  # 5
    ]

    custom_rule_set = {
        "Header": ["Title", "Text"],
        "Title": ["NarrativeText", "UncategorizedText", "FigureCaption"],
    }

    elements = common.set_element_hierarchy(
        elements=elements_to_set,
        ruleset=custom_rule_set,
    )

    assert elements[1].metadata.parent_id == elements[0].id, "Title should be child of Header"
    assert (
        elements[2].metadata.parent_id == elements[1].id
    ), "NarrativeText should be child of Title"
    assert elements[3].metadata.parent_id == elements[1].id, "Text should be child of Title"
    assert elements[4].metadata.parent_id == elements[0].id, "Title 2 should be child of Header"
    assert (
        elements[5].metadata.parent_id == elements[4].id
    ), "FigureCaption should be child of Title 2"


def test_document_to_element_list_sets_category_depth_titles():
    layout_with_hierarchies = MockDocumentLayout()
    elements = document_to_element_list(layout_with_hierarchies)
    assert elements[0].metadata.category_depth == 1
    assert elements[1].metadata.category_depth == 2
    assert elements[2].metadata.category_depth is None
    assert elements[3].metadata.category_depth == 0
