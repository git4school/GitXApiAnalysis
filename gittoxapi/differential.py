from tincan.serializable_base import SerializableBase

"""

.. module:: DiffPart
   :synopsis: The DiffPart class that contains properties to define a modification of a file

"""


class DiffPart(SerializableBase):
    _props = [
        "a_start_line",
        "a_interval",
        "b_start_line",
        "b_interval",
        "content",
    ]

    def __init__(self, *args, **kwargs):
        self._a_start_line = None
        self._a_interval = None
        self._b_start_line = None
        self._b_interval = None
        self._content = None

        super(DiffPart, self).__init__(*args, **kwargs)

    @property
    def a_start_line(self):
        """A start line for DiffPart

        :setter: Tries to convert to int
        :setter type: int
        :rtype: int

        """
        return self._a_start_line

    @a_start_line.setter
    def a_start_line(self, value):
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Property a_start_line must be an integer")
        self._a_start_line = value

    @a_start_line.deleter
    def a_start_line(self):
        del self._a_start_line

    @property
    def a_interval(self):
        """A interval for DiffPart

        :setter: Tries to convert to int
        :setter type: int
        :rtype: int

        """
        return self._a_interval

    @a_interval.setter
    def a_interval(self, value):
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Property a_interval must be an integer")
        self._a_interval = value

    @a_interval.deleter
    def a_interval(self):
        del self._a_interval

    @property
    def b_start_line(self):
        """B start line for DiffPart

        :setter: Tries to convert to int
        :setter type: int
        :rtype: int

        """
        return self._b_start_line

    @b_start_line.setter
    def b_start_line(self, value):
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Property b_start_line must be an integer")
        self._b_start_line = value

    @b_start_line.deleter
    def b_start_line(self):
        del self._b_start_line

    @property
    def b_interval(self):
        """B interval for DiffPart

        :setter: Tries to convert to int
        :setter type: int
        :rtype: int

        """
        return self._b_interval

    @b_interval.setter
    def b_interval(self, value):
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("Property b_interval must be an integer")
        self._b_interval = value

    @b_interval.deleter
    def b_interval(self):
        del self._b_interval

    @property
    def content(self):
        """Content for DiffPart

        :setter: Tries to convert to list of str
        :setter type: list of str
        :rtype: list of str

        """
        return self._content

    @content.setter
    def content(self, value):
        if value is not None:
            if not isinstance(value, list) or not all(
                isinstance(v, str) for v in value
            ):
                raise ValueError("Property content must be a list of strings")
        self._content = value

    @content.deleter
    def content(self):
        del self._content


"""

.. module:: Differential
   :synopsis: The Differential class that contains properties to define a difference between two git revisions

"""


class Differential(SerializableBase):
    _props_req = [
        "object_type",
        "file",
    ]

    _props = [
        "deleted",
        "added",
        "copied",
        "renamed_from",
        "renamed_to",
        "parts",
    ]

    _props.extend(_props_req)

    def __init__(self, *args, **kwargs):
        self._object_type = None
        self._file = None
        self._deleted = None
        self._added = None
        self._copied = None
        self._renamed_from = None
        self._renamed_to = None
        self._parts = None

        super(Differential, self).__init__(*args, **kwargs)

    @property
    def object_type(self):
        """Object Type for Differential. Will always be 'Differential'

        :setter: Tries to convert to unicode
        :setter type: unicode
        :rtype: unicode

        """
        return self._object_type

    @object_type.setter
    def object_type(self, _):
        self._object_type = "Differential"

    @property
    def file(self):
        """File for Differential

        :setter: Tries to convert to str
        :setter type: str
        :rtype: str

        """
        return self._file

    @file.setter
    def file(self, value):
        if value is not None:
            if not isinstance(value, str):
                value = str(value)
        self._file = value

    @file.deleter
    def file(self):
        del self._file

    @property
    def deleted(self):
        """Deleted for Differential

        :setter: Tries to convert to bool
        :setter type: bool
        :rtype: bool

        """
        return self._deleted

    @deleted.setter
    def deleted(self, value):
        if value is not None:
            if not isinstance(value, bool):
                raise ValueError("Property deleted must be a boolean")
        self._deleted = value

    @deleted.deleter
    def deleted(self):
        del self._deleted

    @property
    def added(self):
        """Added for Differential

        :setter: Tries to convert to bool
        :setter type: bool
        :rtype: bool

        """
        return self._added

    @added.setter
    def added(self, value):
        if value is not None:
            if not isinstance(value, bool):
                raise ValueError("Property added must be a boolean")
        self._added = value

    @added.deleter
    def added(self):
        del self._added

    @property
    def copied(self):
        """Copied for Differential

        :setter: Expects a list of two strings
        :setter type: list of str
        :rtype: list of str

        """
        return self._copied

    @copied.setter
    def copied(self, value):
        if value is not None:
            if (
                not isinstance(value, list)
                or len(value) != 2
                or not all(isinstance(v, str) for v in value)
            ):
                raise ValueError("Property copied must be a list of two strings")
        self._copied = value

    @copied.deleter
    def copied(self):
        del self._copied

    @property
    def renamed_from(self):
        """Renamed from for Differential

        :setter: Tries to convert to str
        :setter type: str
        :rtype: str

        """
        return self._renamed_from

    @renamed_from.setter
    def renamed_from(self, value):
        if value is not None:
            if not isinstance(value, str):
                value = str(value)
        self._renamed_from = value

    @renamed_from.deleter
    def renamed_from(self):
        del self._renamed_from

    @property
    def renamed_to(self):
        """Renamed to for Differential

        :setter: Tries to convert to str
        :setter type: str
        :rtype: str

        """
        return self._renamed_to

    @renamed_to.setter
    def renamed_to(self, value):
        if value is not None:
            if not isinstance(value, str):
                value = str(value)
        self._renamed_to = value

    @renamed_to.deleter
    def renamed_to(self):
        del self._renamed_to

    @property
    def parts(self):
        """Parts for Differential

        :setter: Expects a DiffPart object
        :setter type: DiffPart
        :rtype: DiffPart

        """
        return self._parts

    @parts.setter
    def parts(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError("Property parts must be a list of DiffPart instances")
            if not all(isinstance(item, DiffPart) for item in value):
                value = [DiffPart(e) for e in value]
        self._parts = value

    @parts.deleter
    def parts(self):
        del self._parts
