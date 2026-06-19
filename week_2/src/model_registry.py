import logging
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


def unscale(value: str) -> int:
	match = re.fullmatch(r"(\d+(\.\d+)?)([KMB])?", value.strip().upper())

	if not match:
		raise ValueError(f"Invalid number format: {value}")

	number, _, suffix = match.groups()
	multipliers = {
		None: 1,
		"K": 1000,
		"M": 1000000,
		"B": 1000000000,
	}
	return int(float(number) * multipliers[suffix])


class AiModelFamily(Enum):
	OLLAMA = "ollama"
	GEMINI = "gemini"


@dataclass(frozen=True)
class AiModel:
	family: AiModelFamily
	full_name: str
	tier: str
	rpm: int
	tpm: int
	rpd: int

	@classmethod
	def parse(cls, name: str, ratelimits: str) -> AiModel:
		if "-" in name:
			family, tier = name.split("-", 1)
		else:
			match = re.match(r"^([a-zA-Z]+)(.*)$", name)
			if not match:
				raise ValueError(f"Invalid model name: {name}")
			family, tier = match.groups()
			tier = tier or ""
		rpm, tpm, rpd = ratelimits.split(" ", 2)
		if family == "gemini":
			return AiModel(AiModelFamily.GEMINI, name, tier, unscale(rpm), unscale(tpm), unscale(rpd))
		return AiModel(AiModelFamily.OLLAMA, name, tier, int(rpm), int(tpm), int(rpd))


_MODELS: dict[str, AiModel] = {}

def load_models():
	global _MODELS

	if _MODELS:
		return

	file_path = Path("rate_limits.txt")
	if not file_path.exists():
		logging.error("Populate models with format 'full_model RPM TPM RPD' model per line into 'rate_limits.txt'!")
		sys.exit(1)

	with open(file_path, "r", encoding="utf-8") as file:
		for line in file:
			line = line.strip()
			if not line:
				continue
			try:
				name, ratelimits = line.split(" ", 1)
				model = AiModel.parse(name, ratelimits)
			except ValueError as err:
				logging.warning(f"Skipping model '{line}': {err}")
				continue
			_MODELS[name] = model

	# Hardcode for installed Ollama models
	for name in "deepseek-r1", "llama3.1", "phi3":
		_MODELS[name] = AiModel.parse(name, "-1 -1 -1")
	if not _MODELS:
		logging.warning("No valid model exist. Exiting...")
		sys.exit(1)
	_INITIALIZED = True

load_models()

def models() -> dict[str, AiModel]:
	return _MODELS

if __name__ == "__main__":
	for model in _MODELS.values():
		print(model)
