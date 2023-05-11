---
title: "Flask scheduled actions example code"
---

**Main.py**

```py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, Space!"

@app.route('/__space/v0/actions', methods=['POST'])
def actions():
  data = request.get_json()
  event = data['event']
  if event['id'] == 'cleanup':
    cleanup()
```

**Spacefile**

```yml
# Spacefile Docs: https://go.deta.dev/docs/spacefile/v0
v: 0
micros:
  - name: my-app
    src: .
    engine: python3.9
    run: gunicorn main:app
    actions:
      - id: "cleanup"
        name: "Clean Up"
        description: "Cleans up unused data"
        trigger: "schedule"
        default_interval: "0/15 * * * *"
```
