# thinq2-python

This is a reverse-engineered client for the LG ThinQ v2 IoT protocol. 

If you are working with v1 devices, try [wideq](https://github.com/sampsyo/wideq),
which inspired this project.

## Work in progress!

This is very much a **work in progress**.

There are no unit tests, there is no documentation, there is no defined API and
breaking changes are almost guaranteed to happen. Fun times!

## Development

This project uses [poetry](https://python-poetry.org/) for dependency management.

To configure a development environment, run `poetry install`.

## Running the Example

There is currently no documentation, but you can use `example.py` to demo the
codebase, and its code shows basic usage. The `COUNTRY_CODE` and `LANGUAGE_CODE`
environment variables should be set appropriately on first invocation in order
to bootstrap the client. These will be stored in state for future invocations.

Example:

    poetry install
    COUNTRY_CODE=US LANGUAGE_CODE=en-US poetry run python example.py

Example (Windows Powershell):

    $env:COUNTRY_CODE=US
    $env:LANGUAGE_CODE=en-US
    poetry run python example.py

The example script will bootstrap the application state on first run, walking
you through the OAuth flow. If authentication succeeds, you should see a
display of basic account information and a list of your ThinQv2 devices. The
script will then begin dumping device events received via MQTT. Try turning
devices on/off or otherwise changing their state, and you should see raw events
being sent.


## Contributing

As this is an early stage prototype, no contribution guidelines are available,
but help is always welcome!
