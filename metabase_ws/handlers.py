import psycopg


async def FloorsList(pg_conn: str):
    async with await psycopg.AsyncConnection.connect(pg_conn) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT json_agg(
                    json_build_object(
                        'id', FLO.id,
                        'number', FLO.number,
                        'display_name', FLO.display_name,
                        'mime_type', FLO.mime_type,
                        'base64', FLO.base64,
                        'locations', (
                            SELECT json_agg(
                                json_build_object(
                                    'id', LOC.id,
                                    'code', LOC.code,
                                    'polygon_points', LOC.polygon_points
                                )
                            )
                            FROM mws_location LOC
                            WHERE LOC.floor_id = FLO.id
                        )
                    )
                )
                FROM mws_floor FLO;
            """
            )

            res = await cur.fetchall()

            return res[0][0] if res else []


async def FloorsSVG(
    number: int,
    pg_conn: str,
    overlord_host: str,
    overlord_username: str,
    overlord_password: str,
):
    from metabase_ws.remote import FetchQSales

    qsales = await FetchQSales(
        overlord_host, overlord_username, overlord_password
    )

    async with await psycopg.AsyncConnection.connect(pg_conn) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, base64 FROM mws_floor WHERE number = %s",
                (number,),
            )

            floor_rows = await cur.fetchall()

            if not len(floor_rows):
                raise ValueError(f"Floor {number} not found")

            floor_ids = [floor[0] for floor in floor_rows]

            await cur.execute(
                "SELECT code, polygon_points FROM mws_location WHERE floor_id = ANY(%s)",
                (floor_ids,),
            )

            location_rows = await cur.fetchall()

            if not len(location_rows):
                raise ValueError(f"Locations for floor {number} not found")

    qcodes = {
        "q1": {qs["pucp_id"] for qs in qsales["q1"]},
        "q2": {qs["pucp_id"] for qs in qsales["q2"]},
        "q3": {qs["pucp_id"] for qs in qsales["q3"]},
        "q4": {qs["pucp_id"] for qs in qsales["q4"]},
    }

    get_color = lambda code: (
        "red"
        if code in qcodes["q1"]
        else (
            "orange"
            if code in qcodes["q2"]
            else (
                "yellow"
                if code in qcodes["q3"]
                else "green" if code in qcodes["q4"] else "gray"
            )
        )
    )

    floor_base64 = floor_rows[0][1]
    width, height = await _GetPNGDims(floor_base64)

    polygon_info = (
        (row[0], row[1], get_color(int(row[0]))) for row in location_rows
    )

    content = bytearray()

    content.extend(
        f"""<?xml version="1.0" encoding="UTF-8"?>
        <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve">
          <image x="0" y="0" width="{width}" height="{height}" xlink:href="data:image/png;base64,{floor_base64}" />
        """.encode()
    )

    for title, points, color in polygon_info:
        content.extend(
            f"""
            <polygon title="{title}" points="{points}" fill="{color}" stroke="black" stroke-width="0"/>
            """.encode()
        )

    content.extend(b"</svg>")

    return bytes(content)


async def _GetPNGDims(b64: str):
    import base64
    import io

    from PIL import Image

    try:
        image = Image.open(io.BytesIO(base64.b64decode(b64)))
        width, height = image.size
    except Exception as error:
        raise ValueError(f"Failed to decode image: {error}")

    return width, height
