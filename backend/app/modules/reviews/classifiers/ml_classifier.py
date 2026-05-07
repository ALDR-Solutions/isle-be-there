import os
import pickle
import warnings
warnings.filterwarnings('ignore')

from typing import Optional, Tuple

import numpy as np

# ML imports
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer

# Language detection and translation
try:
    from langdetect import detect, LangDetectException
except ImportError:
    detect = None
    LangDetectException = Exception

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

# Import UUIDs from keyword_classifier
from .keyword_classifier import BUSINESS_TYPE_UUIDS

# Model path - relative to this file
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'unified_pipeline_models.pkl')

SUPPORTED_LANGUAGES = ['en', 'fr', 'es', 'nl']

# Cache
_models_cache = None
_embedding_model_cache = None

def detect_language(text: str) -> str:
    """Detect the language of a text."""
    if detect is None:
        return 'en'
    try:
        if not text or len(text.strip()) < 10:
            return 'en'
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGUAGES else 'en'
    except LangDetectException:
        return 'en'
    except Exception:
        return 'en'

def translate_to_english(text: str, source_lang: str) -> str:
    """Translate text to English if not already in English."""
    if source_lang == 'en':
        return text
    if GoogleTranslator is None:
        return text
    try:
        translator = GoogleTranslator(source=source_lang, target='en')
        return translator.translate(text)
    except Exception:
        return text

def translate_if_needed(text: str) -> tuple:
    """Translate text to English if needed. Returns (translated_text, original_lang)."""
    original_lang = detect_language(text)
    if original_lang != 'en':
        translated = translate_to_english(text, original_lang)
        return translated, original_lang
    return text, 'en'

def _load_models():
    """Load classification models from pickle file."""
    global _models_cache
    if _models_cache is not None:
        return _models_cache
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            _models_cache = pickle.load(f)
        return _models_cache
    except Exception:
        return None

def _get_embedding_model():
    """Get or initialize the SentenceTransformer embedding model."""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        if SentenceTransformer is None:
            return None
        _embedding_model_cache = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model_cache

def classify_review(
    text: str,
    business_type_uuid: str,
    hotel_name: Optional[str] = None,
    verbose: bool = False
) -> dict:
    """
    Classify a review using ML models.
    
    Args:
        text: The review text to classify.
        business_type_uuid: UUID identifying the business type (Hotel or Restaurant).
        hotel_name: Optional hotel name for existing hotel check.
        verbose: If True, print additional debug info.
        
    Returns:
        Dictionary containing classification results with keys:
        - business_type_id: 1 for Hotel, 2 for Restaurant
        - business_type: 'Hotel' or 'Restaurant'
        - hotel_name: provided hotel name
        - is_existing_hotel: whether this is an existing hotel
        - detected_language: detected language code
        - original_text: original review text
        - translated_text: translated review text (if applicable)
        - main_label: primary category label
        - second_label: secondary category label
        - third_label: tertiary category label
    """
    # Map UUID to business type
    if business_type_uuid == BUSINESS_TYPE_UUIDS.get('hotel'):
        business_type_id = 1
        business_type = 'Hotel'
    elif business_type_uuid == BUSINESS_TYPE_UUIDS.get('restaurant'):
        business_type_id = 2
        business_type = 'Restaurant'
    else:
        business_type_id = 0
        business_type = 'Unknown'
    
    # Detect language and translate if needed
    translated_text, detected_lang = translate_if_needed(text)
    
    # Check if existing hotel
    is_existing_hotel = hotel_name is not None and hotel_name != ''
    
    # Load models
    models_data = _load_models()
    embedding_model = _get_embedding_model()
    
    if models_data is None or embedding_model is None:
        return {
            'business_type_id': business_type_id,
            'business_type': business_type,
            'hotel_name': hotel_name,
            'is_existing_hotel': is_existing_hotel,
            'detected_language': detected_lang,
            'original_text': text,
            'translated_text': translated_text,
            'main_label': None,
            'second_label': None,
            'third_label': None
        }
    
    # Get models_by_type for this business type
    models_by_type = models_data.get('models_by_type', {})
    model_info = models_by_type.get(business_type_id)
    
    if model_info is None:
        return {
            'business_type_id': business_type_id,
            'business_type': business_type,
            'hotel_name': hotel_name,
            'is_existing_hotel': is_existing_hotel,
            'detected_language': detected_lang,
            'original_text': text,
            'translated_text': translated_text,
            'main_label': None,
            'second_label': None,
            'third_label': None
        }
    
    # Get the classifiers and binarizers
    clf_main = model_info.get('clf_main')
    mlb_main = model_info.get('mlb_main')
    clf_all = model_info.get('clf_all')
    mlb_all = model_info.get('mlb_all')
    
    if clf_main is None or mlb_main is None:
        return {
            'business_type_id': business_type_id,
            'business_type': business_type,
            'hotel_name': hotel_name,
            'is_existing_hotel': is_existing_hotel,
            'detected_language': detected_lang,
            'original_text': text,
            'translated_text': translated_text,
            'main_label': None,
            'second_label': None,
            'third_label': None
        }
    
    # Generate embedding
    embedding = embedding_model.encode([translated_text])
    
    # Predict main label using clf_main and mlb_main
    main_proba = clf_main.predict_proba(embedding)
    main_idx = np.argmax(main_proba[0])
    main_label = mlb_main.classes_[main_idx]
    
    # Get secondary labels using clf_all and mlb_all
    if clf_all is not None and mlb_all is not None:
        all_scores = clf_all.decision_function(embedding)
        sorted_indices = np.argsort(all_scores[0])[::-1]
        
        secondary_labels = []
        for idx in sorted_indices:
            label = mlb_all.classes_[idx]
            if label != main_label and len(secondary_labels) < 2:
                secondary_labels.append(label)
    else:
        secondary_labels = []
    
    second_label = secondary_labels[0] if len(secondary_labels) > 0 else None
    third_label = secondary_labels[1] if len(secondary_labels) > 1 else None
    
    if verbose:
        print(f"Business Type: {business_type}")
        print(f"Main Label: {main_label}")
        print(f"Second Label: {second_label}")
        print(f"Third Label: {third_label}")
    
    return {
        'business_type_id': business_type_id,
        'business_type': business_type,
        'hotel_name': hotel_name,
        'is_existing_hotel': is_existing_hotel,
        'detected_language': detected_lang,
        'original_text': text,
        'translated_text': translated_text,
        'main_label': main_label,
        'second_label': second_label,
        'third_label': third_label
    }