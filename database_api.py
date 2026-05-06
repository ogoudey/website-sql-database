import mysql.connector

# --- Config ---
DB_CONFIG = {
    "host": "myproject.db",
    "user": "youruser",
    "password": "yourpassword",
    "database": "mydb",
}


# --- App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down to your frontend domain later
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()