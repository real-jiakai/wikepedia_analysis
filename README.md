# Wikipedia Category Word Frequency Analyzer

This project analyzes the word frequency across all pages in a specified Wikipedia category and visualizes the results.

## Demo

![Wikipedia Category Word Cloud Visualization](https://cdn.sa.net/2025/02/28/epu5VS2tnHLRiPA.webp)

## Features

- Fetches all pages in a given Wikipedia category using the MediaWiki API
- Processes and cleans the text from each page
- Filters out common words (stopwords)
- Calculates and displays the frequency of non-common words
- Shows results as both raw counts and percentages
- Caches results to avoid redundant processing
- Provides a web interface with interactive word cloud visualization

## Requirements

- Python 3.6+
- Required packages: requests, nltk, flask

## Installation

1. Clone this repository
2. Set up the virtual environment using uv:
   ```
   mkdir -p .venv
   uv venv .venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

## Command-line Usage

Run the script with a Wikipedia category name:

```
python wiki_word_frequency.py "Large_language_models"
```

Optional arguments:
- `--top N`: Display the top N words (default: 50)
- `--no-cache`: Force fresh data retrieval, ignoring cache

## Web Application

The project includes a Flask web application that provides an interactive word cloud visualization.

To run the web app:

```
source .venv/bin/activate
python app.py
```

Then open a browser and go to http://127.0.0.1:5000

Features of the web app:
- Input any Wikipedia category name
- See previously analyzed categories
- Interactive word cloud visualization
- Size of words proportional to their frequency
- Hover over words to see exact frequency counts

## Acknowledgments

This project was created with assistance from:
- **Claude 3.7 Sonnet** - AI model by Anthropic used for planning and code development
- **Windsurf Cascade** - agentic AI coding assistant used for implementation and debugging

Special thanks to the developers of the MediaWiki API, D3.js, Flask, and other open source libraries that made this project possible.

This project was inspired by the [Build Apps with Windsurf's AI Coding Agents](https://www.deeplearning.ai/short-courses/build-apps-with-windsurfs-ai-coding-agents) course from deeplearning.ai.

## The Joy of Coding

Creating this project was a delightful experience! The seamless integration of Wikipedia data with interactive visualizations brought a special joy to the development process. Watching the word clouds transform as different categories are explored creates a truly satisfying coding experience. Enjoy the vibe of coding with data and visualizations!
