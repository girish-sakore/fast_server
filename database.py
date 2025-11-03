from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime
from databases import Database
from config import DATABASE_URL

# Initialize database connection
database = Database(DATABASE_URL)
metadata = MetaData()

# Define the QR visits table
qr_visits = Table(
    "qr_visits",
    metadata,
    Column("source", String, nullable=False),
    Column("timestamp", DateTime, nullable=False),
    Column("useragent", String, nullable=False),
    Column("pagepath", String, nullable=False),
)

# Create the database engine
engine = create_engine(DATABASE_URL)
# metadata.create_all(engine)