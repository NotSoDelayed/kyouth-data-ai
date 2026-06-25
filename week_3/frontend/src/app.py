from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")


@app.get("/")
async def root(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="chat_page.html"
	)
