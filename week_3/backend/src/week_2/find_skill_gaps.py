import sqlite3
import sys
from pathlib import Path

from pydantic import BaseModel

from src.week_2.model_registry import week3_model


class SkillGapResult(BaseModel):
	gaps: list[str]


LLM_RESUME_PROMPT = """
	Identify ALL of the tech stack items explicitly stated in the given resume.
	Each item must be 4 words maximum
	Use short noun phrases (i.e. azure, php, gcp, google cloud, ....).
	Ensure all tech related skills are accounted for
	Omit non tech related skills
	Omit certifications even if tech related
	
	Your final response is strictly a single line, comma-separated list of ALL techstack items identified from the given resume (without quotes) as such:
	"alibaba cloud, api integration or web automation, aws, aws deployment and maintenance, azure, c++, cloud logs, datastudio, excel, gcp, github actions, google cloud, grafana, linux development environments, mongodb, mysql, nginx, node.js, oracle, php, postgresql, power bi, powerbi, prometheus, restful api design and development, spring boot, spring framework, sql server, version control"

	Resume:
"""


def find_skill_gaps(resume_data: str, db_url: str) -> SkillGapResult:
	skills = parse_resume(resume_data)
	tech_stack = tech_stack_from_db(db_url)
	gaps = sorted(tech_stack - skills)
	return SkillGapResult(gaps=gaps)

def parse_resume(resume_data: str) -> set[str]:
	skill_set = set()

	res = week3_model().prompt(
		f"""
		{LLM_RESUME_PROMPT}
		```
		{resume_data}
		```
		""")
	if not res:
		return skill_set
	skills = res.context.split(', ')
	for skill in skills:
		cleaned = skill.strip(". ").lower()
		if cleaned:
			skill_set.add(cleaned)
	return skill_set

def tech_stack_from_db(db_url: str):
	db_path = Path(db_url)
	if not db_path.exists():
		print(f"DB '{db_path}' does not exist.")
		sys.exit(1)
	with sqlite3.connect(db_path) as db:
		db.row_factory = sqlite3.Row

		batch_size = 20
		last_id = 0
		tech_stack = set()
		while True:
			rows = db.execute("""
				SELECT source_id, tech_stack
				FROM jobs
				WHERE source_id > ?
				ORDER BY source_id
				LIMIT ?
				""", (last_id, batch_size)).fetchall()
			if not rows:
				break

			last_id = rows[-1]["source_id"]
			for row in rows:
				skills = row["tech_stack"].split(', ')
				for skill in skills:
					cleaned = skill.strip().lower()
					if cleaned:
						tech_stack.add(cleaned)
	return tech_stack


# if __name__ == "__main__":
# 	print(find_skill_gaps("data/resume_d3.txt", "data/jobs.db"))
