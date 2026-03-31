"""ML training API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies.permissions import require_roles
from app.models.user import User
from app.ml import train_model
from app.ml.model_storage import list_models, get_latest_model_path


router = APIRouter(prefix="/api/ml", tags=["ML"])


class TrainResponse(BaseModel):
    status: str
    model_version: Optional[str] = None
    message: str
    business_types_trained: Optional[int] = None


class ModelInfo(BaseModel):
    filename: str
    trained_at: Optional[str] = None


@router.post("/train", response_model=TrainResponse)
def train_model_endpoint(
    current_user: User = Depends(require_roles("admin")),
) -> TrainResponse:
    """
    Trigger model training.
    
    Only admin users can trigger training.
    This will:
    1. Fetch training data from Supabase
    2. Generate embeddings
    3. Train classifiers
    4. Save versioned model file
    """
    try:
        # Run training
        model_dict = train_model.train_model()
        
        # Extract version info
        model_path = get_latest_model_path()
        model_version = None
        if model_path:
            # Extract version from filename: review_classifier_YYYY-MM-DD_HHMM.pkl
            import os
            filename = os.path.basename(model_path)
            if filename.startswith("review_classifier_"):
                model_version = filename[len("review_classifier_"):-len(".pkl")]
        
        return TrainResponse(
            status="success",
            model_version=model_version,
            message="Model trained and saved successfully",
            business_types_trained=len(model_dict.get("models_by_type", {}))
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {str(e)}"
        )


@router.get("/models", response_model=list[ModelInfo])
def list_model_versions(
    current_user: User = Depends(require_roles("admin", "user")),
) -> list[ModelInfo]:
    """
    List all available model versions.
    
    Admin and user roles can view available models.
    """
    models = list_models()
    
    result = []
    for filename in models:
        # Try to extract trained_at from the model file
        trained_at = None
        try:
            from app.ml.model_storage import load_model_by_version
            version = filename[len("review_classifier_"):-len(".pkl")]
            model_dict = load_model_by_version(version)
            if model_dict and "trained_at" in model_dict:
                trained_at = model_dict["trained_at"]
        except Exception:
            pass
        
        result.append(ModelInfo(
            filename=filename,
            trained_at=trained_at
        ))
    
    return result


@router.get("/models/latest")
def get_latest_model_info(
    current_user: User = Depends(require_roles("admin", "user")),
) -> dict:
    """
    Get information about the latest model.
    """
    model_path = get_latest_model_path()
    
    if not model_path:
        return {
            "available": False,
            "message": "No trained models available"
        }
    
    import os
    filename = os.path.basename(model_path)
    version = filename[len("review_classifier_"):-len(".pkl")]
    
    # Try to get more info from the model file
    trained_at = None
    embedding_model = None
    try:
        from app.ml.model_storage import load_model_by_version
        model_dict = load_model_by_version(version)
        if model_dict:
            trained_at = model_dict.get("trained_at")
            embedding_model = model_dict.get("embedding_model")
    except Exception:
        pass
    
    return {
        "available": True,
        "filename": filename,
        "version": version,
        "trained_at": trained_at,
        "embedding_model": embedding_model
    }


__all__ = ["router"]
