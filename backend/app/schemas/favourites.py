from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.listing import ListingResponse

class FavouriteResponse(BaseModel):
    id: UUID
    user_id: UUID
    listing_id: UUID
    created_at: datetime
    listing: ListingResponse
    model_config = {"from_attributes": True}