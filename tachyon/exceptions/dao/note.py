from tachyon.exceptions.base import BaseTachyonException


class NoteDAOException(BaseTachyonException):
    """Base exception for internal errors in dao note."""


class NoteDAOSignError(NoteDAOException):
    """Base exception for internal errors with note sign."""


class NoteDAONotFound(NoteDAOException):
    """Base exception for internal errors with note found."""


class NoteDAOEncryptPasswordError(NoteDAOException):
    """Base exception for internal errors with note password."""
