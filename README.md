# discbridge

How to run:
```console
$ python3 -m pip install -r requirements.txt
$ python3 discbridge.py
```

### Config (create `config.yaml` file):

Note: All input and output values are optional.
If you do not need any backend just omit corresponding part of config.

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
  email:
    email: <sender_email>
    password: <sender_email_password>
    smtp_server: <sender_email_smtp_server>
    to_addrs:
      - <destination_email_address>
    cc_addrs:
      - <destination_email_address>
    bcc_addrs:
      - <destination_email_address>
    subject: <subject>
  matrix:
    server: <matrix_host_link>
    user: <username>
    password: <password>
    room_id: <matrix_room_id> # Looks like: !opaque_id:domain
```
