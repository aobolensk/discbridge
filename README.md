# discbridge

How to run:
```console
$ python3 -m pip install -r requirements.txt
$ python3 discbridge.py
```

Config:
```json
{
    "input": {
        "telegram": {
            "token": "",
            "chat_filter": true,
            "chat_ids": []
        }
    },
    "output": {
        "discord": {
            "webhook_link": ""
        },
        "telegram": {
            "token": "",
            "chat_id": 0
        }
    }
}
```
