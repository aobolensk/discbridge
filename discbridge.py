#!/usr/bin/env python3
import argparse

from core import Core


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str, nargs="?", default="config.yaml", help="Path to config file")
    args = parser.parse_args()

    core = Core(args)
    core.run()


if __name__ == "__main__":
    main()
