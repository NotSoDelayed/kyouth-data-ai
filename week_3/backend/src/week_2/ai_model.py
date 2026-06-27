import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import ollama
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerateContentResponse
from ollama import ChatResponse, ResponseError


@dataclass
class PromptResponse:
	context: str
	tokens: int = 0

	@staticmethod
	def create(res: ChatResponse | GenerateContentResponse) -> PromptResponse | None:

		# Ollama
		if isinstance(res, ChatResponse):
			context = res.message.content
			if not context:
				return None
			tokens = res.get('eval_count') or 0
		# Gemini
		else:
			context = res.text
			if not context:
				return None
			tokens = res.usage_metadata.candidates_token_count or 0

		return PromptResponse(context, tokens)

@dataclass(frozen=True)
class AiModel(ABC):
	name: str
	rpm: int
	tpm: int
	rpd: int

	@abstractmethod
	def prompt(self, content: Any) -> PromptResponse | None:
		pass

class OllamaModel(AiModel):
	def prompt(self, content: Any) -> PromptResponse | None:
		try:
			res = ollama.chat(model=self.name, messages=[
				{"role": "user", "content": content}
			])
		except ResponseError as err:
			print(f"[Ollama Error] {err.error}")
			return None
		except Exception as err:
			print(f"[Ollama Error] {err}")
			return None
		return PromptResponse.create(res)

class GeminiCloudModel(AiModel):
	@classmethod
	def parse(cls, name: str, ratelimits: str) -> GeminiCloudModel:
		rpm, tpm, rpd = ratelimits.split(" ", 2)
		return GeminiCloudModel(name, unscale(rpm), unscale(tpm), unscale(rpd))

	def prompt(self, content: Any) -> PromptResponse | None:
		load_dotenv()
		apikey = os.getenv("API_KEY")
		if not apikey:
			print("'API_KEY' in .env does not exist.")
			return None
		client = genai.Client(api_key=apikey)
		try:
			res = client.models.generate_content(model=self.name, contents=content)
		except APIError as err:
			print(f"[Gemini Error] {err.message}")
			return None
		except Exception as err:
			print(f"[Gemini Error] {err}")
			return None
		return PromptResponse.create(res)

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
