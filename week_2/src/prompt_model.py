import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentResponse
from ollama import ChatResponse, chat

from model_registry import AiModelFamily, models


@dataclass
class PromptResponse:
	context: str
	tokens: int = 0

	@staticmethod
	def create(res: ChatResponse | GenerateContentResponse | str) -> PromptResponse:
		tokens = 0
		# Ollama
		if isinstance(res, ChatResponse):
			context = res.message.content or "No context available"
			tokens = res.get('eval_count') or tokens
			success = res.done
		# Gemini
		else:
			context = res.text or "No context available"
			tokens = res.usage_metadata.candidates_token_count or tokens

		return PromptResponse(context, tokens)


def prompt_model(model_name: str, prompt: str) -> PromptResponse | None:
	ai_model = models().get(model_name)
	if not ai_model:
		print(f"Model '{model_name}' does not exist.")
		return None
	if ai_model.family is AiModelFamily.GEMINI:
		load_dotenv()
		gemini_api_key = os.getenv("API_KEY")
		if not gemini_api_key:
			print("'API_KEY' in .env does not exist.")
			return None
		success = True
		client = genai.Client(api_key=gemini_api_key)
		res = client.models.generate_content(
			model=ai_model.full_name,
			contents=prompt
		)
		return PromptResponse.create(res)
	res = chat(model=ai_model.full_name, messages=[
		{
			'role': 'user',
			'content': prompt
		}
	])
	return PromptResponse.create(res)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python prompt_model.py <model> <prompt>")
		sys.exit(1)
	response = prompt_model(sys.argv[1], sys.argv[2])
	if not response:
		sys.exit(1)
	print("\n--- RESPONSE ---\n")
	print(response.context)