import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime

# Database connection
db_url = "postgresql://postgres:yourpassword@localhost:5432/fire_db"
engine = create_engine(db_url)


def extract_timestamp(filename):
    try:
        # Find the first occurrence of a timestamp in the filename
        parts = filename.split("_")
        for part in parts:
            print("PART", part)
            if "T" in part and "." in part:
                return datetime.strptime(part, "%Y-%m-%dT%H%M%S.%fZ")
    except Exception as e:
        print(f"Error extracting timestamp from {filename}: {e}")

    return None  # Return None if no valid timestamp is found


# Function to extract timestamp from filename
# def extract_timestamp(filename):
#     # Extract the part after "acquisition_" (assuming format is "F002_L2_FIRE____acquisition_XXX_XXX.csv")
#     try:
#         timestamp_str = filename.split("acquisition_")[1].split(".csv")[0]
#         timestamp = datetime.strptime(timestamp_str, "%Y%m%dT%H%M%S")
#         return timestamp
#     except Exception as e:
#         print(f"Error extracting timestamp from {filename}: {e}")
#         return None

# Load CSV and preprocess
v_file = r"\F002_L2__FIRE________2023-11-17T055836.143099Z_2023-12-12T130221.101063Z_9bc95636.csv"
csv_path = (
    r"C:\Users\jseelig\Desktop\side_projects\OroraTech_1\challenge\challenge" + v_file
)
filename = os.path.basename(csv_path)
print("FILE", filename)
print("ts", extract_timestamp(filename))
df = pd.read_csv(csv_path, usecols=["lat", "lon"])  # Ignore x, y, mwir
df["timestamp"] = extract_timestamp(filename)  # Add extracted timestamp

# Insert into the database
df.to_sql("fire_detections", engine, if_exists="append", index=False)

# Update geometry column
with engine.connect() as conn:
    conn.execute(
        "UPDATE fire_detections SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);"
    )
