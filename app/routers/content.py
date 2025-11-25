# Import necessary modules from FastAPI and other parts of the application.
from fastapi import APIRouter, Request, HTTPException, status, Query
# Import List for type hinting a list of responses.
from typing import List
# Import the data models for content creation, response, and updates.
from ..models import ContentCreate, ContentResponse, ContentUpdate
# Import controller functions that handle the business logic.
from ..controllers.content_controller import (
    create_content, get_content, list_contents, update_content, delete_content
)

# Create a new router object with a prefix for all routes in this file and tags for API documentation.
router = APIRouter(prefix="/contents", tags=["contents"])

# Define a route to create new content.
# It responds with the created content and a 201 status code on success.
@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create(request: Request, payload: ContentCreate):
    # Get the database connection from the application state.
    db = request.app.state.db
    # Call the controller function to create the content in the database.
    return await create_content(db, payload)

# Define a route to list all content with pagination support.
# It responds with a list of content.
@router.get("/", response_model=List[ContentResponse])
async def list_all(request: Request, skip: int = Query(0, ge=0), limit: int = Query(50, le=200)):
    # Get the database connection from the application state.
    db = request.app.state.db
    # Call the controller function to retrieve a list of content from the database.
    return await list_contents(db, skip=skip, limit=limit)

# Define a route to get a single piece of content by its ID.
# It responds with the requested content.
@router.get("/{content_id}", response_model=ContentResponse)
async def read(request: Request, content_id: str):
    # Get the database connection from the application state.
    db = request.app.state.db
    # Call the controller function to retrieve the content from the database.
    doc = await get_content(db, content_id)
    # If the content is not found, raise an HTTP 404 error.
    if not doc:
        raise HTTPException(status_code=404, detail="Content not found")
    # Return the found content.
    return doc

# Define a route to update an existing piece of content by its ID.
# It responds with the updated content.
@router.put("/{content_id}", response_model=ContentResponse)
async def update(request: Request, content_id: str, payload: ContentUpdate):
    # Get the database connection from the application state.
    db = request.app.state.db
    # Call the controller function to update the content in the database.
    doc = await update_content(db, content_id, payload)
    # If the content is not found or the ID is invalid, raise an HTTP 404 error.
    if doc is None:
        raise HTTPException(status_code=404, detail="Content not found or invalid id")
    # Return the updated content.
    return doc

# Define a route to delete a piece of content by its ID.
# It responds with a 204 status code on success, indicating no content.
@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(request: Request, content_id: str):
    # Get the database connection from the application state.
    db = request.app.state.db
    # Call the controller function to delete the content from the database.
    ok = await delete_content(db, content_id)
    # If the deletion was unsuccessful (e.g., content not found), raise an HTTP 404 error.
    if not ok:
        raise HTTPException(status_code=404, detail="Content not found")
    # Return None, as there is no content to return.
    return None
