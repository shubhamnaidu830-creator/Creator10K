import pandas as pd
import sqlite3
import os

CSV_FILE = "data/top-500-most-subscribed-youtube-channels.csv"
DATABASE_FILE = "database/creators.db"

print("Reading dataset...")

df = pd.read_csv(CSV_FILE)

print(f"Rows found: {len(df)}")
print(f"Columns found: {len(df.columns)}")


# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------

df.columns = [
    column.strip()
    for column in df.columns
]


# -----------------------------
# RENAME COLUMNS
# -----------------------------

df = df.rename(columns={

    "Rank": "rank",

    "Channel ID": "channel_id",

    "Channel Name": "channel_name",

    "Subscribers": "subscribers",

    "Views": "views",

    "Country Code": "country_code",

    "Country": "country",

    "Topic Groups": "topic_groups",

    "Subtopics": "subtopics",

    "Profile URL": "profile_url",

    "Profile Picture URL": "profile_picture_url"

})


# -----------------------------
# REMOVE DUPLICATES
# -----------------------------

df = df.drop_duplicates(
    subset=["channel_id"]
)


# -----------------------------
# CONVERT NUMERIC COLUMNS
# -----------------------------

df["subscribers"] = pd.to_numeric(
    df["subscribers"],
    errors="coerce"
).fillna(0).astype("int64")


df["views"] = pd.to_numeric(
    df["views"],
    errors="coerce"
).fillna(0).astype("int64")


# -----------------------------
# CREATE OUR OWN DATABASE ID
# -----------------------------

df.insert(
    0,
    "id",
    range(1, len(df) + 1)
)


# -----------------------------
# CREATE DATABASE FOLDER
# -----------------------------

os.makedirs(
    "database",
    exist_ok=True
)


# -----------------------------
# CONNECT TO SQLITE
# -----------------------------

connection = sqlite3.connect(
    DATABASE_FILE
)


# -----------------------------
# SAVE DATABASE
# -----------------------------

df.to_sql(
    "creators",
    connection,
    if_exists="replace",
    index=False
)


connection.close()


print()
print("================================")
print("DATABASE CREATED SUCCESSFULLY")
print("================================")

print(f"Creators: {len(df)}")

print(
    f"Database: {DATABASE_FILE}"
)

print("Table: creators")

print()
print("ID column added successfully.")