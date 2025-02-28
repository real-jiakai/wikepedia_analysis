#!/usr/bin/env python3
"""
Script to analyze word frequencies across Wikipedia pages in a specified category.
"""

import argparse
import requests
import re
import sys
import os
import json
from collections import Counter
import nltk
from nltk.corpus import stopwords
import time
import hashlib

# Download necessary NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Create cache directory if it doesn't exist
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(category):
    """Generate a cache file path for a category."""
    # Create a unique filename based on the category name
    hashed = hashlib.md5(category.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{category.replace(' ', '_')}_{hashed}.json")

def load_from_cache(category):
    """Load cached results for a category if available."""
    cache_path = get_cache_path(category)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                # Convert strings back to integers for the Counter
                word_counts = Counter({k: int(v) for k, v in cache_data.items()})
                print(f"Loaded cached results for category: {category}")
                return word_counts
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading cache: {e}")
    return None

def save_to_cache(category, word_counts):
    """Save results to cache."""
    cache_path = get_cache_path(category)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            # Convert Counter to dictionary for JSON serialization
            json.dump(dict(word_counts), f, indent=2)
        print(f"Saved results to cache: {cache_path}")
    except IOError as e:
        print(f"Error saving to cache: {e}")

def get_category_members(category, cmcontinue=None):
    """Get all pages in a Wikipedia category."""
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category}',
        'cmlimit': '500'  # Maximum allowed
    }
    
    if cmcontinue:
        params['cmcontinue'] = cmcontinue
    
    response = requests.get('https://en.wikipedia.org/w/api.php', params=params)
    data = response.json()
    
    results = data.get('query', {}).get('categorymembers', [])
    
    # Handle continuation if there are more results
    if 'continue' in data:
        next_cmcontinue = data['continue']['cmcontinue']
        results.extend(get_category_members(category, next_cmcontinue))
        
    return results

def get_page_content(page_id):
    """Get the content of a Wikipedia page."""
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'pageids': page_id,
        'explaintext': True  # Get plain text instead of HTML
    }
    
    response = requests.get('https://en.wikipedia.org/w/api.php', params=params)
    data = response.json()
    
    page_data = data.get('query', {}).get('pages', {}).get(str(page_id), {})
    return page_data.get('extract', '')

def clean_text(text):
    """Clean the text by removing non-alphanumeric characters and converting to lowercase."""
    # Replace newlines with spaces
    text = text.replace('\n', ' ')
    # Remove non-alphanumeric characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Split into words
    words = text.split()
    return words

def filter_common_words(words):
    """Filter out common words (stopwords)."""
    stop_words = set(stopwords.words('english'))
    # Add additional common words if needed
    additional_stop_words = {'also', 'may', 'used', 'use', 'using', 'one', 'two', 'many', 'can', 'often'}
    stop_words.update(additional_stop_words)
    
    return [word for word in words if word not in stop_words and len(word) > 1]

def analyze_category(category, use_cache=True):
    """Analyze word frequencies in a Wikipedia category."""
    if use_cache:
        cached_results = load_from_cache(category)
        if cached_results:
            return cached_results
    
    print(f"Analyzing category: {category}")
    print("Fetching pages in the category...")
    
    category_members = get_category_members(category)
    
    # Filter for normal pages (namespace 0)
    page_ids = [str(member['pageid']) for member in category_members if member['ns'] == 0]
    
    if not page_ids:
        print(f"No pages found in category '{category}'")
        return Counter()
    
    print(f"Found {len(page_ids)} pages. Processing...")
    
    all_words = []
    
    for i, page_id in enumerate(page_ids, 1):
        print(f"Processing page {i}/{len(page_ids)}: ID {page_id}")
        content = get_page_content(page_id)
        words = clean_text(content)
        filtered_words = filter_common_words(words)
        all_words.extend(filtered_words)
        
        # Be nice to the API, add a small delay between requests
        if i < len(page_ids):
            time.sleep(0.5)
    
    # Count word frequencies
    word_counts = Counter(all_words)
    
    # Save results to cache
    if use_cache:
        save_to_cache(category, word_counts)
    
    return word_counts

def display_results(word_counts, top_n=50):
    """Display the word frequency results."""
    if not word_counts:
        print("No results to display.")
        return
    
    total_words = sum(word_counts.values())
    print(f"\nTotal words (excluding common words): {total_words}")
    print(f"\nTop {top_n} words by frequency:")
    
    for word, count in word_counts.most_common(top_n):
        percentage = (count / total_words) * 100
        print(f"{word}: {count} ({percentage:.2f}%)")

def main():
    parser = argparse.ArgumentParser(description='Analyze word frequencies in a Wikipedia category.')
    parser.add_argument('category', help='Wikipedia category to analyze (without "Category:" prefix)')
    parser.add_argument('--top', type=int, default=50, help='Number of top words to display (default: 50)')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching (always fetch fresh data)')
    
    args = parser.parse_args()
    
    try:
        word_counts = analyze_category(args.category, use_cache=not args.no_cache)
        if word_counts:
            display_results(word_counts, args.top)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
