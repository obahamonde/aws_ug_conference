from aiofauna import *
from aiohttp.web import HTTPFound

from src import *

app = APIServer()

@app.get("/")
async def index():
	return HTTPFound("/docs")

@app.get("/api/functions")
async def functions():
	clss = OpenAIFunction.Metadata.subclasses
	return [i.openaischema for i in clss]

@app.get("/api/")
async def ifft_gpt(text:str):
	return await function_call(text)

@app.get("/api/audio/{text}")
async def audio_endpoint(text: str):
	options = await Voice.assign(text=text)
	language = [option.LanguageCode for option in options][0]
	app.logger.info(f"Selected language {language}")
	polly = Polly(Text=text, LanguageCode=language)

	async def generator():
		async for chunk in polly.stream_audio():
			yield chunk

	return Response(body=generator(), headers={"Content-Type": "audio/mpeg"})