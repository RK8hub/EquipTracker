from typing import Annotated

from pydantic import Field, StringConstraints

NonEmptyStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


SerialString = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=30, pattern=r"^[A-Z0-9-]+$"
    ),
]

Id = Annotated[int, Field(ge=1, description="Positive database ID")]
