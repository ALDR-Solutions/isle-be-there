"""
Model storage utilities for versioned model files.

Provides functions to:
- save_model(): Save model with timestamp
- load_latest_model(): Load most recent model
- list_models(): List all available model versions
"""

import os
import pickle
from datetime import datetime
from typing import Dict, Any, List, Optional


MODEL_PREFIX = "review_classifier_"
MODEL_EXTENSION = ".pkl"


def save_model(models_dict: Dict[str, Any], base_path: str = "models/") -> str:
    """
    Save model with timestamp version.
    
    Args:
        models_dict: The model dictionary to save
        base_path: Directory to save models in
        
    Returns:
        The filepath where the model was saved
    """
    os.makedirs(base_path, exist_ok=True)
    
    # Generate timestamp (no seconds to reduce uniqueness)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"{MODEL_PREFIX}{timestamp}{MODEL_EXTENSION}"
    filepath = os.path.join(base_path, filename)
    
    with open(filepath, 'wb') as f:
        pickle.dump(models_dict, f)
    
    return filepath


def load_latest_model(base_path: str = "models/") -> Optional[Dict[str, Any]]:
    """
    Load the most recent model file.
    
    Args:
        base_path: Directory containing model files
        
    Returns:
        The model dictionary, or None if no models exist
    """
    model_files = list_models(base_path)
    
    if not model_files:
        return None
    
    # Get the most recent file (sorted by modification time)
    latest_file = model_files[-1]
    filepath = os.path.join(base_path, latest_file)
    
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def load_model_by_version(version: str, base_path: str = "models/") -> Optional[Dict[str, Any]]:
    """
    Load a specific model version.
    
    Args:
        version: The version string (e.g., "2026-03-26_1430")
        base_path: Directory containing model files
        
    Returns:
        The model dictionary, or None if not found
    """
    filename = f"{MODEL_PREFIX}{version}{MODEL_EXTENSION}"
    filepath = os.path.join(base_path, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def list_models(base_path: str = "models/") -> List[str]:
    """
    List all available model versions.
    
    Args:
        base_path: Directory containing model files
        
    Returns:
        List of model filenames, sorted by modification time (oldest first)
    """
    if not os.path.exists(base_path):
        return []
    
    model_files = [
        f for f in os.listdir(base_path)
        if f.startswith(MODEL_PREFIX) and f.endswith(MODEL_EXTENSION)
    ]
    
    # Sort by modification time (oldest first)
    model_files.sort(key=lambda f: os.path.getmtime(os.path.join(base_path, f)))
    
    return model_files


def get_latest_model_path(base_path: str = "models/") -> Optional[str]:
    """
    Get the filepath of the most recent model.
    
    Args:
        base_path: Directory containing model files
        
    Returns:
        Full filepath, or None if no models exist
    """
    model_files = list_models(base_path)
    
    if not model_files:
        return None
    
    latest_file = model_files[-1]
    return os.path.join(base_path, latest_file)


def delete_model(version: str, base_path: str = "models/") -> bool:
    """
    Delete a specific model version.
    
    Args:
        version: The version string to delete
        base_path: Directory containing model files
        
    Returns:
        True if deleted, False if not found
    """
    filename = f"{MODEL_PREFIX}{version}{MODEL_EXTENSION}"
    filepath = os.path.join(base_path, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    
    return False
