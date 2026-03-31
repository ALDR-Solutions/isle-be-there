
import os
from typing import Optional, Dict, Any, List, Tuple

import numpy as np


from sentence_transformers import SentenceTransformer

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'fr', 'es', 'nl']

# Business type UUID mappings (UUID string to internal integer ID)
BUSINESS_TYPES: Dict[str, int] = {
    '390a6943-b75a-465b-a09b-560e7522682c': 1,  # Hotel
    'b155ad8f-91e8-4cee-9384-de3eb498bec5': 2,  # Restaurant
}

# Internal integer to UUID mapping
INT_TO_UUID: Dict[int, str] = {
    1: '390a6943-b75a-465b-a09b-560e7522682c',
    2: 'b155ad8f-91e8-4cee-9384-de3eb498bec5',
}

# Business type names
BUSINESS_TYPE_NAMES: Dict[int, str] = {
    1: "Hotel",
    2: "Restaurant"
}

# Categories by business type UUID
CATEGORIES: Dict[str, List[str]] = {
    '390a6943-b75a-465b-a09b-560e7522682c': [
        "room", "service", "food", "clean", "location", "amenities", "value", "other"
    ],
    'b155ad8f-91e8-4cee-9384-de3eb498bec5': [
        "food_quality", "service_quality", "ambience", "cleanliness", "value_for_money",
        "location_convenience", "wait_time", "hygiene_safety", "dietary_options"
    ]
}


# =============================================================================
# MODEL LOADING (Lazy initialization)
# =============================================================================

# Global model storage
_models: Optional[Dict[str, Any]] = None
_embedding_model: Optional[SentenceTransformer] = None


def load_models() -> Dict[str, Any]:
    """Load ML models from pickle file (lazy loading)."""
    global _models
    
    if _models is None:
        try:
            from app.ml.model_storage import load_latest_model
            from app.core.config import settings
            
            model_path = settings.MODEL_PATH or "models/"
            
            # Try to load latest model using model_storage
            _models = load_latest_model(model_path)
            
            if _models is None:
                _models = {"categories": CATEGORIES}
        except ImportError:
            # Fallback to old behavior if model_storage not available
            try:
                import pickle
                from app.core.config import settings
                
                model_path = settings.MODEL_PATH or "models/"
                model_file = os.path.join(model_path, "unified_pipeline_models.pkl")
                
                _models = {}
                
                if os.path.exists(model_file):
                    with open(model_file, 'rb') as f:
                        _models = pickle.load(f)
                else:
                    _models = {"categories": CATEGORIES}
            except Exception:
                _models = {"categories": CATEGORIES}
    
    if _models is None:
        _models = {"categories": CATEGORIES}
    
    if "categories" not in _models:
        _models["categories"] = CATEGORIES
    
    return _models


def get_embedding(text: str) -> Optional[np.ndarray]:
    """Get embedding vector for text using sentence transformer."""
    global _embedding_model
    
    if _embedding_model is None:
        try:
            from app.core.config import settings
            
            model_name = settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2"
            _embedding_model = SentenceTransformer(model_name)
        except ImportError:
            _embedding_model = None
    
    if _embedding_model is None:
        return None
    
    return _embedding_model.encode([text])[0]


def is_model_loaded() -> bool:
    """Check if models are loaded."""
    return _models is not None or _embedding_model is not None


# =============================================================================
# CATEGORY & BUSINESS TYPE HELPERS
# =============================================================================

def get_categories(business_type_uuid: str) -> List[str]:
    """Get category list for a business type UUID."""
    return CATEGORIES.get(business_type_uuid, [])


def get_business_type_name(business_type_uuid: str) -> str:
    """Get business type name from UUID."""
    internal_id = BUSINESS_TYPES.get(business_type_uuid, 1)
    return BUSINESS_TYPE_NAMES.get(internal_id, "Unknown")


# =============================================================================
# LANGUAGE DETECTION & TRANSLATION
# =============================================================================

def detect_language(text: str) -> str:
    """
    Detect the language of a text.
    
    Args:
        text: Input text to detect language for
        
    Returns:
        Language code (en, fr, es, nl) or 'en' as default
    """
    if not text or len(text.strip()) < 10:
        return 'en'
    
    if not LANGDETECT_AVAILABLE:
        return 'en'
    
    try:
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGUAGES else 'en'
    except LangDetectException:
        return 'en'


def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translate text to English if not already in English.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        
    Returns:
        Translated text in English, or original if translation fails
    """
    if source_lang == 'en' or not text:
        return text
    
    if not DEEP_TRANSLATOR_AVAILABLE:
        return text
    
    try:
        translator = GoogleTranslator(source=source_lang, target='en')
        return translator.translate(text)
    except Exception:
        return text


def translate_if_needed(text: str) -> Tuple[str, str]:
    """
    Translate text to English if needed.
    
    Args:
        text: Text that may need translation
        
    Returns:
        Tuple of (translated_text, original_language)
    """
    original_lang = detect_language(text)
    if original_lang != 'en':
        translated = translate_to_english(text, original_lang)
        return translated, original_lang
    return text, 'en'


# =============================================================================
# MAIN CLASSIFICATION FUNCTION
# =============================================================================

def classify_review(
    text: str, 
    business_type_uuid: str, 
    hotel_name: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Classify a review text based on business type.
    
    Args:
        text: Review text to classify
        business_type_uuid: UUID for business type (Hotel or Restaurant)
        hotel_name: Optional business name
        verbose: Enable verbose output
        
    Returns:
        Dict with classification results including labels and detected language
    """
    # Validate UUID
    if business_type_uuid not in BUSINESS_TYPES:
        return {
            'error': f'Unknown business type UUID: {business_type_uuid}',
            'business_type_id': business_type_uuid
        }
    
    resolved_type = BUSINESS_TYPES[business_type_uuid]
    
    if not text:
        return {
            'error': 'Empty text provided',
            'business_type_id': business_type_uuid
        }
    
    categories = get_categories(business_type_uuid)
    if not categories:
        return {
            'error': f'Unknown business type: {resolved_type}',
            'business_type_id': business_type_uuid
        }
    
    # Translate if needed
    translated_text, detected_lang = translate_if_needed(text)
    text_to_classify = translated_text if detected_lang != 'en' else text
    
    # Check if existing business
    is_existing = True
    if hotel_name:
        is_existing = hotel_name.lower() != 'brand new hotel'
    
    # Load models
    models = load_models()
    
    # Return early if models not trained
    if not models or 'models_by_type' not in models:
        return {
            'business_type_id': business_type_uuid,
            'business_type': get_business_type_name(business_type_uuid),
            'hotel_name': hotel_name or 'Unknown',
            'is_existing_business': is_existing,
            'detected_language': detected_lang,
            'original_text': text,
            'translated_text': translated_text if detected_lang != 'en' else None,
            'main_label': '(none)',
            'second_label': '(none)',
            'third_label': '(none)',
            'note': 'Models not yet trained'
        }
    
    # Get model for business type
    models_by_type = models.get('models_by_type', {})
    
    if resolved_type not in models_by_type:
        return {'error': f'No model for business type: {resolved_type}', 'business_type_id': business_type_uuid}
    
    model_data = models_by_type[resolved_type]
    clf_main = model_data.get('clf_main')
    mlb_main = model_data.get('mlb_main')
    clf_all = model_data.get('clf_all')
    mlb_all = model_data.get('mlb_all')
    
    # Get embedding
    emb = get_embedding(text_to_classify)
    
    if emb is None:
        return {'error': 'Failed to generate embedding', 'business_type_id': business_type_uuid}
    
    # Predict main label
    if clf_main is not None and mlb_main is not None:
        main_proba = clf_main.predict_proba(emb.reshape(1, -1))
        main_idx = np.argmax(main_proba[0])
        main_label = mlb_main.classes_[main_idx]
    else:
        main_label = categories[0] if categories else '(none)'
    
    # Get secondary labels
    secondary_labels = []
    if clf_all is not None and mlb_all is not None:
        all_scores = clf_all.decision_function(emb.reshape(1, -1))
        sorted_indices = np.argsort(all_scores[0])[::-1]
        for idx in sorted_indices:
            label = mlb_all.classes_[idx]
            if label != main_label and len(secondary_labels) < 2:
                secondary_labels.append(label)
    
    return {
        'business_type_id': business_type_uuid,
        'business_type': get_business_type_name(business_type_uuid),
        'hotel_name': hotel_name or 'Unknown',
        'is_existing_business': is_existing,
        'detected_language': detected_lang,
        'original_text': text,
        'translated_text': translated_text if detected_lang != 'en' else None,
        'main_label': main_label,
        'second_label': secondary_labels[0] if len(secondary_labels) > 0 else '(none)',
        'third_label': secondary_labels[1] if len(secondary_labels) > 1 else '(none)'
    }
