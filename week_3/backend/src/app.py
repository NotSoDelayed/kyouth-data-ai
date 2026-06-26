import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.week_2 import model_registry
from src.week_2.find_skill_gaps import find_skill_gaps

load_dotenv()
MODEL_ENV = os.getenv("AI_MODEL")
if not MODEL_ENV:
	raise ValueError("env AI_MODEL is not set")
MODEL = model_registry.models().get(MODEL_ENV)
if MODEL is None:
	raise ValueError(f"No available models found. Check your Ollama service and presence of supported models")


app = FastAPI()

def is_skill_gap_query(content: str) -> bool:
	assert MODEL is not None
	res = MODEL.prompt(f"""
		You are a binary classifier.
		
		Exact output format:
		true
		false
		
		Task:
		Return true if the user prompt is about finding or analyzing skill gaps for a person, especially the user.
		
		Skill gaps can be written as:
		- skill gaps
		- skillgaps
		- gaps in skills
		- missing skills
		
		The request does NOT need to include "my" or "me".
		If no person is specified, assume it refers to the user.
		
		Return true when the user is asking to:
		- find skill gaps
		- identify skill gaps
		- analyze skill gaps
		- assess skill gaps
		- discover skill gaps
		- help with skill gaps
		- find gaps in skills
		
		Return false only when:
		- skill gaps concept is not present at all
		- it is clearly about someone else (his, her, their skill gaps)
		- it is only a definition or explanation (what are skill gaps)
		- it is negated (do not find skill gaps, don't analyze skill gaps)
		
		TRUE examples:
		- find skill gaps
		- find my skill gaps
		- help find skill gaps
		- identify skill gaps
		- analyse skill gaps
		- assess skill gaps
		- discover skill gaps
		- find skillgaps
		- find gaps in skills
		
		FALSE examples:
		- skill gaps
		- what are skill gaps
		- explain skill gaps
		- find skills
		- find gaps
		- find his skill gaps
		- find their skill gaps
		- do not find skill gaps
		
		prompt: `{content}`
	""")
	return res is not None and res.context.strip().lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
def chat(data: dict[str, str]):
	assert MODEL is not None
	user_input = data["reply"]
	if re.fullmatch(r"^find\s+(my\s+)?skill\s*gaps?$", user_input):
		prompt_skill_gaps = True
	else:
		prompt_skill_gaps = is_skill_gap_query(user_input)

	reply: str
	if prompt_skill_gaps:
		# TODO read resume from frontend
		reply = ", ".join(find_skill_gaps("./week_2/data/resume_d3.txt", "./week_2/data/jobs.db").gaps)
	else:
		reply = "[Error] Unknown error occurred."
		res = MODEL.prompt(user_input)
		if res is not None:
			reply = res.context
	return {
		"model": MODEL.name,
		"reply": reply
	}
