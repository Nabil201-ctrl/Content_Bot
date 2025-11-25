from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContentResponse(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentCreate(BaseModel):
    title: str = Field(..., max_length=100)
    body: str = Field(..., max_length=5000)


class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    body: Optional[str] = Field(None, max_length=5000)
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContentResponse(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentCreate(BaseModel):
    title: str = Field(..., max_length=100)
    body: str = Field(..., max_length=5000)


class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    body: Optional[str] = Field(None, max_length=5000)
# Import BaseModel and Field from pydantic for data validation and settings management.
from pydantic import BaseModel, Field
# Import Optional for defining optional fields.
from typing import Optional
# Import datetime for handling date and time.
from datetime import datetime

# Defines the response model for content, specifying the structure of the data returned by the API.
class ContentResponse(BaseModel):
    # Unique identifier for the content.
    id: str
    # Title of the content.
    title: str
    # Body of the content.
    body: str
    # Timestamp when the content was created.
    created_at: datetime
    # Timestamp when the content was last updated, can be None if never updated.
    updated_at: Optional[datetime] = None

# Defines the input model for creating content, used for request body validation.
class ContentCreate(BaseModel):
    # Title of the content, required field with a maximum length of 100 characters.
    title: str = Field(..., max_length=100)
    # Body of the content, required field with a maximum length of 5000 characters.
    body: str = Field(..., max_length=5000)

# Defines the model for updating content, allowing for partial updates.
class ContentUpdate(BaseModel):
    # Optional new title for the content, with a maximum length of 100 characters.
    title: Optional[str] = Field(None, max_length=100)
    # Optional new body for the content, with a maximum length of 5000 characters.
    body: Optional[str] = Field(None, max_length=5000)
