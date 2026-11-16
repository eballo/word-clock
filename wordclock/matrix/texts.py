from __future__ import annotations

from logging import getLogger

from wordclock.matrix.languages import TEXTS, MatrixLanguage, Texts

logger = getLogger(__name__)

__all__ = ["TEXTS", "Locale", "MatrixLanguage", "Texts"]


class Locale:
    """
    The language the scenes write in, shared by all of them and changed
    live from the remote control.
    """

    def __init__(self, language: MatrixLanguage = MatrixLanguage.catalan) -> None:
        self.language = language

    @property
    def texts(self) -> Texts:
        """The words of the current language."""
        return TEXTS[self.language]

    def set(self, language: MatrixLanguage) -> None:
        """
        Switch the language; the next text of every scene uses it.

        Args:
            language: The new language.
        """
        if language != self.language:
            logger.info("Language: %s", language.value)
        self.language = language
