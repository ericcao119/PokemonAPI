from sanic import Sanic
from sanic.exceptions import NotFound, ServerError
from sanic.request import Request
from sanic.websocket import WebSocketProtocol, ConnectionClosed
from sanic.response import html, json
from asyncio import Event, ensure_future
from json import dumps as json_string
from jinja2 import Environment, FileSystemLoader
from loguru import logger

import argparse

# Set up a logfile for the sake of debugging/DDoS forensics/postmortems
logger.add("output.log", rotation="500 MB")

app = Sanic(configure_logging=False)
# Use WebSockets to live-update the index page
app.enable_websocket()
# Static bindings allow Sanic to serve files from disk
# These are explicitly named to avoid someone accidentally placing something secret in one of these folders

# CSS
app.static(
    "/assets/css/fontawesome-all.min.css", "./res/assets/css/fontawesome-all.min.css"
)
app.static("/assets/css/main.css", "./res/assets/css/main.css")
app.static("/assets/css/noscript.css", "./res/assets/css/noscript.css")

# JS
app.static("/assets/js/breakpoints.min.js", "./res/assets/js/breakpoints.min.js")
app.static("/assets/js/browser.min.js", "./res/assets/js/browser.min.js")
app.static("/assets/js/jquery.min.js", "./res/assets/js/jquery.min.js")
app.static("/assets/js/main.js", "./res/assets/js/main.js")
app.static("/assets/js/util.js", "./res/assets/js/util.js")

# Third Party libraries
# Highlight js
app.static(
    "/assets/thirdparty/highlight/highlight.pack.js",
    "./res/assets/thirdparty/highlight/highlight.pack.js",
)
app.static(
    "/assets/thirdparty/highlight/styles/dracula.css",
    "./res/assets/thirdparty/highlight/styles/dracula.css",
)


# HTML
# app.static('/res/index.html', './res/index.html')

# Images
app.static("/pokeball.svg", "./res/pokeball.svg")
app.static("/favicon.ico", "./res/favicon.ico")


env = Environment(loader=FileSystemLoader(["./res/templates", "./res/code"]))

# Load page templates - it should be easy to change these templates later.
# These are loaded once at the start of the program, and never again.
# with open("res/index.html") as f:
#     index_template = Template(f.read())
index_template = env.get_template("index.html")


@app.route("/")
async def index(request: Request):
    logger.info(f"Client at {request.ip}:{request.port} requested {request.url}.")
    # We need to wait for Sanic to do the first asyncio call, because Sanic uses a different loop than Python by default.
    # The tournament therefore starts the first time the page is loaded.
    # if not rr.active:
    #     logger.info(f"Tournament not running - starting it now.")
    #     ensure_future(rr.git_live())
    #     ensure_future(rr.run_queue())
    # index_html = index_template.render(
    #     standings=rr.get_standings(),
    #     games=rr.get_games(),
    #     last_match=rr.get_video(),
    #     queue_status=rr.get_queue(),
    # )

    index_html = index_template.render()
    return html(index_html)


# @app.websocket("/ws/feed")
# async def feed_socket(request: Request, ws: WebSocketProtocol):
#     logger.info(
#         f"Client at {request.ip}:{request.port} opened websocket at {request.url}.")
#     # This is the WebSocket code.
#     # It infinite loops (until the socket is closed when the client disconnects...) and waits on new matches.
#     # When a new match is found, it sends a JSON blob containing the tournament data.
#     while True:
#         json_blob = {"standings": rr.get_standings(), "games": rr.get_games(
#         ), "last_video": rr.get_video(), "queue_status": rr.get_queue()}
#         binary_blob = json_string(json_blob)
#         try:
#             await ws.send(binary_blob)
#             logger.info(
#                 f"Updated feed for client at {request.ip}:{request.port}.")
#         except ConnectionClosed:
#             logger.info(
#                 f"Feed disconnected from client at {request.ip}:{request.port}.")
#             break
#         await rr.update()


# async def ise_handler(request, exception):
#     # Handle internal server errors by displaying a custom error page.
#     return html(ise_template.render(), status=500)


# async def missing_handler(request, exception):
#     # Handle 404s by displaying a custom error page.
#     return html(missing_template.render(), status=404)


# app.error_handler.add(ServerError, ise_handler)
# app.error_handler.add(NotFound, missing_handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple website server.")
    parser.add_argument(
        "--port",
        dest="port",
        action="store",
        default=8000,
        type=int,
        help="sum the integers (default: find the max)",
    )

    args = parser.parse_args()

    try:
        port = int(args.port)
    except ValueError:
        print("Invalid port specified")
        exit()
    app.run(host="0.0.0.0", port=port)
