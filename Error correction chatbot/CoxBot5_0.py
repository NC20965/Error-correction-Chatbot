#!/usr/bin/env python
# coding: utf-8

# In[5]:


import re
import json
import nltk
import string
import random

from nltk.stem import WordNetLemmatizer, PorterStemmer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Ensure necessary NLTK resources are downloaded
#nltk.download('punkt')
#nltk.download('wordnet')

# Initialize lemmatizer and stemmer
lemmer = WordNetLemmatizer()
stemmer = PorterStemmer()

# Tokenization, lemmatization, and stemming functions
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def StemTokens(tokens):
    return [stemmer.stem(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

# Load responses from JSON
def load_responses(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading responses: {e}")
        return {}

# Load error responses from a text file
def load_error_responses(file_path):
    """
    Load error response mappings from a text file into a dictionary.
    Each line in the file should have the format: key:value
    """
    error_responses = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Ignore empty lines or lines without a key-value pair
                if ":" in line.strip():
                    key, value = line.strip().split(":", 1)
                    error_responses[key.strip().lower()] = value.strip()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"Error loading error responses from file: {e}")
    return error_responses


# Detect Python or Java errors
def detect_error(user_input):
    tokens = LemNormalize(user_input)
    processed_input = " ".join(tokens)
    
    python_pattern = (
        r"traceback \(most recent call last\):|nameerror|typeerror|valueerror|"
        r"importerror|indentationerror|keyerror|indexerror|attributeerror|"
        r"modulenotfounderror|syntaxerror"
    )
    java_pattern = (
        r"exception in thread.*|nullpointerexception|arrayindexoutofboundsexception|"
        r"classnotfoundexception|illegalargumentexception|numberformatexception|"
        r"filenotfoundexception|noclassdeffounderror|arithmeticexception|"
        r"unsupportedoperationexception|java\.lang\.[a-z]+exception"
    )
    
    if re.search(python_pattern, processed_input, re.IGNORECASE):
        return "python"
    elif re.search(java_pattern, processed_input, re.IGNORECASE):
        return "java"
    return None

# Extract error message
# Extract error message
def extract_error_message(error_input):
    # Tokenize while preserving punctuation relevant to patterns (e.g., '.' and ':')
    tokens = nltk.word_tokenize(error_input)
    print(f"Raw tokens: {tokens}")  # Debugging to check initial tokens

    # Patterns for matching Java and Python errors
    java_python_patterns = r"(nullpointerexception|arrayindexoutofboundsexception|" \
                           r"classnotfoundexception|illegalargumentexception|" \
                           r"numberformatexception|filenotfoundexception|" \
                           r"noclassdeffounderror|arithmeticexception|" \
                           r"unsupportedoperationexception|java\.lang\.[a-z]+exception|" \
                           r"traceback|nameerror|typeerror|valueerror|" \
                           r"importerror|indentationerror|keyerror|indexerror|" \
                           r"attributeerror|modulenotfounderror|syntaxerror)"

    # Search for patterns in tokens
    for token in tokens:
        match = re.match(java_python_patterns, token, re.IGNORECASE)
        if match:
            # Clean up and normalize the error keyword
            matched_error = match.group(0).lower().replace('java.lang.', '')
            print(f"Matched error keyword: {matched_error}")  # Debugging
            return matched_error

    print("No matching error keyword found.")  # Debugging for failure case
    return None


# Search Stack Overflow using Selenium
def search_stack_overflow(error_type, user_input, error_responses):
    error_message = extract_error_message(user_input)
    if not error_message:
        return "Could not identify the error message from the input."

    base_url = error_responses.get(error_type)
    if not base_url:
        return "I couldn't find a suitable Stack Overflow URL for this error type."
    
    search_url = f"{base_url}+{error_message.replace(' ', '+')}"

    try:
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)
        results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.result-link > a')))
        
        if results:
            first_result_url = results[0].get_attribute('href')
            driver.quit()
            return f"Here is a suggested solution: {first_result_url}"
        else:
            driver.quit()
            return "No solutions were found on Stack Overflow for your error."
    except Exception as e:
        return f"An error occurred while accessing Stack Overflow: {str(e)}"

# Get error solution
def get_error_solution(error_type, user_input, error_responses):
    return search_stack_overflow(error_type, user_input, error_responses)

# Chatbot response logic
def response(user_response, responses_data, error_responses):
    if user_response == "patterns":
        patterns = [pattern for intent in responses_data.get("intents", []) for pattern in intent["patterns"]]
        return f"Here are the patterns I recognize: {', '.join(patterns)}"
    
    for intent in responses_data.get("intents", []):
        for pattern in intent["patterns"]:
            if re.search(pattern, user_response, re.IGNORECASE):
                return random.choice(intent["responses"])
    
    error_type = detect_error(user_response)
    if error_type:
        return get_error_solution(error_type, user_response, error_responses)
    
    return "Sorry, I didn't understand that. Can you provide more details?"

# Main chatbot loop
if __name__ == "__main__":
    responses_data = load_responses('responses.json')
    if not responses_data:
        print("Error: Responses data not loaded correctly.")
        exit()

    error_responses = load_error_responses('error_responses.txt')
    if not error_responses:
        print("Error: No error responses found in the text file.")
        exit()

    print("CoxBot: Hello! I can help you with Python or Java errors. Type 'bye' to exit.")

    while True:
        user_response = input("You: ").lower()
        if user_response == 'bye':
            print("CoxBot: Goodbye! Have a nice day!")
            break
        elif user_response in ['thanks', 'thank you']:
            print("CoxBot: You are welcome!")
        else:
            print("CoxBot: ", end="")
            print(response(user_response, responses_data, error_responses))


# In[ ]:




