# Dobot Arm control via EEG

This is the dobot arm side over the Mind Over Matter RES project for display at the Royal Society.

Before use, I recommend setting up a Python virtual environment and then installing the required packages.

## Setup
First ensure you are in the same directory as this readme file in an open terminal and run the following shell
commands.

Create a python virtual environment for a separate local version of Python to be added to this project. This helps stop
your system being polluted with many packages and to avoid version conflicts between different projects you are
working on.
```sh
python -m venv env
```

Activate the new virtual environment to use the local version of Python that was created.
```sh
source env/bin/activate
```

Install the required dependencies to the now activated virtual environment
```
python -m pip install -r requirements.txt
```

## Run
There are two packages used for starting a server to listen to the incoming UDP connection from the speller, both need
to be run separately and at the same time.

### UDP Server
To start the UDP server so it can be ready to take incoming connections from the speller cap there are a few steps
to follow:
1. Ensure the setup instructions have been followed previously first
2. Open a terminal to the same directory as this readme file
3. Source the local version of Python that was used in the installation
```sh
source env/bin/activate
```
4. Start the server
```sh
python server
```

The UDP server will accept strings to print via the network. Upon receipt it will generate an armcode file that will
be placed in a generated queue/ directory. The armcode files are to be output by the controller, but can also be
viewed using the optional web viewer, see web-renderer/ if this is what you would like to do.

### Dobot Controller
This controller takes armcode files from the queue/ directory and will use them to drive a connected dobot robotic arm.
The armcode files contain a description of how to draw the rendered objects/text using a pen and the robotic arm. The
controller will run until an armcode file is found, in which case it will output them in first to last date order.

To run the controller, the steps are similar to the UDP server:
1. Ensure the setup instructions have been followed previously first
2. Open a terminal to the same directory as this readme file
3. Source the local version of Python that was used in the installation
```sh
source env/bin/activate
```
4. Start the server
```sh
python controller
```
