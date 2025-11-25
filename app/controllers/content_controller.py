# controllers/content_controller.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from ..models import ContentCreate, ContentUpdate

def doc_to_response(doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Converts a MongoDB document to a dictionary, renaming '_id' to 'id'."""
    if doc is None:
        return None
    result = doc.copy()
    _id = result.pop('_id', None)
    result['id'] = str(_id) if _id else None
    return result

async def create_content(db, data: ContentCreate) -> dict:
    payload = data.dict()
    now = datetime.utcnow()
    payload["created_at"] = now
    payload["updated_at"] = now
    res = await db.contents.insert_one(payload)
    doc = await db.contents.find_one({"_id": res.inserted_id})
    return doc_to_response(doc)

async def get_content(db, content_id: str) -> Optional[dict]:
    if not ObjectId.is_valid(content_id):
        return None
    doc = await db.contents.find_one({"_id": ObjectId(content_id)})
    return doc_to_response(doc)

async def list_contents(db, skip: int = 0, limit: int = 50) -> List[dict]:
    cursor = db.contents.find().skip(skip).limit(limit).sort("created_at", -1)
    result = []
    async for doc in cursor:
        result.append(doc_to_response(doc))
    return result

async def update_content(db, content_id: str, data: ContentUpdate) -> Optional[dict]:
    if not ObjectId.is_valid(content_id):
        return None
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        return await get_content(db, content_id)
    update_data["updated_at"] = datetime.utcnow()
    res = await db.contents.find_one_and_update(
        {"_id": ObjectId(content_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return doc_to_response(res)

async def delete_content(db, content_id: str) -> bool:
    if not ObjectId.is_valid(content_id):
        return False
    res = await db.contents.delete_one({"_id": ObjectId(content_id)})
    return res.deleted_count == 1