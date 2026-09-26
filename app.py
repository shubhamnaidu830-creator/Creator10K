from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import requests
from datetime import datetime
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

DATABASE = "database/creators.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# YOUTUBE API
# =========================================================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def get_channel_data(channel_id):

    url = "https://www.googleapis.com/youtube/v3/channels"

    params = {

        "part":
            "snippet,statistics,contentDetails,"
            "brandingSettings,status,topicDetails",

        "id": channel_id,

        "key": YOUTUBE_API_KEY

    }

    response = requests.get(
        url,
        params=params
    )

    if response.status_code != 200:

        try:
            error_data = response.json()

        except Exception:

            error_data = {
                "error": response.text
            }

        return None, error_data


    data = response.json()


    if not data.get("items"):

        return None, {
            "error": "Channel not found"
        }


    return data["items"][0], None


# =========================================================
# SUBSCRIBER GROWTH
# =========================================================

def get_subscriber_growth_per_hour(channel_id):

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row


    rows = connection.execute("""
        SELECT
            subscriber_count,
            recorded_at
        FROM subscriber_history
        WHERE channel_id = ?
        ORDER BY recorded_at DESC
        LIMIT 2
    """, (channel_id,)).fetchall()


    connection.close()


    # Need at least two snapshots
    if len(rows) < 2:

        return None


    latest = rows[0]

    previous = rows[1]


    latest_count = latest["subscriber_count"]

    previous_count = previous["subscriber_count"]


    try:

        latest_time = datetime.fromisoformat(
            latest["recorded_at"]
        )

        previous_time = datetime.fromisoformat(
            previous["recorded_at"]
        )

    except ValueError:

        return None


    elapsed_seconds = (
        latest_time - previous_time
    ).total_seconds()


    if elapsed_seconds <= 0:

        return None


    elapsed_hours = (
        elapsed_seconds / 3600
    )


    growth = (
        latest_count - previous_count
    ) / elapsed_hours


    return round(growth)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# CREATOR PROFILE
# =========================================================

@app.route("/creator/<int:creator_id>")
def creator_profile(creator_id):

    connection = get_db()


    creator = connection.execute(
        """
        SELECT *
        FROM creators
        WHERE id = ?
        """,
        (creator_id,)
    ).fetchone()


    connection.close()


    if creator is None:

        return "Creator not found", 404


    creator = dict(creator)


    # -----------------------------------------------------
    # CHANNEL ID
    # -----------------------------------------------------

    channel_id = creator.get(
        "channel_id"
    )


    # -----------------------------------------------------
    # DEFAULT VALUES
    # -----------------------------------------------------

    youtube_data = None

    youtube_error = None

    subscriber_growth = None


    # -----------------------------------------------------
    # GET YOUTUBE DATA
    # -----------------------------------------------------

    if channel_id:

        youtube_data, youtube_error = (
            get_channel_data(
                channel_id
            )
        )


        # -------------------------------------------------
        # GET SUBSCRIBER GROWTH
        # -------------------------------------------------

        subscriber_growth = (
            get_subscriber_growth_per_hour(
                channel_id
            )
        )


    # -----------------------------------------------------
    # DEBUG INFORMATION
    # -----------------------------------------------------

    print("================================")

    print(
        "CHANNEL ID:",
        channel_id
    )

    print(
        "API KEY FOUND:",
        bool(YOUTUBE_API_KEY)
    )

    print(
        "YOUTUBE DATA:",
        youtube_data
    )

    print(
        "YOUTUBE ERROR:",
        youtube_error
    )

    print(
        "SUBSCRIBER GROWTH:",
        subscriber_growth
    )

    print("================================")


    # -----------------------------------------------------
    # SEND DATA TO HTML
    # -----------------------------------------------------

    return render_template(

        "creator.html",

        creator=creator,

        youtube=youtube_data,

        youtube_error=youtube_error,

        subscriber_growth=subscriber_growth

    )


# =========================================================
# GET CREATORS
# =========================================================

@app.route("/api/creators")
def get_creators():

    search = request.args.get(
        "search",
        ""
    ).strip()


    category = request.args.get(
        "category",
        ""
    ).strip()


    country = request.args.get(
        "country",
        ""
    ).strip()


    connection = get_db()


    query = """
        SELECT *
        FROM creators
        WHERE 1 = 1
    """


    parameters = []


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        query += """
            AND (
                channel_name LIKE ?
                OR channel_id LIKE ?
            )
        """


        search_value = (
            f"%{search}%"
        )


        parameters.extend([

            search_value,

            search_value

        ])


    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:

        query += """
            AND topic_groups LIKE ?
        """


        parameters.append(
            f"%{category}%"
        )


    # -----------------------------------------------------
    # COUNTRY FILTER
    # -----------------------------------------------------

    if country:

        query += """
            AND country = ?
        """


        parameters.append(
            country
        )


    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    query += """
        ORDER BY subscribers DESC
        LIMIT 100
    """


    creators = connection.execute(

        query,

        parameters

    ).fetchall()


    connection.close()


    return jsonify([

        dict(creator)

        for creator in creators

    ])


# =========================================================
# CATEGORIES
# =========================================================

@app.route("/api/categories")
def get_categories():

    connection = get_db()


    rows = connection.execute(
        """
        SELECT DISTINCT topic_groups
        FROM creators
        WHERE topic_groups IS NOT NULL
        AND topic_groups != ''
        ORDER BY topic_groups
        """
    ).fetchall()


    connection.close()


    categories = []


    for row in rows:

        value = row[
            "topic_groups"
        ]


        if value and value not in categories:

            categories.append(
                value
            )


    return jsonify(
        categories
    )


# =========================================================
# COUNTRIES
# =========================================================

@app.route("/api/countries")
def get_countries():

    connection = get_db()


    rows = connection.execute(
        """
        SELECT DISTINCT country
        FROM creators
        WHERE country IS NOT NULL
        AND country != ''
        ORDER BY country
        """
    ).fetchall()


    connection.close()


    return jsonify([

        row["country"]

        for row in rows

    ])


# =========================================================
# WEBSITE STATISTICS
# =========================================================

@app.route("/api/stats")
def get_stats():

    connection = get_db()


    # -----------------------------------------------------
    # TOTAL CREATORS
    # -----------------------------------------------------

    total_creators = connection.execute(
        """
        SELECT COUNT(*)
        FROM creators
        """
    ).fetchone()[0]


    # -----------------------------------------------------
    # TOTAL COUNTRIES
    # -----------------------------------------------------

    total_countries = connection.execute(
        """
        SELECT COUNT(DISTINCT country)
        FROM creators
        WHERE country IS NOT NULL
        """
    ).fetchone()[0]


    # -----------------------------------------------------
    # TOTAL CATEGORIES
    # -----------------------------------------------------

    total_categories = connection.execute(
        """
        SELECT COUNT(DISTINCT topic_groups)
        FROM creators
        WHERE topic_groups IS NOT NULL
        """
    ).fetchone()[0]


    # -----------------------------------------------------
    # TOTAL SUBSCRIBERS
    # -----------------------------------------------------

    total_subscribers = connection.execute(
        """
        SELECT SUM(subscribers)
        FROM creators
        """
    ).fetchone()[0]


    connection.close()


    return jsonify({

        "total_creators":
            total_creators,

        "total_countries":
            total_countries,

        "total_categories":
            total_categories,

        "total_subscribers":
            total_subscribers or 0

    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )

