YouTube Makeup Video Recommender - Data Ingestion (Phase 1a)
This repository contains the initial phase of a project aimed at building a personalized YouTube makeup video recommender. This phase focuses on data ingestion and initial LLM-driven analysis of YouTube channels and their content.

Project Overview
The overall vision for this project is to create a sophisticated makeup video recommendation platform that leverages AI to provide highly personalized suggestions based on a user's unique facial features.

The project is structured into several key phases:

Phase 1a (Current) - Data Ingestion & Initial LLM Analysis:

Searches for relevant YouTube channels.

Fetches channel statistics, branding information, and recent video details.

Downloads channel profile pictures and video transcripts.

Utilizes Google Gemini AI to analyze channel content (descriptions & transcripts) and channel profile pictures (thumbnails) to infer specific facial features and makeup styles.

Displays the processed and analyzed data.

Phase 1b (Future) - Storing Video Details:

Extend the data ingestion to include detailed metadata for individual videos, potentially leveraging a database for persistent storage.

Phase 2 (Future) - Developing Recommendation Engine:

Implement a recommendation engine that matches user-analyzed facial features with the features identified in video content and creators.

Develop algorithms for ranking and filtering recommendations based on various criteria.

Phase 3 (Future) - FastAPI for UI:

Build a FastAPI backend to expose the recommendation engine via an API, allowing a user interface (e.g., a web application) to consume the recommendations.

Scripts Overview
This phase includes the following modular Python scripts:

config.py:

Purpose: Stores all global configuration variables, including YouTube Data API Key, Gemini API Key, Gemini model names, predefined search queries, and categories for LLM analysis.

Role: Centralized configuration management.

youtube_api_utils.py:

Purpose: Contains functions for interacting with the YouTube Data API. This includes searching for channels, fetching channel statistics, getting the last video upload timestamp, and retrieving video transcripts. It also handles translation of non-English transcripts to English using Gemini.

Role: Handles all YouTube-related data fetching.

gemini_ai_utils.py:

Purpose: Provides utility functions for interacting with the Google Gemini AI. This includes downloading images and converting them to PIL Image objects, and performing LLM-driven analysis on both images (for facial features from thumbnails) and text (for content analysis from descriptions and transcripts).

Role: Encapsulates all Gemini AI interactions.

main_channel_processor.py:

Purpose: The main orchestration script. It imports functions from config, youtube_api_utils, and gemini_ai_utils to execute the full data ingestion and analysis pipeline. It searches for channels, fetches their details, performs LLM analysis, and prints the comprehensive results to the console.

Role: The entry point for running the data processing pipeline.

Setup
Prerequisites
Python 3.8+

pip (Python package installer)

API Keys
You will need API keys for:

YouTube Data API v3:

Go to Google Cloud Console.

Create a new project (if you don't have one).

Navigate to "APIs & Services" > "Library".

Search for and enable "YouTube Data API v3".

Go to "APIs & Services" > "Credentials".

Create "API Key" (restrict it to YouTube Data API v3 for security).

Important: This API key should be a "Server key" or "Browser key" (unrestricted by OAuth) for direct API calls.

Google Gemini API:

Go to Google AI Studio or Google Cloud Console.

Generate an API key for the Gemini API.

SECURITY WARNING: Never hardcode your API keys directly into publicly shared code or commit them to version control. For production applications, use environment variables or a secure secrets management system. For this demo, you will place them directly in config.py.

Installation
Clone this repository (or create the files manually if you're pasting them).

Navigate to the project directory in your terminal.

Install the required Python libraries:

pip install google-api-python-client google-generativeai youtube-transcript-api Pillow requests

Usage
Configure API Keys:

Open config.py.

Replace "YOUR_YOUTUBE_API_KEY" with your actual YouTube Data API Key.

Replace "YOUR_GEMINI_API_KEY" with your actual Gemini API Key.

# config.py
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

Run the Main Processor Script:
From your terminal in the project directory, execute:

python main_channel_processor.py

The script will:

Search for channels based on the queries in config.py.

Fetch detailed information for a limited number of unique US-centric channels (currently set to 5 for demonstration).

Attempt to fetch and translate video transcripts.

Perform Gemini AI analysis on channel descriptions, transcripts, and profile pictures.

Print the detailed analysis for each channel to your console.

Individual Module Testing
Each utility script (youtube_api_utils.py, gemini_ai_utils.py) contains an if __name__ == "__main__": block with example usage. You can run these scripts independently to test their specific functionalities:

python youtube_api_utils.py
python gemini_ai_utils.py

(Note: Ensure API keys are set in config.py for these tests to function correctly).

Future Work
As outlined in the project overview, the next steps include:

Phase 1b: Storing Video Details: Integrating a database (e.g., SQLite, as hinted by sqlite_channels_table_creation.py which was part of the original context) to persistently store the enriched channel and video data.

Phase 2: Developing Recommendation Engine: Building the core logic to match user profiles (based on their facial features) with the analyzed video content and creators.

Phase 3: FastAPI for UI: Creating a web API using FastAPI to serve recommendations to a front-end application, enabling a dynamic and interactive user experience.# Makeup_Video_Recommendation
Project to recommend makeup videos based on facial features. 
![ChatGPT Image May 9, 2025, 12_50_54 PM](https://github.com/user-attachments/assets/aea455b0-585d-443e-b04e-c654c3fe53a3)

