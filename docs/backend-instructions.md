# Backend specific instructions

To setup particular backend you need to fill config.yaml.
There is a [doc](docs/config.md) about all supported config fields.

## discord

### input

1. Create application on [Discord Developer Portal](https://discord.com/developers/applications)
1. Copy bot token on "Bot" tab
1. Paste token to config.yaml

### output

1. Create discord webhook using [this](https://gist.github.com/jagrosh/5b1761213e33fc5b54ec7f6379034a22) instruction
1. Paste link to config.yaml

## matrix

1. Prepare bot user account
1. Run `python tools/matrix_e2ee.py` from discbridge directory
1. Follow instructions
1. Set in config.yaml:
    ```yaml
    store_path: backend_data/matrix/store
    credentials_json: backend_data/matrix/credentials.json
    ```
