ere are the canonical docs, grouped by the step they show up in on sheet 03. Standard-library links are docs.python.org (rock-stable); third-party I've pointed at the official source for each.

00 · Status contract

dataclasses — https://docs.python.org/3/library/dataclasses.html
enum — https://docs.python.org/3/library/enum.html
datetime — https://docs.python.org/3/library/datetime.html
json — https://docs.python.org/3/library/json.html
pydantic (the upgrade path) — https://docs.pydantic.dev/latest/

01 · Ingest

sqlite3 — https://docs.python.org/3/library/sqlite3.html
pathlib — https://docs.python.org/3/library/pathlib.html
re — https://docs.python.org/3/library/re.html
ipaddress — https://docs.python.org/3/library/ipaddress.html
socketserver — https://docs.python.org/3/library/socketserver.html
Pi-hole FTL database schema (verify the status codes here) — https://docs.pi-hole.net/database/ftl/
pfSense raw filter log format — https://docs.netgate.com/pfsense/en/latest/monitoring/logs/raw-filter-format.html

02 · Detect

collections (deque, Counter, defaultdict) — https://docs.python.org/3/library/collections.html
ipaddress — https://docs.python.org/3/library/ipaddress.html

03 · Terminal output

rich — https://rich.readthedocs.io/
colorama (alt) — https://pypi.org/project/colorama/

04 · Web layer

FastAPI, WebSockets page specifically — https://fastapi.tiangolo.com/advanced/websockets/
Uvicorn — https://www.uvicorn.org/
websockets — https://websockets.readthedocs.io/

05 · More detections + config

PyYAML — https://pyyaml.org/wiki/PyYAMLDocumentation
APScheduler — https://apscheduler.readthedocs.io/

06 · Health + Prometheus

prometheus_client (docs) — https://prometheus.github.io/client_python · repo — https://github.com/prometheus/client_python 
SageMath
psutil — https://psutil.readthedocs.io/
httpx — https://www.python-httpx.org/
socket — https://docs.python.org/3/library/socket.html

07 · LLM analyst

ollama-python (official library) — https://github.com/ollama/ollama-python 
GitHub
Ollama REST API reference — https://docs.ollama.com/api/introduction

08 · Mascot glow

Adafruit NeoPixel (CircuitPython) — https://docs.circuitpython.org/projects/neopixel/en/latest/
websockets client — https://websockets.readthedocs.io/

Cross-cutting

asyncio — https://docs.python.org/3/library/asyncio.html · asyncio.Queue — https://docs.python.org/3/library/asyncio-queue.html
logging — https://docs.python.org/3/library/logging.html
python-dotenv — https://github.com/theskumar/python-dotenv
pytest — https://docs.pytest.org/

Three honest accuracy flags while I had the docs open:

The APScheduler snippet on the sheet (BackgroundScheduler(...).add_job(..., 'interval')) is the v3 API. There's now a v4 on master with a different Scheduler API, so pin to the 3.x docs for the code as written: https://apscheduler.readthedocs.io/en/3.x/ — or use v4 and follow its newer guide. 
APScheduler

The Ollama call is ollama.chat(model=..., messages=[...]), and the response is accessed as response['message']['content'] or response.message.content — matches what's on the sheet. 
GitHub

And the one I already flagged: those Pi-hole blocked status codes — confirm them against the FTL schema doc above plus a SELECT DISTINCT status FROM queries on your box, since they've shifted across FTL versions.