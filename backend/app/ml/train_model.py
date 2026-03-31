"""
ML Training Script - Train review classifiers from Supabase data.

Usage:
    python -m app.ml.train_model

This script:
1. Fetches training data from Supabase ml_training_reviews table
2. Generates embeddings using all-MiniLM-L6-v2
3. Trains scikit-learn classifiers
4. Saves versioned model file
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# =============================================================================
# CONSTANTS
# =============================================================================

# Business type UUIDs (matching review_classifier.py)
BUSINESS_TYPE_UUIDS = {
    '390a6943-b75a-465b-a09b-560e7522682c': 1,  # Hotel
    'b155ad8f-91e8-4cee-9384-de3eb498bec5': 2,  # Restaurant
}

# Reverse mapping
UUID_FROM_ID = {v: k for k, v in BUSINESS_TYPE_UUIDS.items()}

# Categories per business type
CATEGORIES = {
    '390a6943-b75a-465b-a09b-560e7522682c': [
        "room", "service", "food", "clean", "location", "amenities", "value", "other"
    ],
    'b155ad8f-91e8-4cee-9384-de3eb498bec5': [
        "food_quality", "service_quality", "ambience", "cleanliness",
        "value_for_money", "location_convenience", "wait_time",
        "hygiene_safety", "dietary_options"
    ]
}


# =============================================================================
# SUPABASE CONNECTION
# =============================================================================

def get_supabase_client():
    """Create Supabase client from environment variables."""
    from supabase import create_client
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    
    return create_client(supabase_url, supabase_key)


def fetch_training_data(supabase) -> Dict[str, List[Dict]]:
    """Fetch training data from Supabase, grouped by business type."""
    print("Fetching training data from Supabase...")
    
    response = supabase.table('ml_training_reviews').select(
        'review_text, main_label, second_label, third_label, business_type_uuid'
    ).execute()
    
    records = response.data
    
    # Filter out records without main_label and group by business type
    grouped: Dict[str, List[Dict]] = {uuid: [] for uuid in BUSINESS_TYPE_UUIDS.keys()}
    
    valid_count = 0
    for record in records:
        if not record.get('main_label'):
            continue
        
        business_uuid = record.get('business_type_uuid')
        if business_uuid not in grouped:
            continue
        
        # Collect all labels for this record
        labels = [record['main_label']]
        if record.get('second_label'):
            labels.append(record['second_label'])
        if record.get('third_label'):
            labels.append(record['third_label'])
        
        grouped[business_uuid].append({
            'text': record['review_text'],
            'labels': labels,
            'main_label': record['main_label']
        })
        valid_count += 1
    
    print(f"  Fetched {valid_count} valid records")
    for uuid, items in grouped.items():
        print(f"    {uuid[:8]}...: {len(items)} records")
    
    return grouped


# =============================================================================
# EMBEDDING GENERATION
# =============================================================================

def generate_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Generate embeddings for a list of texts."""
    from sentence_transformers import SentenceTransformer
    
    print(f"  Generating embeddings for {len(texts)} texts...")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    return embeddings


# =============================================================================
# MODEL TRAINING
# =============================================================================

def train_classifiers(
    texts: List[str],
    all_labels: List[List[str]],
    main_labels: List[str],
    categories: List[str]
) -> Tuple[Any, Any, Any, Any]:
    """Train classifiers for a business type."""
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import MultiLabelBinarizer
    
    # Generate embeddings
    embeddings = generate_embeddings(texts)
    
    # Train main label classifier (single label)
    mlb_main = MultiLabelBinarizer(classes=categories)
    y_main = mlb_main.fit_transform([[l] for l in main_labels])
    
    clf_main = OneVsRestClassifier(LogisticRegression(max_iter=1000, random_state=42))
    clf_main.fit(embeddings, y_main)
    
    # Train multi-label classifier (all labels)
    mlb_all = MultiLabelBinarizer(classes=categories)
    y_all = mlb_all.fit_transform(all_labels)
    
    clf_all = OneVsRestClassifier(LogisticRegression(max_iter=1000, random_state=42))
    clf_all.fit(embeddings, y_all)
    
    return clf_main, mlb_main, clf_all, mlb_all


# =============================================================================
# MODEL SAVING
# =============================================================================

def save_model(models_dict: Dict[str, Any], base_path: str = "models/") -> str:
    """Save model with timestamp version."""
    import pickle
    from datetime import datetime
    
    # Create models directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)
    
    # Generate timestamp (no seconds)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"review_classifier_{timestamp}.pkl"
    filepath = os.path.join(base_path, filename)
    
    # Save model
    with open(filepath, 'wb') as f:
        pickle.dump(models_dict, f)
    
    print(f"  Model saved to: {filepath}")
    return filepath


# =============================================================================
# MAIN TRAINING FUNCTION
# =============================================================================

def train_model() -> Dict[str, Any]:
    """Main training function."""
    print("=" * 60)
    print("ML Training Pipeline")
    print("=" * 60)
    
    # Connect to Supabase
    supabase = get_supabase_client()
    
    # Fetch training data
    grouped_data = fetch_training_data(supabase)
    
    # Initialize model structure
    models_by_type = {}
    
    # Train classifiers for each business type
    for business_uuid, records in grouped_data.items():
        if not records:
            print(f"\nSkipping {business_uuid[:8]}... - no valid records")
            continue
        
        internal_id = BUSINESS_TYPE_UUIDS[business_uuid]
        categories = CATEGORIES[business_uuid]
        
        print(f"\nTraining model for {business_uuid[:8]}... (internal_id={internal_id})")
        print(f"  Categories: {categories}")
        
        # Extract texts and labels
        texts = [r['text'] for r in records]
        all_labels = [r['labels'] for r in records]
        main_labels = [r['main_label'] for r in records]
        
        # Train classifiers
        clf_main, mlb_main, clf_all, mlb_all = train_classifiers(
            texts, all_labels, main_labels, categories
        )
        
        models_by_type[internal_id] = {
            'clf_main': clf_main,
            'mlb_main': mlb_main,
            'clf_all': clf_all,
            'mlb_all': mlb_all
        }
    
    # Create final model dict
    model_dict = {
        'models_by_type': models_by_type,
        'categories': CATEGORIES,
        'trained_at': datetime.now().isoformat(),
        'embedding_model': 'all-MiniLM-L6-v2'
    }
    
    # Save model
    print("\n" + "=" * 60)
    print("Saving model...")
    filepath = save_model(model_dict)
    
    print("\n✓ Training complete!")
    print(f"  Model file: {filepath}")
    print(f"  Business types trained: {len(models_by_type)}")
    
    return model_dict


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    try:
        train_model()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
