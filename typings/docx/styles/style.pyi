from typing import Optional

class BaseStyle:
    @property
    def name(self) -> Optional[str]: ...

class _CharacterStyle(BaseStyle): ...
class _ParagraphStyle(_CharacterStyle): ...
