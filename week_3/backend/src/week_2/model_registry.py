import os
from pathlib import Path

from dotenv import load_dotenv

from src.week_2.ai_model import AiModel, OllamaModel, GeminiCloudModel

_MODELS: dict[str, AiModel] = {}
_MODEL: AiModel | None = None

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


def load_week3_model():
	global _MODEL
	load_dotenv()
	model_env = os.getenv("AI_MODEL")
	if not model_env:
		raise ValueError("env AI_MODEL is not set")
	model_tmp = models().get(model_env)
	if model_tmp is None:
		raise ValueError("No available models found. Check your Ollama service and presence of supported models.")
	if isinstance(model_tmp, GeminiCloudModel):
		key_gemini = os.getenv("API_KEY")
		if not key_gemini:
			raise ValueError("env 'API_KEY' for Gemini model not set.")
	_MODEL = model_tmp

def week3_model() -> AiModel:
	global _MODEL
	assert _MODEL is not None
	return _MODEL


if __name__ == "__main__":
	for model in _MODELS.values():
		print(model)
