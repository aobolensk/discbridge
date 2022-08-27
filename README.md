# discbridge

discbridge allows you to bridge your messages between [different messenger platforms](docs/support-table.md).

## Requirements:

- [Python](https://www.python.org/) 3.8-3.10
- [libolm](https://gitlab.matrix.org/matrix-org/olm)

  Ubuntu/Debian:
  ```
  $ sudo apt install libolm-dev python3-olm
  ```

## How to run:
```console
$ python3 -m pip install -r requirements.txt
$ python3 discbridge.py
```

Setup config.yaml file following the [tutorial](docs/config.md).
You need to use credentials for your bots to run the bridge.
Use Ctrl+C to stop.

## FAQ

Config setup: [Read](docs/config.md)<br>
What platforms are supported? [Read](docs/support-table.md)<br>
How to setup platform X? [Read](docs/backend-instructions.md)<br>
