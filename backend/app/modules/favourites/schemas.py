from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.listings.schemas import ListingResponse


class FavouriteResponse(BaseModel):
    id: UUID
    user_id: UUID
    listing_id: UUID
    created_at: datetime
    listing: ListingResponse

    model_config = {"from_attributes": True}
