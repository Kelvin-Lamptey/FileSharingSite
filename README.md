# Simple file sharing server

This small Flask app serves files from the `files/` directory and exposes them on the network so other devices on the same LAN can download them.

Quick start

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Run the server (default port 8000):

```bash
./start.sh
# or
python3 server.py --port 8000 --dir files
```

3. Open the printed Local or Network address in a browser. The app binds to `0.0.0.0`, so use the Network address (e.g. `http://192.168.1.42:8000`) from other devices.

Notes

- The server lists the top-level entries under `files/`; click a filename's "Download" button to download it.
- If you need to serve a different directory, pass `--dir <path>`.
