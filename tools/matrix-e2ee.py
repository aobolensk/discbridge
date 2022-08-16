# Based on matrix-nio documentation:
# https://matrix-nio.readthedocs.io/en/latest/examples.html#interactive-encryption-key-verification

import asyncio
import getpass
import json
import os
import sys
import traceback

from nio import (AsyncClient, AsyncClientConfig, KeyVerificationCancel,
                 KeyVerificationEvent, KeyVerificationKey, KeyVerificationMac,
                 KeyVerificationStart, LocalProtocolError, LoginResponse,
                 ToDeviceError)

CONFIG_FILE = "./backend_data/matrix/credentials.json"  # login credentials JSON file
# directory to store persistent data for end-to-end encryption
STORE_PATH = "./backend_data/matrix/store/"  # local directory


class Callbacks(object):
    def __init__(self, client):
        self._client = client

    async def to_device_callback(self, event):  # noqa
        """Handle events sent to device."""
        try:
            client = self._client

            if isinstance(event, KeyVerificationStart):
                if "emoji" not in event.short_authentication_string:
                    print(
                        "Other device does not support emoji verification "
                        f"{event.short_authentication_string}."
                    )
                    return
                resp = await client.accept_key_verification(event.transaction_id)
                if isinstance(resp, ToDeviceError):
                    print(f"accept_key_verification failed with {resp}")

                sas = client.key_verifications[event.transaction_id]

                todevice_msg = sas.share_key()
                resp = await client.to_device(todevice_msg)
                if isinstance(resp, ToDeviceError):
                    print(f"to_device failed with {resp}")

            elif isinstance(event, KeyVerificationCancel):  # anytime
                print(
                    f"Verification has been cancelled by {event.sender} "
                    f'for reason "{event.reason}".'
                )

            elif isinstance(event, KeyVerificationKey):  # second step
                sas = client.key_verifications[event.transaction_id]
                print(f"{sas.get_emoji()}")

                yn = input("Do the emojis match? (Y/N) (C for Cancel) ")
                if yn.lower() == "y":
                    print(
                        "Match! The verification for this " "device will be accepted."
                    )
                    resp = await client.confirm_short_auth_string(event.transaction_id)
                    if isinstance(resp, ToDeviceError):
                        print(f"confirm_short_auth_string failed with {resp}")
                elif yn.lower() == "n":  # no, don't match, reject
                    print(
                        "No match! Device will NOT be verified "
                        "by rejecting verification."
                    )
                    resp = await client.cancel_key_verification(
                        event.transaction_id, reject=True
                    )
                    if isinstance(resp, ToDeviceError):
                        print(f"cancel_key_verification failed with {resp}")
                else:  # C or anything for cancel
                    print("Cancelled by user! Verification will be " "cancelled.")
                    resp = await client.cancel_key_verification(
                        event.transaction_id, reject=False
                    )
                    if isinstance(resp, ToDeviceError):
                        print(f"cancel_key_verification failed with {resp}")

            elif isinstance(event, KeyVerificationMac):  # third step
                sas = client.key_verifications[event.transaction_id]
                try:
                    todevice_msg = sas.get_mac()
                except LocalProtocolError as e:
                    # e.g. it might have been cancelled by ourselves
                    print(
                        f"Cancelled or protocol error: Reason: {e}.\n"
                        f"Verification with {event.sender} not concluded. "
                        "Try again?"
                    )
                else:
                    resp = await client.to_device(todevice_msg)
                    if isinstance(resp, ToDeviceError):
                        print(f"to_device failed with {resp}")
                    print(
                        f"sas.we_started_it = {sas.we_started_it}\n"
                        f"sas.sas_accepted = {sas.sas_accepted}\n"
                        f"sas.canceled = {sas.canceled}\n"
                        f"sas.timed_out = {sas.timed_out}\n"
                        f"sas.verified = {sas.verified}\n"
                        f"sas.verified_devices = {sas.verified_devices}\n"
                    )
                    print("Emoji verification was successful!")
                    sys.exit(0)
            else:
                print(
                    f"Received unexpected event type {type(event)}. "
                    f"Event is {event}. Event will be ignored."
                )
        except BaseException:
            print(traceback.format_exc())


def write_details_to_disk(resp: LoginResponse, homeserver) -> None:
    # open the config file in write-mode
    with open(CONFIG_FILE, "w") as f:
        # write the login details to disk
        json.dump(
            {
                "homeserver": homeserver,  # e.g. "https://matrix.example.org"
                "user_id": resp.user_id,  # e.g. "@user:example.org"
                "device_id": resp.device_id,  # device ID, 10 uppercase letters
                "access_token": resp.access_token,  # cryptogr. access token
            },
            f,
        )


async def login() -> AsyncClient:
    # Configuration options for the AsyncClient
    client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
        encryption_enabled=True,
    )

    # If there are no previously-saved credentials, we'll use the password
    if not os.path.exists(CONFIG_FILE):
        print(
            "First time use. Did not find credential file. Asking for "
            "homeserver, user, and password to create credential file."
        )
        homeserver = "https://matrix.example.org"
        homeserver = input(f"Enter your homeserver URL: [{homeserver}] ")

        if not (homeserver.startswith("https://") or homeserver.startswith("http://")):
            homeserver = "https://" + homeserver

        user_id = "@user:example.org"
        user_id = input(f"Enter your full user ID: [{user_id}] ")

        device_name = "matrix-nio"
        device_name = input(f"Choose a name for this device: [{device_name}] ")

        if not os.path.exists(STORE_PATH):
            os.makedirs(STORE_PATH)

        # Initialize the matrix client
        client = AsyncClient(
            homeserver,
            user_id,
            store_path=STORE_PATH,
            config=client_config,
        )
        pw = getpass.getpass()

        resp = await client.login(password=pw, device_name=device_name)

        # check that we logged in succesfully
        if isinstance(resp, LoginResponse):
            write_details_to_disk(resp, homeserver)
        else:
            print(f'homeserver = "{homeserver}"; user = "{user_id}"')
            print(f"Failed to log in: {resp}")
            sys.exit(1)

        print(
            "Logged in using a password. Credentials were stored. "
            "On next execution the stored login credentials will be used."
        )

    # Otherwise the config file exists, so we'll use the stored credentials
    else:
        # open the file in read-only mode
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Initialize the matrix client based on credentials from file
            client = AsyncClient(
                config["homeserver"],
                config["user_id"],
                device_id=config["device_id"],
                store_path=STORE_PATH,
                config=client_config,
            )

            client.restore_login(
                user_id=config["user_id"],
                device_id=config["device_id"],
                access_token=config["access_token"],
            )
        print("Logged in using stored credentials.")

    return client


async def main() -> None:
    """Login and wait for and perform emoji verify."""
    client = await login()
    # Set up event callbacks
    callbacks = Callbacks(client)
    client.add_to_device_callback(callbacks.to_device_callback, (KeyVerificationEvent,))
    # Sync encryption keys with the server
    # Required for participating in encrypted rooms
    if client.should_upload_keys:
        await client.keys_upload()
    print(
        "This program is ready and waiting for the other party to initiate "
        'an emoji verification with us by selecting "Verify by Emoji" '
        "in their Matrix client."
    )
    await client.sync_forever(timeout=30000, full_state=True)


try:
    asyncio.get_event_loop().run_until_complete(main())
except Exception:
    print(traceback.format_exc())
    sys.exit(1)
except KeyboardInterrupt:
    print("Received keyboard interrupt.")
    sys.exit(0)
