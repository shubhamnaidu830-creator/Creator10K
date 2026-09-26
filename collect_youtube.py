import sqlite3
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE = "database/creators.db"


# =========================================================
# YOUTUBE API KEY
# =========================================================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


# =========================================================
# SAVE SUBSCRIBER SNAPSHOT
# =========================================================

def save_subscriber_snapshot(channel_id, subscriber_count):

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        INSERT INTO subscriber_history
        (
            channel_id,
            subscriber_count,
            recorded_at
        )
        VALUES (?, ?, ?)
    """, (
        channel_id,
        subscriber_count,
        datetime.now()
    ))

    connection.commit()
    connection.close()


# =========================================================
# GET CHANNEL DATA
# =========================================================

def get_channel_data(channel_id):

    url = "https://www.googleapis.com/youtube/v3/channels"

    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(
        url,
        params=params
    )

    if response.status_code != 200:

        print(
            "YouTube API Error:",
            response.text
        )

        return None

    data = response.json()

    if not data.get("items"):

        print(
            "Channel not found:",
            channel_id
        )

        return None

    return data["items"][0]


# =========================================================
# COLLECT ALL CREATORS
# =========================================================

def collect_subscriber_data():

    connection = sqlite3.connect(DATABASE)

    creators = connection.execute("""
        SELECT channel_id
        FROM creators
        WHERE channel_id IS NOT NULL
        AND channel_id != ''
    """).fetchall()

    connection.close()

    print(
        f"Found {len(creators)} channels."
    )

    successful = 0

    for row in creators:

        channel_id = row[0]

        print(
            f"Collecting: {channel_id}"
        )

        youtube_data = get_channel_data(
            channel_id
        )

        if youtube_data:

            statistics = youtube_data.get(
                "statistics",
                {}
            )

            subscriber_count = statistics.get(
                "subscriberCount"
            )

            if subscriber_count:

                save_subscriber_snapshot(
                    channel_id,
                    int(subscriber_count)
                )

                successful += 1

                print(
                    f"Saved: {subscriber_count}"
                )

    print()
    print("==============================")
    print("COLLECTION COMPLETE")
    print("==============================")
    print(
        f"Successful: {successful}/{len(creators)}"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    collect_subscriber_data()