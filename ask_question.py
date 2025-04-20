"""
Simple script to ask a question to Gemini Pro API
"""

from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel('gemini-1.5-pro')

def get_answer(question):
    """Get answer from Gemini Pro model"""
    response = model.generate_content(question)
    return response.text

if __name__ == "__main__":
    print("QA System using Gemini Pro API")
    print("------------------------------")
    print("Type 'exit' to quit")
    print()

    while True:
        question = input("Ask a question: ")

        if question.lower() in ['exit', 'quit', 'q']:
            break

        if not question.strip():
            print("Please enter a question.")
            continue

        print("\nThinking...\n")
        try:
            answer = get_answer(question)
            print(f"Answer: {answer}\n")
        except Exception as e:
            print(f"Error: {str(e)}\n")
