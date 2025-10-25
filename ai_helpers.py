import os
from openai import OpenAI
from dotenv import load_dotenv

# load environment variables from .env
load_dotenv()

# create openAI client using API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- BASIC TEXT GENERATOR ----------------------------
# receives string which is user prompt,*temperature is house creative/rational ai is (1=creative, 0=rational)
def generate_text(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """
    Sends a prompt to OpenAI and returns the model's response.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error:", e)
        return "Error generating text."

# -------- SUMMARIZATION --------
def summarize_text(text: str, max_words: int = 100) -> str:
    """
    Summarizes the given text in under 'max_words' words.
    """
    prompt = f"Summarize this text in under {max_words} words:\n\n{text}"
    return generate_text(prompt, temperature=0.3)

# -------- SENTIMENT ANALYSIS --------
def analyze_sentiment(text: str) -> str:
    """
    Classifies the sentiment of the text as Positive, Negative, or Neutral.
    """
    prompt = f"Classify the sentiment of this text (Positive, Negative, or Neutral):\n\n{text}"
    return generate_text(prompt, temperature=0.0)

# -------- Quick test if you run this file directly --------
if __name__ == "__main__":
    sample = "I love coding with my teammates, it makes learning fun!"
    print("Summary:", summarize_text(sample))
    print("Sentiment:", analyze_sentiment(sample))