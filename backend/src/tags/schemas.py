import uuid

from pydantic import BaseModel, ConfigDict


class TagResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    name: str

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, TagResponse):
            return self.id == other.id
        return NotImplemented
