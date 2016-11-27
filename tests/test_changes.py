import pytest

from ctxt.shared_document.changes import *


@pytest.fixture
def text():
	return "Lorem ipsum dolor sit amet, \nconsectetur adipiscing elit."


def test_apply_insert(text):
	insert = Insert(0, "abc")
	new_txt = insert.apply(text)
	assert new_txt.startswith("abcLorem")

	insert = Insert(len(text), "abc")
	new_txt = insert.apply(text)
	assert new_txt.endswith("elit.abc")

	insert = Insert(text.find("amet"), "abc")
	new_txt = insert.apply(text)
	assert "abcamet" in new_txt

	with pytest.raises(AssertionError):
		insert = Insert(-1, "abc")
		new_txt = insert.apply(text)

	with pytest.raises(AssertionError):
		insert = Insert(len(text) + 1, "abc")
		new_txt = insert.apply(text)


def test_apply_delete(text):
	delete = Delete(0, 5)
	new_txt = delete.apply(text)
	assert new_txt.startswith(text[6:])

	delete = Delete(0, len(text) - 1)
	new_txt = delete.apply(text)
	assert len(new_txt) == 0

	delete = Delete(3, len(text) - 3)
	new_txt = delete.apply(text)
	assert new_txt == "Lort."

	with pytest.raises(AssertionError):
		delete = Delete(-1, 5)
		new_txt = delete.apply(text)

	with pytest.raises(AssertionError):
		delete = Delete(2, len(text))
		new_txt = delete.apply(text)

