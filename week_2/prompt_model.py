import sys
from dataclasses import dataclass

import ollama
from google.genai.errors import APIError
from google.genai.types import GenerateContentResponse
from ollama import ChatResponse, ResponseError

import model_registry


@dataclass
class PromptResponse:
	context: str
	tokens: int = 0

	@staticmethod
	def create(res: ChatResponse | GenerateContentResponse) -> PromptResponse:

		# Ollama
		if isinstance(res, ChatResponse):
			context = res.message.content or "No context available"
			tokens = res.get('eval_count') or 0
		# Gemini
		else:
			context = res.text or "No context available"
			tokens = res.usage_metadata.candidates_token_count or 0

		return PromptResponse(context, tokens)


def prompt_model(model_name: str, content: str) -> PromptResponse | None:
	# Lazy-check on whether the input is a gemini model
	if model_name.startswith("gemini"):
		model_registry.load_models()
		ai_model = model_registry.models().get(model_name)
		if not ai_model:
			print(f"Model '{model_name}' does not exist.")
			return None
		return ai_model.prompt(content)
	
	res = ollama.chat(model=model_name, messages=[{"role": "user", "content": content}])
	return PromptResponse.create(res)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python prompt_model.py <model> <prompt>")
		sys.exit(1)

	response = None
	try:
		response = prompt_model(sys.argv[1], sys.argv[2])
	except APIError as err:
		print(f"[Gemini Error] {err.message}")
	except ResponseError as err:
		print(f"[Ollama Error] {err.error}")
	if not response:
		sys.exit(1)

	print("\n--- RESPONSE ---\n")
	print(response.context)
