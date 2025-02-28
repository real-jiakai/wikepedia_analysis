#!/usr/bin/env python3
"""
Flask application to display word frequencies as a word cloud.
"""

import os
import json
import re
from flask import Flask, render_template, request, jsonify
from wiki_word_frequency import analyze_category, load_from_cache, get_cache_path

app = Flask(__name__)

def normalize_category_name(category):
    """Normalize category name to consistent format."""
    # Replace underscores with spaces for display
    return category.replace('_', ' ')

def get_internal_category_name(category):
    """Convert display category name to internal format."""
    # Replace spaces with underscores for processing
    return category.replace(' ', '_')

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/get_categories')
def get_categories():
    """Return a list of all cached categories."""
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    if not os.path.exists(cache_dir):
        return jsonify([])
        
    categories = []
    for filename in os.listdir(cache_dir):
        if filename.endswith('.json'):
            # Extract category name from filename (remove hash and extension)
            category_with_hash = filename.rsplit('.', 1)[0]  # Remove extension
            if '_' in category_with_hash:
                # Find the last underscore followed by the hash
                match = re.search(r'(.+)_[a-f0-9]{32}$', category_with_hash)
                if match:
                    category = match.group(1)
                    # Display with spaces instead of underscores
                    categories.append(normalize_category_name(category))
    
    return jsonify(categories)

@app.route('/word_frequencies', methods=['POST', 'GET'])
def get_word_frequencies():
    if request.method == 'POST':
        category = request.form.get('category', '')
    else:  # GET method
        category = request.args.get('category', '')
        
    if not category:
        return jsonify({"error": "No category provided"}), 400

    # Convert displayed category name to internal format
    internal_category = get_internal_category_name(category)
    
    # Try to load from cache, or analyze if not cached
    word_counts = load_from_cache(internal_category)
    
    if word_counts is None:
        # Not in cache, analyze the category
        try:
            word_counts = analyze_category(internal_category)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Convert to the format needed for the word cloud
    # and limit to top 100 words for better visualization
    words_data = [{"text": word, "size": count} for word, count in word_counts.most_common(100)]
    
    return jsonify(words_data)

if __name__ == '__main__':
    app.run(debug=True)
