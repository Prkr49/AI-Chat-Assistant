from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

command = """
[20:30, 18/2/2025] Code Ninja: jo sunke coding ho sake?
[20:30, 18/2/2025] Arnav Das: https://www.youtube.com/watch?v=DzmG-4-OASQ
[20:30, 18/2/2025] Arnav Das: ye
[20:30, 18/2/2025] Arnav Das: https://www.youtube.com/watch?v=DzmG-4-OASQ
[20:31, 18/2/2025] Code Ninja: bhai ye to pura hindi hai
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "system",
            "content": "You are a person named Prince from India who speaks Hindi and English. Reply in a funny style. Only return the next chat message."
        },
        {
            "role": "user",
            "content": command
        }
    ]
)

print(response.output_text)