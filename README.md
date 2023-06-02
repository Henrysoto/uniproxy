# UniProxy
This project is still under development.

UniProxy was created to fetch UniFi's cameras snapshot and stream it through HTTP. That was needed for using these images in TPControl (AMX user interface product). TPControl cannot authenticate on something else than basic http authentication method and cannot read RTSP/RTSPS stream, it can only make requests to HTTP or HTTPS URLs.

# Functionalities
- User registration / login
- Cameras are sorted by Projects (Create a project then add cameras to it)
- Check cameras status (online or not)

# Requirements
- Cameras must be accessible from external IP or though a VPN. If you are running UniProxy on a local network with cameras on the same network, it will work. If you run UniProxy on an external server and try to reach camera from another destination, you will need to open ports on your router and provide your external IP to UniProxy when adding camera to your project.

# Dependencies
- Flask
- sqlite3

# How-to
Initialize sqlite database file:
```
flask --app uniproxy init-db
```
Start UniProxy instance:
```
flask --app uniproxy run
```

Make sure to edit `__init__.py` if you want UniProxy to be accessible from outside your local network.
