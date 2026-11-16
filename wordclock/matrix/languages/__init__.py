"""
Languages of the mini matrix texts, one module per language.

To add a language: create ``<language>.py`` here with a ``TEXTS`` of
:class:`Texts`, then add it to :class:`MatrixLanguage` and :data:`TEXTS`.
These are the matrix languages only; the word clock faces have their own
in :mod:`wordclock.layouts.registry`.
"""

from __future__ import annotations

from enum import StrEnum

from wordclock.matrix.languages import catalan, dutch, english, spanish
from wordclock.matrix.languages.base import Texts


class MatrixLanguage(StrEnum):
    catalan = "catalan"
    english = "english"
    spanish = "spanish"
    dutch = "dutch"


TEXTS: dict[MatrixLanguage, Texts] = {
    MatrixLanguage.catalan: catalan.TEXTS,
    MatrixLanguage.english: english.TEXTS,
    MatrixLanguage.spanish: spanish.TEXTS,
    MatrixLanguage.dutch: dutch.TEXTS,
}

__all__ = ["TEXTS", "MatrixLanguage", "Texts"]
