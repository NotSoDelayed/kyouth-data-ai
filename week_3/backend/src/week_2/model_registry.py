from calendar import week
from pathlib import Path

from src.week_2.ai_model import AiModel, OllamaModel, GeminiCloudModel

_MODELS: dict[str, AiModel] = {}

def load_models():
	global _MODELS

	if _MODELS:
		return

	# Load Gemini cloud models from file
	file_path = Path(__file__).parent.joinpath("rate_limits.txt")
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
				print(f"Skipping model '{line}': {err}")
				continue
			_MODELS[name] = model

	# Load supported Ollama models
	for name in "deepseek-r1:1.5b", "llama3.1", "phi3":
		_MODELS[name] = OllamaModel(name, -1, -1 ,-1)

load_models()

def models() -> dict[str, AiModel]:
	return _MODELS

if __name__ == "__main__":
	for model in _MODELS.values():
		print(model)
