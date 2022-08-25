### Config (create `config.yaml` file):

Note: All input and output values are optional.
If you do not need any backend just omit corresponding part of config.
There is a [doc](docs/backend-instructions.md) about backend specific details.

```yaml
input:
  telegram:
    token: <token>
    chat_filter: false            # optional
    chat_ids: []                  # optional
    polling_interval: 600         # optional
    user_blocklist: false         # optional
    user_blocklist_ids: []        # optional
    user_allowlist: false         # optional
    user_allowlist_ids: []        # optional
    proxy: false                  # optional
  discord:
    token: <token>
    chat_filter: false            # optional
    chat_ids: []                  # optional
    proxy: false                  # optional
  email:
    imap_server: <receiver_email_imap_server>
    email: <email>
    password: <password>
    check_interval: 60            # optional
  matrix:
    store_path: <store_path>
    credentials_json: <path_to_json>
    password: <user_password>
    room_id: <matrix_room_id>     # Looks like: !opaque_id:domain
    user_blocklist: false         # optional
    user_blocklist_names: []      # optional
    user_allowlist: false         # optional
    user_allowlist_names: []      # optional
    proxy: false                  # optional
output:
  discord:
    webhook_link: <link>
    proxy: false                  # optional
  telegram:
    token: <token>
    chat_id: 0
    proxy: false                  # optional
  email:
    email: <sender_email>
    password: <sender_email_password>
    smtp_server: <sender_email_smtp_server>
    subject: <subject>
    to_addrs:                     # optional
      - <destination_email_address>
    cc_addrs:                     # optional
      - <destination_email_address>
    bcc_addrs:                    # optional
      - <destination_email_address>
  matrix:
    store_path: <store_path>
    credentials_json: <path_to_json>
    password: <user_password>
    room_id: <matrix_room_id>     # Looks like: !opaque_id:domain
    proxy: false                  # optional
```

It is possible to add multiple input and output configurations.
You can add them using the following pattern: `<input/output_name>.<custom_name>` (e.g. `telegram.main` or `email.test`).
First part should be backend type the second part (after dot) is custom name which is up to user.

Example:

```yaml
input:
  telegram.1:
    token: <token>
    chat_filter: false
    chat_ids: []
  telegram.2:
    token: <token>
    chat_filter: false
    chat_ids: []
```
