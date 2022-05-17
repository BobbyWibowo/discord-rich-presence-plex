from services.config import config
from typing import Optional
from utils.logging import logger
import models.imgur
import requests

def uploadImage(url: str) -> Optional[str]:
	try:
		data: models.imgur.UploadResponse = requests.post(
			"https://api.imgur.com/3/image",
			headers = { "Authorization": f"Client-ID {config['display']['posters']['imgurClientID']}" },
			files = { "image": requests.get(url).content }
		).json()
		if not data["success"]:
			raise Exception(data["data"]["error"])
		if config['display']['posters']['useWeservProxy']:
			link = data["data"]["link"].replace("https://", "")
			return f"https://images.weserv.nl/?url={link}&w=128&h=128&fit=cover"
		else:
			return data["data"]["link"]
	except:
		logger.exception("An unexpected error occured while uploading an image")
