import logging
from pathlib import Path

from ai_model import AiModel, OllamaModel, GeminiCloudModel

_MODELS: dict[str, AiModel] = {}

def load_models():
	global _MODELS

	if _MODELS:
		return

	# Load supported Ollama models
	for name in "deepseek-r1:1.5b", "llama3.1", "phi3":
		_MODELS[name] = OllamaModel(name, -1, -1 ,-1)

	# Load Gemini cloud models from file
	file_path = Path("rate_limits.txt")
	if not file_path.exists():
		print(f"{file_path} doesn't exist. Skipping...")

	with open(file_path, "r", encoding="utf-8") as file:
		for line in file:
			line = line.strip()
			if not line:
				continue
			try:
				name, ratelimits = line.split(" ", 1)
				model = GeminiCloudModel.parse(name, ratelimits)
			except ValueError as err:
				logging.warning(f"Skipping model '{line}': {err}")
				continue
			_MODELS[name] = model

def models() -> dict[str, AiModel]:
	return _MODELS

load_models()

if __name__ == "__main__":
	for model in _MODELS.values():
		print(model)
