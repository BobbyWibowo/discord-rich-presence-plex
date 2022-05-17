from services.config import config
from typing import Any, Optional
from utils.logging import logger
import models.imgur
import os
import re
import requests

def json_get(_dict: dict, key: Optional[str], default: Any = None) -> Any:
	if key == None:
		return default
	segments = key.split('.')
	base: dict = _dict
	for seg in segments:
		index = None
		match = re.match("^(.*)\[(\d+)\]$", seg)
		if match:
			seg = match.group(1)
			index = int(match.group(2))
		if seg not in base:  # this assumes a valid "mapping path"
			logger.debug(f"No value for key {key!r}")
			return default
		base = base[seg]
		if type(index) is int and index >= 0:
			base = base[index]
	logger.debug(f"Value for {key!r}: {base!r}")
	return base

def uploadImage(url: str) -> Optional[str]:
	try:
		customHost = config['display']['posters']['customHost']
		if customHost['enabled']:
			logger.debug("Fetching album cover")
			s = requests.get(url)
			image = s.content

			filename = os.path.basename(url)
			if "content-type" in s.headers:
				if "jpg" in s.headers['content-type'] or "jpeg" in s.headers['content-type']:
					filename += ".jpg"
				elif "png" in s.headers['content-type']:
					filename += ".png"

			logger.debug("Uploading album cover to custom host")
			data = requests.post(
				customHost['api'],
				headers = customHost['headers'] or {},
				files = { customHost['field']: (filename, image) }
			)
			if customHost['jsonKeys']:
				data = data.json()
				if customHost['jsonKeys']['status']:
					status = json_get(data, customHost['jsonKeys']['status'])
					if not status:
						if customHost['jsonKeys']['description']:
							raise Exception(json_get(data, customHost['jsonKeys']['description']))
						else:
							raise Exception(data)
				return json_get(data, customHost['jsonKeys']['result'])
			else:
				return data
		else:
			logger.debug("Uploading album cover to Imgur")
			data: models.imgur.UploadResponse = requests.post(
				"https://api.imgur.com/3/image",
				headers = { "Authorization": f"Client-ID {config['display']['posters']['imgurClientID']}" },
				files = { "image": requests.get(url).content }
			).json()
			if not data["success"]:
				raise Exception(data["data"]["error"])
			return data["data"]["link"]
	except:
		logger.exception("An unexpected error occured while uploading an image")
