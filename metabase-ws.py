from dotenv import load_dotenv
from sanic import Sanic, json, response
from sanic.response import text

import metabase_ws.handlers

# Init Sanic
# ----------


load_dotenv()

app = Sanic("metabase-ws", env_prefix="MWS_")

cache = {}


# Management routes
# -----------------


@app.get("/health-check")
async def health_check(_):
    return text("⚕️")


# Web service routes
# ------------------


@app.get("/floors")
async def locations_list(_):
    content = await metabase_ws.handlers.FloorsList(app.config.PG_CONN)
    return json(content)


@app.get("/floors/<number:int>/svg")
async def floor_svg(_, number):
    cache_key = f"floor_svg_{number}"
    if cache_key in cache:
        return response.raw(cache[cache_key], content_type="image/svg+xml")

    content = await metabase_ws.handlers.FloorsSVG(
        number,
        app.config.PG_CONN,
        app.config.OVERLORD_HOST,
        app.config.OVERLORD_USERNAME,
        app.config.OVERLORD_PASSWORD,
    )

    cache[cache_key] = content

    return response.raw(content, content_type="image/svg+xml")
