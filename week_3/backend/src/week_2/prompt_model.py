import sys

from src.week_2.ai_model import PromptResponse
from src.week_2 import model_registry


def prompt_model(model_name: str, content: str) -> PromptResponse | None:
	model_registry.load_models()
	ai_model = model_registry.models().get(model_name)
	if not ai_model:
		print(f"Model '{model_name}' does not exist.")
		return None
	return ai_model.prompt(content)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python prompt_model.py <model> <prompt>")
		sys.exit(1)

	response = prompt_model(sys.argv[1], sys.argv[2])
	if not response:
		sys.exit(1)

	print("\n--- RESPONSE ---\n")
	print(response.context)
