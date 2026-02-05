from groq import Groq
from api_key import GROQ_API_KEY

# Initialize Groq client
client = Groq(api_key= GROQ_API_KEY)

# User input
text = input("What topic you want to write about: ")

print("The AI BOT is trying now to generate a new text for you...")

# Generate text using LLaMA 3
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": text}
    ],
    max_tokens=1024,
    temperature=0.5
)

generated_text = response.choices[0].message.content

# Save output
with open("generated_text.txt", "w", encoding="utf-8") as file:
    file.write(generated_text.strip())

print("The Text Has Been Generated Successfully!")
