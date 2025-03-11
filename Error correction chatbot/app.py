

from flask import Flask, render_template, request
from CoxBot import response, load_responses, load_error_responses

# Initialize Flask app
app = Flask(__name__)

# Load Coxbot data
responses_data = load_responses('responses.json')
if not responses_data:
    raise Exception("Error: Responses data not loaded correctly.")

error_responses = load_error_responses('error_responses.txt')
if not error_responses:
    raise Exception("Error: No error responses found in the text file.")

# Route for CoxBot's home page
@app.route("/CoxBot")
def home():
    return render_template("index.html")  # Ensure 'index.html' exists in the 'templates' folder

# Route to handle CoxBot responses
@app.route("/get")
def     bot_response():
    user_input = request.args.get('msg')  # Get user input from the query parameter
    if not user_input:
        return "Please enter a valid message."

    try:
        # Get the CoxBot response
        bot_response = response(user_input.lower(), responses_data, error_responses)
        return str(bot_response)
    except Exception as e:
        # Handle errors gracefully and log them
        return f"An error occurred while processing your request: {str(e)}"

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)


# In[ ]:




