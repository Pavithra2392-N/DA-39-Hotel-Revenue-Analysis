"""
STEP 2 - BUILD THE RELATIONAL TABLES   (feeds Rubric: Deliverable 3 - SQL, 15 marks)
Run:  python scripts/02_build_tables.py

Splits the one flat file into 7 linked tables, saves them as CSV (data/tables/) and also
creates a ready SQLite database (data/hotel.db) so you can practise SQL immediately.
For MySQL / PostgreSQL, use sql/01_schema.sql and load the CSVs (see README).

IMPORTANT ASSUMPTION - HOTEL CAPACITY
The dataset does NOT say how many rooms the hotel has. RevPAR needs it.
Leave CAPACITY = None and the script picks a capacity so that the busiest night is ~95 % full.
Or type your own number (e.g. CAPACITY = 350) and explain why in your report.
"""
import os, sqlite3, math
import pandas as pd, numpy as np

CAPACITY = None          # <- set a number here to override the automatic choice

df = pd.read_csv("data/clean/hotel_clean.csv", parse_dates=["arrival_dt"])
os.makedirs("data/tables", exist_ok=True)

# ---- dimension tables ---------------------------------------------------------------
room_types = pd.DataFrame({"room_type": sorted(df.room_type_reserved.unique())})
room_types.insert(0, "room_type_id", range(1, len(room_types) + 1))
segments = pd.DataFrame({"market_segment": sorted(df.market_segment_type.unique())})
segments.insert(0, "segment_id", range(1, len(segments) + 1))
meal_plans = pd.DataFrame({"meal_plan": sorted(df.type_of_meal_plan.unique())})
meal_plans.insert(0, "meal_plan_id", range(1, len(meal_plans) + 1))

# ---- customers: the dataset has no guest ID, so we create one guest profile per booking ----
df = df.sort_values(["arrival_dt", "booking_id"]).reset_index(drop=True)
df["customer_id"] = np.arange(1, len(df) + 1)
customers = df[["customer_id", "no_of_adults", "no_of_children", "total_guests", "repeated_guest",
                "no_of_previous_cancellations", "no_of_previous_bookings_not_canceled"]].rename(
    columns={"no_of_adults": "adults", "no_of_children": "children",
             "no_of_previous_cancellations": "prev_cancellations",
             "no_of_previous_bookings_not_canceled": "prev_not_cancelled"})

# ---- fact table: bookings -------------------------------------------------------------
b = (df.merge(room_types, left_on="room_type_reserved", right_on="room_type")
       .merge(segments, left_on="market_segment_type", right_on="market_segment")
       .merge(meal_plans, left_on="type_of_meal_plan", right_on="meal_plan"))
bookings = b[["booking_id", "customer_id", "room_type_id", "segment_id", "meal_plan_id",
              "arrival_dt", "arrival_year", "arrival_month", "total_nights",
              "no_of_weekend_nights", "no_of_week_nights", "lead_time", "lead_bucket",
              "avg_price_per_room", "room_revenue", "is_cancelled", "is_complimentary",
              "no_of_special_requests", "required_car_parking_space"]].rename(
    columns={"arrival_dt": "arrival_date", "no_of_weekend_nights": "weekend_nights",
             "no_of_week_nights": "week_nights", "no_of_special_requests": "special_requests",
             "required_car_parking_space": "parking_required"}).sort_values("arrival_date")
bookings["arrival_date"] = bookings.arrival_date.dt.strftime("%Y-%m-%d")

# ---- stay_nights: one row per occupied night (non-cancelled bookings) ---------------------
stay = df[df.is_cancelled == 0][["booking_id", "arrival_dt", "total_nights"]].copy()
stay = stay.loc[stay.index.repeat(stay.total_nights)]
stay["offset"] = stay.groupby(level=0).cumcount()
stay["stay_date"] = stay.arrival_dt + pd.to_timedelta(stay.offset, unit="D")
stay_nights = stay[["booking_id", "stay_date"]].reset_index(drop=True)

# ---- calendar --------------------------------------------------------------------------
season_map = {12:"Winter",1:"Winter",2:"Winter",3:"Spring",4:"Spring",5:"Spring",
              6:"Summer",7:"Summer",8:"Summer",9:"Autumn",10:"Autumn",11:"Autumn"}
days = pd.date_range(stay_nights.stay_date.min(), stay_nights.stay_date.max())
calendar = pd.DataFrame({"date_key": days})
calendar["year"] = calendar.date_key.dt.year
calendar["month"] = calendar.date_key.dt.month
calendar["month_name"] = calendar.date_key.dt.month_name()
calendar["quarter"] = calendar.date_key.dt.quarter
calendar["weekday"] = calendar.date_key.dt.day_name()
calendar["is_weekend"] = calendar.date_key.dt.dayofweek.isin([5, 6]).astype(int)  # Sat/Sun nights (the Kaggle page defines weekend nights as Saturday or Sunday)
calendar["season"] = calendar.month.map(season_map)

# ---- hotel capacity (ASSUMPTION) ------------------------------------------------------
peak = stay_nights.groupby("stay_date").size().max()
cap = CAPACITY if CAPACITY else int(math.ceil(peak / 0.95 / 10) * 10)
hotel_info = pd.DataFrame({"hotel_name": ["INN Hotels (assumed capacity)"], "total_rooms": [cap]})

# ---- save CSVs --------------------------------------------------------------------------
stay_nights["stay_date"] = stay_nights.stay_date.dt.strftime("%Y-%m-%d")
calendar["date_key"] = calendar.date_key.dt.strftime("%Y-%m-%d")
tables = {"bookings": bookings, "customers": customers, "room_types": room_types,
          "segments": segments, "meal_plans": meal_plans, "calendar": calendar,
          "stay_nights": stay_nights, "hotel_info": hotel_info}
for name, t in tables.items():
    t.to_csv(f"data/tables/{name}.csv", index=False)

# ---- SQLite practice database -----------------------------------------------------------
if os.path.exists("data/hotel.db"): os.remove("data/hotel.db")
con = sqlite3.connect("data/hotel.db")
for name, t in tables.items():
    t.to_sql(name, con, index=False)
con.close()

print("Tables written to data/tables/ and data/hotel.db")
for name, t in tables.items():
    print(f"  {name:<12} {len(t):>8,} rows")
print(f"\nPeak occupied rooms on a single night : {peak}")
print(f"ASSUMED HOTEL CAPACITY (total_rooms)  : {cap}   <- write this in your report")
