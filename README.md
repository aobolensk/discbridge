# discbridge

How to run:
```console
$ python3 -m pip install -r requirements.txt
$ python3 discbridge.py
```

Config (create `config.yaml` file):
```yaml
input:
  telegram:
    token: <token>
    chat_filter: false
    chat_ids: []
  discord:
    token: <token>
    chat_filter: false
    chat_ids: []
output:
  discord:
    webhook_link: <link>
  telegram:
    token: <token>
    chat_id: 0
```
