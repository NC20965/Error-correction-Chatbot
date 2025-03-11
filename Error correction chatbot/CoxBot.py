import re
import json
import nltk
import string
import random
import threading

from nltk.stem import WordNetLemmatizer, PorterStemmer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys

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
    error_responses = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
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
def extract_error_message(error_input):
    tokens = nltk.word_tokenize(error_input)
    java_python_patterns = r"(nullpointerexception|arrayindexoutofboundsexception|" \
                           r"classnotfoundexception|illegalargumentexception|" \
                           r"numberformatexception|filenotfoundexception|" \
                           r"noclassdeffounderror|arithmeticexception|" \
                           r"unsupportedoperationexception|java\.lang\.[a-z]+exception|" \
                           r"traceback|nameerror|typeerror|valueerror|" \
                           r"importerror|indentationerror|keyerror|indexerror|" \
                           r"attributeerror|modulenotfounderror|syntaxerror)"
    for token in tokens:
        match = re.match(java_python_patterns, token, re.IGNORECASE)
        if match:
            return match.group(0).lower().replace('java.lang.', '')
    return None


# Function to close the browser after a delay
def close_browser_after_delay(driver, delay):
    threading.Timer(delay, lambda: driver.quit()).start()

# Search Stack Overflow using Selenium
def search_stack_overflow(error_type, user_input, error_responses):
    # Extract the error message from the user input
    error_message = extract_error_message(user_input)
    if not error_message:
        return "Could not identify the error message from the input."

    # Get the base URL for the error type
    base_url = error_responses.get(error_type)
    if not base_url:
        return "I couldn't find a suitable Stack Overflow URL for this error type."

    try:
        # Initialize the Selenium WebDriver
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)

        # Launch the website
        driver.get(base_url)

        # Start a timer to close the browser after 5 minutes
        close_browser_after_delay(driver, 300)  # 300 seconds = 5 minutes

        # Wait for the search bar to be available and interactable
        wait = WebDriverWait(driver, 10)
        search_bar = wait.until(EC.presence_of_element_located((By.NAME, "q")))

        # Input the user error message into the search bar and submit
        search_bar.send_keys(error_message)
        search_bar.send_keys(Keys.RETURN)

        # Wait for the search results page to load
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.question-summary')))

        # Get the first result link
        first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.question-summary .result-link > a')))
        first_result_url = first_result.get_attribute('href')

        # Return the first result link to the chatbot interface
        return f"Search completed! Here's the first result: <a href='{first_result_url}' target='_blank'>{first_result_url}</a>"

    except Exception as e:
        # Handle exceptions gracefully and return the error message
        return f"An error occurred while searching Stack Overflow: {str(e)}"



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
