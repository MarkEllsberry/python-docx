# encoding: utf-8

"""Block item container, used by body, cell, header, etc.

Block level items are things like paragraph and table, although there are a few other
specialized ones like structured document tags.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from docx.oxml.table import CT_Tbl
from docx.shared import Parented
from docx.text.paragraph import Paragraph
import sys
import random
from .shared import Parented
from .text import Paragraph
from .list import ListParagraph


class BlockItemContainer(Parented):
    """Base class for proxy objects that can contain block items.

    These containers include _Body, _Cell, header, footer, footnote, endnote, comment,
    and text box objects. Provides the shared functionality to add a block item like
    a paragraph or table.
    """

    def __init__(self, element, parent):
        super(BlockItemContainer, self).__init__(parent)
        self._element = element

    def generate_numId(self):
        """
        Generate a unique numId value on this container.
        """
        while True:
            numId = random.randint(0, 999999)
            if not len(self._element.xpath("//w:numId[@w:val='%s']" % numId)):
                return numId

    def add_paragraph(self, text='', style=None):
        """
        Return a paragraph newly added to the end of the content in this
        container, having *text* in a single run if present, and having
        paragraph style *style*. If *style* is |None|, no paragraph style is
        applied, which has the same effect as applying the 'Normal' style.
        """
        paragraph = self._add_paragraph()
        if text:
            paragraph.add_run(text)
        if style is not None:
            paragraph.style = style
        return paragraph

    def add_table(self, rows, cols, width):
        """
        Return a table of *width* having *rows* rows and *cols* columns,
        newly appended to the content in this container. *width* is evenly
        distributed between the table columns.
        """
        from .table import Table
        tbl = CT_Tbl.new_tbl(rows, cols, width)
        self._element._insert_tbl(tbl)
        return Table(tbl, self)

    def add_list(self, style=None, level=0):
        """
        Return a list paragraph newly added to the end of the content in this
        container, having a paragraph style *style* and an indentation level
        *level*.
        """
        return ListParagraph(
            self,
            numId=self.generate_numId(),
            style=style,
            level=level,
        )

    @property
    def paragraphs(self):
        """
        A list containing the paragraphs in this container, in document
        order. Read-only.
        """
        return [Paragraph(p, self) for p in self._element.p_lst]

    @property
    def lists(self):
        """
        A list containing the paragraphs grouped in lists in this container,
        in document order. Read-only.
        """
        nums = [paragraph.numId for paragraph in self.paragraphs
                if paragraph.numId is not None]
        return [ListParagraph(self, numId) for numId in set(nums)]

    @property
    def tables(self):
        """
        A list containing the tables in this container, in document order.
        Read-only.
        """
        from .table import Table
        return [Table(tbl, self) for tbl in self._element.tbl_lst]

    def _add_paragraph(self):
        """
        Return a paragraph newly added to the end of the content in this
        container.
        """
        return Paragraph(self._element.add_p(), self)
