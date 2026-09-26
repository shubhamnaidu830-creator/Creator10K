import sqlite3
import os

DATABASE = "database/creators.db"


def create_subscriber_history_table():

    os.makedirs("database", exist_ok=True)

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS subscriber_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            channel_id TEXT NOT NULL,

            subscriber_count INTEGER NOT NULL,

            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    connection.commit()
    connection.close()

    print("Subscriber history table created successfully.")


if __name__ == "__main__":
    create_subscriber_history_table()