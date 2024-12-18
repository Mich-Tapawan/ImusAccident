import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
from scripts.chatbot import answer_gemini
from scripts.model import AccidentModel
from scripts.barangay_list import generate_barangay_list
from scripts.month_data import generate_month_list
from datetime import datetime


accident_model = AccidentModel()
accident_model.load_model()

def answer_prompt(prompt):
    # Load SpaCy's English language model
    nlp = spacy.load("en_core_web_sm")

    # Define the keywords and phrases
    FILE_PATH = 'traffic-incident.xlsx'
    barangay_list = generate_barangay_list(FILE_PATH)
    
    PROMPT_KEYWORDS = {
        "request": ["accident percentage", "percentage of accidents", 'total accidents'],
        "barangay": barangay_list,
        "time": [str(i) for i in range(1, 25)],  # Times as strings to match tokens
        "month":["january","february","march","april","may","june","july","august","september","october","november","december"],
        'year':['2022', '2023', '2024']
    }

    # Build PhraseMatcher for multi-word phrases
    def build_phrase_matcher(keywords):
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        for phrase in keywords:
            doc = nlp(phrase)
            matcher.add(phrase, [doc])
        return matcher

    # Create matchers for each category
    matchers = {key: build_phrase_matcher(values) for key, values in PROMPT_KEYWORDS.items()}

    # Tokenize the input prompt
    doc = nlp(prompt.lower())
    matched_details = {"request": None, "barangay": None, "time": None}

    # Match tokens with each category's matcher
    for category, matcher in matchers.items():
        matches = matcher(doc)
        for match_id, start, end in matches:
            matched_phrase = doc[start:end].text 
            matched_details[category] = matched_phrase

    # Handle specific requests for accident percentage
    if matched_details["request"] in ["percentage of accidents", "accident percentage"]:
        barangay = matched_details["barangay"]
        time = matched_details["time"]

        if not barangay or not time:
            return "Error: Please specify both barangay and time for accident percentage queries."
        print(matched_details)
        try:
            data = accident_model.predict_accident_chance(barangay.upper(), int(time))
            return f'The accident percentage is {data} in {barangay.upper()} during hour {time}'
        except Exception as e:
            return f"Error processing request: {e}"
        
    elif matched_details["request"] in ["total of accidents", "total accidents"]:
        month_name = matched_details["month"][:3].upper() 
        month = datetime.strptime(month_name, "%b").month 
        print(month)
        print(f"Matched Month: {month_name}, Numeric Month: {month}")
        year = matched_details["year"]

        if year not in PROMPT_KEYWORDS['year'] or matched_details['month'] not in PROMPT_KEYWORDS['month']:
            return 'No data for this month and year.'
        
        if not month or not year:
            return "Error: Please specify both barangay and time for accident percentage queries."
        print(matched_details)
        try:
            data = generate_month_list(FILE_PATH, int(year), month)
            print(data)
            return f'The total number of accidents during {matched_details['month']} of the year {year} is {data['totalAccidents']}'
        except Exception as e:
            return f"Error processing request: {e}"

        # Handle chatbot fallback if no matches are found
    if not matched_details["request"]:
        print("chatbot fallback")
        response = answer_gemini(prompt)
        return response


    # Default fallback
    return "No valid match found in the prompt."

# Example usage
#print(answer_prompt('what is the total accidents in march during 2023'))
