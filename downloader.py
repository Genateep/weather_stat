import asyncio
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
            'SELECT * FROM statApp_onedaydata ORDER BY id DESC LIMIT 1'
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


def requester(cityname, start, end, api):
    """gets json data from request to source api
    """
    link = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
    dotenv.load_dotenv(dotenv.find_dotenv())
    payload = {
        "q": cityname,
        "tp": '24',
        "date": start,
        "enddate": end,
        "format": "json",
        "key": api
    }
    response = requests.get(link, params=payload)
    # print(response.json())
    return response.json()['data']['weather']


async def downloader(db, api, start_date, end_date):
    """saves received data with processed parameters to a table
    """
    async with db.execute("SELECT * FROM statApp_citylist") as cursor:
        async for city_row in cursor:
            try:
                weather = requester(city_row[1], start_date, end_date, api)
            except KeyError:  # in case of empty response at start of the day
                end_date -= timedelta(1)
                weather = requester(city_row[1], start_date, end_date, api)

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
                'INSERT INTO statApp_onedaydata values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                parameters
            )
            await db.commit()
            print(api, start_date, end_date, city_row[1], ' downloaded')


async def to_db():
    """checks db and gets updates from api
    """
    end_date = date.today()
    try:
        async with aiosqlite.connect('weather_history.db') as db:
            # checks db for last entry to start from
            latest_date = await get_latest_date(db)

            if latest_date == end_date:
                return
            elif latest_date == date(2010, 1, 1):
                start_date = latest_date
            else:
                start_date = latest_date + timedelta(1)

            # worldweatheronline-api provides up to 35 days data in one request only
            api = wwo_api_keys[randint(0, 5)]

            if (end_date - start_date).days <= 35:
                return await downloader(db, api, start_date, end_date)

            elif (end_date - start_date).days > 35:
                tasks = []

                while start_date < (end_date - timedelta(35)):
                    task = asyncio.create_task(downloader(db, wwo_api_keys[randint(0, 5)], start_date, end_date))
                    tasks.append(task)
                    start_date += timedelta(35)
                    # await asyncio.sleep(random.randrange(5, 30) / 100)
                tasks.append(asyncio.create_task(downloader(db, api, start_date, end_date)))
                await asyncio.gather(*tasks)

    except aiosqlite.Error as err:
        print("[SQLite ERROR]", err)


if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(to_db())
    print('time elapsed:', int(time.time() - start_time), 'sec')
