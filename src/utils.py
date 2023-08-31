import functools
import io
import re
import socket
import subprocess

from aiofauna import *


def random_port() -> int:
	"""Returns a random port number that is available for listening."""
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", 0))
	s.listen(1)
	port = s.getsockname()[1]
	s.close()
	return port

def parse_env_string(env: str) -> List[str]:
	"""Parses a string of environment variables into a list of strings."""
	return env.split(" ")


def nginx_config(name: str, port: int) -> str:
	"""Generates an nginx configuration file."""
	text = f"""
server {{
	listen 80;
	server_name { name }.aiofauna.com;

	location / {{
		proxy_pass http://localhost:{ port };
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "Upgrade";
	}}

	location /api/sse {{
		proxy_pass http://localhost:{ port };
		proxy_http_version 1.1;
		proxy_set_header Connection "";
		proxy_set_header Host $host;
		proxy_buffering off;
		proxy_cache off;
		proxy_ignore_headers "Cache-Control" "Expires";
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Scheme $scheme;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}}

	location /ws {{
		proxy_pass http://localhost:{ port };
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "Upgrade";
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Scheme $scheme;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}}
}}
"""
	for path in (
		"/etc/nginx/sites-enabled",
		"/etc/nginx/conf.d",
		"/etc/nginx/sites-available",
	):
		try:
			with open(f"{path}/{name}.conf", "w") as f:
				f.write(text)
		except FileNotFoundError:
			pass
	return subprocess.run(["nginx", "-s", "reload"], capture_output=True).stdout.decode(
		"utf-8"
	)

