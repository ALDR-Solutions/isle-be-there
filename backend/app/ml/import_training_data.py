# Data import script - Import training data from CSV  to Supabase has hotel and restaurant review data needs for other 3 
"""
Usage:
    python import_training_data.py [--csv-path PATH] [--batch-size N]

This script imports labeled review data from CSV into Supabase ml_training_reviews table.
"""
import os 
import sys
import csv
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv; load_dotenv()



def parse_labels(label_str: str) -> List[str]:
    """Parse labels from string representation."""
    if not label_str or label_str in ['nan', 'None', '(none)']:
        return []
    
    label_str = str(label_str).strip()
    
    if label_str.startswith('[') and label_str.endswith(']'):
        try:
            import ast
            parsed = ast.literal_eval(label_str)
            if isinstance(parsed, list):
                return [str(l).strip() for l in parsed if l and str(l).strip() not in ['none', '(none)', 'None', '']]
        except:
            pass
    
    return [label_str] if label_str and label_str not in ['none', '(none)', 'None', ''] else []


def import_csv_to_supabase(csv_path: str, batch_size: int = 500):
    """Import CSV data to Supabase."""
    try:
        from supabase import create_client
    except ImportError:
        print("ERROR: supabase-py not installed. Run: pip install supabase")
        return 0
    
    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY environment variables not set")
        return 0
    
    client = create_client(supabase_url, supabase_key)
    
    # Find the CSV file
    if not os.path.exists(csv_path):
        # Try default locations
        default_paths = [
            'C:/Users/raeda/OneDrive/Desktop/hotel-reviews/data/all_reviews_labelled.csv',
            'data/all_reviews_labelled.csv',
            '../hotel-reviews/data/all_reviews_labelled.csv',
        ]
        for path in default_paths:
            if os.path.exists(path):
                csv_path = path
                break
        else:
            print(f"ERROR: CSV file not found at {csv_path}")
            return 0
    
    print(f"Reading CSV from: {csv_path}")
    
    total_imported = 0
    batch: List[Dict[str, Any]] = []
    
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        
        # Determine column names
        text_col = 'cleaned' if 'cleaned' in reader.fieldnames else 'reviews.text'
        label_col = 'auto_labels'
        
        for i, row in enumerate(reader):
            try:
                review_text = row.get(text_col, '').strip()
                if not review_text or review_text in ['nan', 'None']:
                    continue
                
                labels = parse_labels(row.get(label_col, ''))
                
                # Get business type
                business_type_id = int(row.get('business_type_id', 1))
                
                # Create record
                record = {
                    'business_type_id': business_type_id,
                    'review_text': review_text,
                    'main_label': labels[0] if len(labels) > 0 else None,
                    'second_label': labels[1] if len(labels) > 1 else None,
                    'third_label': labels[2] if len(labels) > 2 else None,
                    'detected_language': 'en',  # Default, can be enhanced
                    'is_hand_labelled': bool(row.get('is_hand_labelled', '0') == '1')
                }
                
                batch.append(record)
                
                # Insert batch when full
                if len(batch) >= batch_size:
                    try:
                        client.table('ml_training_reviews').insert(batch).execute()
                        total_imported += len(batch)
                        print(f"  Imported {total_imported} records...")
                    except Exception as e:
                        print(f"  Batch insert error: {e}")
                    batch = []
                    
            except Exception as e:
                print(f"  Row {i} error: {e}")
                continue
    
    # Insert remaining records
    if batch:
        try:
            client.table('ml_training_reviews').insert(batch).execute()
            total_imported += len(batch)
        except Exception as e:
            print(f"  Final batch insert error: {e}")
    
    return total_imported


def main():
    parser = argparse.ArgumentParser(description='Import training data to Supabase')
    parser.add_argument('--csv-path', default='', help='Path to CSV file')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for inserts')
    
    args = parser.parse_args()
    
    csv_path = args.csv_path or 'data/all_reviews_labelled.csv'
    count = import_csv_to_supabase(csv_path, args.batch_size)
    
    print(f"\nTotal records imported: {count}")


if __name__ == '__main__':
    main()