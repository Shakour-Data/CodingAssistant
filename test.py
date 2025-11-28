from together import Together
client = Together()

completion = client.chat.completions.create(
  model="openai/gpt-oss-20b",
  messages=[{"role": "user", "content": "What are the top 3 things to do in New York?"}],
)

print(completion.choices[0].message.content)