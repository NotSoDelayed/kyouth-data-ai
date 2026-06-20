import logging
import re
import sys
from dataclasses import dataclass
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


@dataclass(frozen=True)
class GeminiCloudModel:
	tier: str
	rpm: int
	tpm: int
	rpd: int

	@classmethod
	def parse(cls, name: str, ratelimits: str) -> GeminiCloudModel:
		family, tier = name.split("-", 1)
		rpm, tpm, rpd = ratelimits.split(" ", 2)
		return GeminiCloudModel(tier, unscale(rpm), unscale(tpm), unscale(rpd))

	def name(self):
		return f"gemini-{self.tier}"


_MODELS: dict[str, GeminiCloudModel] = {}

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
				model = GeminiCloudModel.parse(name, ratelimits)
			except ValueError as err:
				logging.warning(f"Skipping model '{line}': {err}")
				continue
			_MODELS[name] = model

load_models()

def models() -> dict[str, GeminiCloudModel]:
	return _MODELS

if __name__ == "__main__":
	for model in _MODELS.values():
		print(model)
