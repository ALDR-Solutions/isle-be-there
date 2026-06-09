from __future__ import annotations

import logging
import os
import pickle
import threading
import warnings
from typing import Any
from typing import Optional

warnings.filterwarnings("ignore")

from .keyword_classifier import BUSINESS_TYPE_UUIDS

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "ml_models", "unified_pipeline_models.pkl"
)

SUPPORTED_LANGUAGES = ["en", "fr", "es", "nl"]

ML_TIMEOUT_SECONDS = 60

LOCAL_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "ml_models", "all-MiniLM-L6-v2"
)

_models_cache = None
_embedding_model_cache = None
logger = logging.getLogger(__name__)


def _get_numpy():
    try:
        import numpy as np
    except ImportError:
        return None
    return np


def _get_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    return SentenceTransformer


def _get_langdetect_tools():
    try:
        from langdetect import LangDetectException, detect
    except ImportError:
        return None, Exception
    return detect, LangDetectException


def _get_translator_class():
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        return None
    return GoogleTranslator


def _get_embedding_model_with_timeout(
    timeout: int = ML_TIMEOUT_SECONDS,
) -> Optional[Any]:
    global _embedding_model_cache

    if _embedding_model_cache is not None:
        return _embedding_model_cache

    sentence_transformer = _get_sentence_transformer()
    if sentence_transformer is None:
        return None

    result = {"model": None, "error": None}

    def load_model():
        try:
            if os.path.exists(LOCAL_MODEL_PATH):
                result["model"] = sentence_transformer(LOCAL_MODEL_PATH)
            else:
                result["model"] = sentence_transformer("all-MiniLM-L6-v2")
        except Exception as exc:
            result["error"] = exc

    thread = threading.Thread(target=load_model)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        return None

    if result["error"]:
        return None

    _embedding_model_cache = result["model"]
    return _embedding_model_cache


def detect_language(text: str) -> str:
    detect, lang_detect_exception = _get_langdetect_tools()
    if detect is None:
        return "en"
    try:
        if not text or len(text.strip()) < 10:
            return "en"
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGUAGES else "en"
    except lang_detect_exception:
        return "en"
    except Exception:
        return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text

    translator_class = _get_translator_class()
    if translator_class is None:
        return text
    try:
        translator = translator_class(source=source_lang, target="en")
        return translator.translate(text, timeout=5)
    except Exception:
        return text


def translate_if_needed(text: str) -> tuple:
    original_lang = detect_language(text)
    if original_lang != "en":
        translated = translate_to_english(text, original_lang)
        return translated, original_lang
    return text, "en"


def _load_models():
    global _models_cache
    if _models_cache is not None:
        return _models_cache
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        with open(MODEL_PATH, "rb") as f:
            _models_cache = pickle.load(f)
        return _models_cache
    except Exception:
        return None


def _get_embedding_model():
    global _embedding_model_cache
    if _embedding_model_cache is not None:
        return _embedding_model_cache
    return _get_embedding_model_with_timeout(ML_TIMEOUT_SECONDS)


def _fallback_response(
    business_type_id: int,
    business_type: str,
    detected_lang: str,
    *,
    text: str,
    translated_text: str,
    hotel_name: Optional[str],
):
    return {
        "business_type_id": business_type_id,
        "business_type": business_type,
        "hotel_name": hotel_name,
        "detected_language": detected_lang,
        "original_text": text,
        "translated_text": translated_text,
        "main_label": None,
        "second_label": None,
        "third_label": None,
    }


def classify_review(
    text: str,
    business_type_uuid: str,
    hotel_name: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    if business_type_uuid == BUSINESS_TYPE_UUIDS.get("hotel"):
        business_type_id = 1
        business_type = "Hotel"
    elif business_type_uuid == BUSINESS_TYPE_UUIDS.get("restaurant"):
        business_type_id = 2
        business_type = "Restaurant"
    else:
        business_type_id = 0
        business_type = "Unknown"

    translated_text, detected_lang = translate_if_needed(text)

    models_data = _load_models()
    embedding_model = _get_embedding_model_with_timeout(ML_TIMEOUT_SECONDS)

    if models_data is None or embedding_model is None:
        return _fallback_response(
            business_type_id,
            business_type,
            detected_lang,
            text=text,
            translated_text=translated_text,
            hotel_name=hotel_name,
        )

    models_by_type = models_data.get("models_by_type", {})
    model_info = models_by_type.get(business_type_id)

    if model_info is None:
        return _fallback_response(
            business_type_id,
            business_type,
            detected_lang,
            text=text,
            translated_text=translated_text,
            hotel_name=hotel_name,
        )

    clf_main = model_info.get("clf_main")
    mlb_main = model_info.get("mlb_main")
    clf_all = model_info.get("clf_all")
    mlb_all = model_info.get("mlb_all")

    if clf_main is None or mlb_main is None:
        return _fallback_response(
            business_type_id,
            business_type,
            detected_lang,
            text=text,
            translated_text=translated_text,
            hotel_name=hotel_name,
        )

    np = _get_numpy()
    if np is None:
        return _fallback_response(
            business_type_id,
            business_type,
            detected_lang,
            text=text,
            translated_text=translated_text,
            hotel_name=hotel_name,
        )

    embedding = embedding_model.encode([translated_text])

    main_proba = clf_main.predict_proba(embedding)
    main_idx = np.argmax(main_proba[0])
    main_label = mlb_main.classes_[main_idx]

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
        logger.debug(
            "Review classification result: business_type=%s main=%s second=%s third=%s",
            business_type,
            main_label,
            second_label,
            third_label,
        )

    return {
        "business_type_id": business_type_id,
        "business_type": business_type,
        "hotel_name": hotel_name,
        "detected_language": detected_lang,
        "original_text": text,
        "translated_text": translated_text,
        "main_label": main_label,
        "second_label": second_label,
        "third_label": third_label,
    }
