"""
Crisis Classification Module
========================
This module provides a function to follow the CrisisMMD annotation process using Gemini 2.5 Flash.
It takes tweet text and an image, and returns structured labels for:
    - Informative vs Not informative (text and image)
    - Humanitarian categories (text and image)
    - Damage severity (image)
    - Confidence scores (simulated)
    - Location (if possible)
    - Seriousness score (0-1, extra)
"""

import os
import google.generativeai as genai
import json
import re
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file in the project root
load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if API_KEY is None:
    raise EnvironmentError("Please set the GOOGLE_API_KEY variable in your .env file.")
genai.configure(api_key=API_KEY)

def classify_crisismmd(tweet_text, image_path, image_url=None):
    """
    Imitates CrisisMMD annotation using Gemini 2.5 Flash.

    Args:
        tweet_text (str): The tweet text.
        image_path (str): Path to the tweet image file.
        image_url (str, optional): Original image URL for reference.

    Returns:
        dict: Structured results with keys matching CrisisMMD columns.
    """
    with open(image_path, 'rb') as img_file:
        image_bytes = img_file.read()

    prompt = f"""
    You are an expert annotator for the CrisisMMD dataset. Given a tweet's text, image, and image URL, assign the following labels, using only the provided options. If unsure, use 'not_informative', 'not_humanitarian', or 'dont_know_or_cant_judge'.

**Task 1: Informative vs Not informative**
- For text: 'informative', 'not_informative', or 'dont_know_or_cant_judge'
- For image: 'informative', 'not_informative', or 'dont_know_or_cant_judge'

**Task 2: Humanitarian categories**
- For text and image: one of
    'affected_individuals', 'infrastructure_and_utility_damage', 'injured_or_dead_people',
    'missing_or_found_people', 'rescue_volunteering_or_donation_effort', 'vehicle_damage',
    'other_relevant_information', 'not_humanitarian'

**Task 3: Damage severity assessment (image only)**
- 'severe_damage', 'mild_damage', 'little_or_no_damage', or 'dont_know_or_cant_judge'

For each label, also provide a confidence score (0-1).

If possible, extract a location from the tweet or image (otherwise null).
Also, provide a seriousness_score (0-1).

Return a JSON object with these keys:
- text_info (str)
- text_info_conf (float)
- image_info (str)
- image_info_conf (float)
- text_human (str)
- text_human_conf (float)
- image_human (str)
- image_human_conf (float)
- image_damage (str)
- image_damage_conf (float)
- location (str or null)
- seriousness_score (float)
- tweet_text (str)
- image_url (str)

Tweet text: {tweet_text}
Image URL: {image_url}
"""

    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content([prompt, image_bytes])

    # Extract JSON from response
    match = re.search(r'\{[\s\S]*\}', response.text)
    if not match:
        raise ValueError("Model response did not contain valid JSON.")
    result = json.loads(match.group(0))
    # Include original tweet and image URL
    result['tweet_text'] = tweet_text
    result['image_url'] = image_url
    return result