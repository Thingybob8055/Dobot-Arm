# Web based viewer for generated ,armcode files

This is just intended for testing generated armcode files.

Requires hosting with a http server due to browser security policies, a fast way to do this is to use the python http.server.
From the same directory as this readme, run the following command
```sh
python -m http.server
```
Then go to http://0.0.0.0:8000/ and attempt to open a saved armcode file