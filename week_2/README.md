## Overview
This project uses LLMs (selective options between Ollama and Gemini Cloud models) to perform tech stack tagging on job descriptions and analyze skill gaps with a given resume.

## Requirements
- Python 3.14
- [uv](https://docs.astral.sh/uv/getting-started/installation/)


## Setup
- Git clone this repo and CD into it.
- Run `uv sync`
- Initiate virtual environment: `source .venv/bin/activate`
- For Gemini models usage, duplicate `.env.example` as `.env` and paste your Gemini API key.

## Usage

```
python prompt_model.py <model> <context>
```
Prompts a model with the context and prints it.

```
python tag_data.py <model> <db_path>
```
Prompts a model to start tech stack tagging onto the provided DB.

```
python find_skill_gaps.py
```
A default model will be used to start identify skill gaps from resume with the DB.


## Testing
Human-tested with the required Ollama models and Gemini Cloud Models.
Repeated calls with identical inputs was tested to check determinism

## Limitations
Processing from local LLMs is subjective to user hardware capabilities, and from cloud LLMs is subjective to current cloud traffic.
Cheaper LLMs may not perform tagging properly due to lower input tokens.

## Refection
I prioritised trying to get determined outputs even in the data tagging as much as I could which had the tradeoff for speed as the prompt to the model is very large. Python OOPs were used to load AI Models as part of code structuring.
