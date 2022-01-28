import asyncio
import aiohttp
import os
import time
from datetime import date, timedelta
from random import randint

import aiosqlite
import dotenv
import requests

dotenv.load_dotenv(dotenv.find_dotenv())
wwo_api_keys = [
    os.environ['WWO_API'],
    os.environ['WWO_API2'],
    os.environ['WWO_API3'],
    os.environ['WWO_API4'],
    os.environ['WWO_API5'],
    os.environ['WWO_API6']
]


async def get_latest_date(db):
    """gets latest date from db
    """
    async with db.execute(
            'SELECT * FROM statApp_onedaydata ORDER BY date DESC LIMIT 1'
    ) as cursor:
        latest_saved = await cursor.fetchone()

    if not latest_saved:
        latest_date = date(2010, 1, 1)
    else:
        latest_date = date(
            int(latest_saved[1][:4]),
            int(latest_saved[1][5:7]),
            int(latest_saved[1][8:])
        )
    return latest_date


async def writer(db, city_row, weather):
    """saves received data with processed parameters
    """
    parameters = []

    for day in weather:
        parameters.append((
            None,
            day['date'],
            day['maxtempC'],
            day['mintempC'],
            day['avgtempC'],
            day['hourly'][0]['windspeedKmph'],
            day['hourly'][0]['winddir16Point'],
            day['hourly'][0]['precipMM'],
            day['hourly'][0]['weatherDesc'][0]['value'],
            city_row[0]
        ))
    await db.executemany(
        'INSERT INTO statApp_onedaydata values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',  # noqa
        parameters
    )
    await db.commit()
    print(city_row[1], 'updated to', parameters[-1][1])


async def requester(session, db, start_date, end_date, api):
    """gets bunch of json data from api and sends it to db writer
    """
    async with db.execute("SELECT * FROM statApp_citylist") as cursor:
        async for city_row in cursor:
            url = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"  # noqa
            payload = {
                "q": city_row[1],
                "tp": '24',
                "date": str(start_date),
                "enddate": str(end_date),
                "format": "json",
                "key": api
            }
            async with session.get(url, params=payload) as resp:
                resp_text = await resp.json()

                try:
                    weather = resp_text['data']['weather']
                except KeyError as e:
                    print(e, resp_text)

                await writer(db, city_row, weather)

            await asyncio.sleep(randint(5, 30) / 100)


async def db_updater():
    """checks db and gets updates.
    Api provides up to 35 days data in one request only,
    therefore requests are divided into 35 day periods
    """
    end_date = date.today()
    try:
        async with aiosqlite.connect('weather_history.db') as db:

            latest_date = await get_latest_date(db)

            if latest_date == end_date:
                return
            elif latest_date == date(2010, 1, 1):
                start_date = latest_date
            else:
                start_date = latest_date + timedelta(1)

            async with aiohttp.ClientSession() as session:
                if (end_date - start_date).days <= 35:
                    return await requester(
                        session,
                        db,
                        start_date,
                        end_date,
                        wwo_api_keys[randint(0, 5)]
                    )

                elif (end_date - start_date).days > 35:
                    tasks = []

                    while start_date < (end_date - timedelta(35)):
                        task = asyncio.create_task(
                            requester(
                                session,
                                db,
                                start_date,
                                end_date,
                                wwo_api_keys[randint(0, 5)]
                            )
                        )
                        tasks.append(task)
                        start_date += timedelta(35)

                    tasks.append(
                        asyncio.create_task(
                            requester(
                                session,
                                db,
                                start_date,
                                end_date,
                                wwo_api_keys[randint(0, 5)]
                            )
                        )
                    )
                    await asyncio.gather(*tasks)

    except aiosqlite.Error as err:
        print("[SQLite ERROR]", err)


if __name__ == '__main__':
    start_time = time.time()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(db_updater())

    print(round(time.time() - start_time, 2), 'sec elapsed')
