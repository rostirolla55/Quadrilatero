from openai import OpenAI

client = OpenAI(
  api_key="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"
)

response = client.responses.create(
  model="gpt-5.4-mini",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text);
