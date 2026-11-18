"""
STEP 1 - DATA CLEANING   (Rubric: Deliverable 2, 15 marks)
Run from the project root:   python scripts/01_clean_data.py
Input : data/raw/hotel_reservations.csv      (real Kaggle file)
Output: data/clean/hotel_clean.csv
        data/clean/cleaning_log.csv          (before/after row counts + reasons -> put in your report)
"""
import sys, os
import pandas as pd, numpy as np

RAW = "data/raw/hotel_reservations.csv"
if not os.path.exists(RAW):
    RAW = "data/raw/hotel_reservations_SAMPLE.csv"
    print("!! Real file not found - using SAMPLE data for practice only.")

raw = pd.read_csv(RAW)
df = raw.copy()
log = []
def add(step, rows_affected, rows_after, reason):
    log.append({"Step": step, "Rows affected": rows_affected, "Rows after step": rows_after, "Reason / decision": reason})

add("0. Raw file loaded", 0, len(df), f"Source file: {RAW}")

# ---- 1. Standardise column names and text ------------------------------------------------
df.columns = df.columns.str.strip().str.lower()
for c in df.columns:
    if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c]):
        df[c] = df[c].str.strip()
add("1. Column names / text trimmed", 0, len(df), "lower-case names, removed stray spaces")

# ---- 2. Missing values --------------------------------------------------------------------
nulls = df.isna().sum()
nulls = nulls[nulls > 0]
before = len(df)
df = df.dropna()
add("2. Rows with missing values dropped", before - len(df), len(df),
    f"Null counts found: {nulls.to_dict() if len(nulls) else 'none'}")

# ---- 3. Duplicates ------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
add("3. Exact duplicate rows removed", before - len(df), len(df), "Identical rows across all columns")
before = len(df)
df = df.drop_duplicates(subset="booking_id")
add("3b. Duplicate booking_id removed", before - len(df), len(df), "booking_id must be unique")

# ---- 4. Invalid arrival dates (e.g. 29-Feb-2018 does not exist) -----------------------------
df["arrival_dt"] = pd.to_datetime(
    dict(year=df.arrival_year, month=df.arrival_month, day=df.arrival_date), errors="coerce")
before = len(df)
df = df.dropna(subset=["arrival_dt"])
add("4. Invalid arrival dates removed", before - len(df), len(df),
    "e.g. 29-Feb-2018 - 2018 is not a leap year, so the date cannot exist")

# ---- 5. Zero-night stays ---------------------------------------------------------------------
df["total_nights"] = df.no_of_weekend_nights + df.no_of_week_nights
before = len(df)
df = df[df.total_nights > 0]
add("5. Zero-night bookings removed", before - len(df), len(df), "0 nights = no room-night revenue can exist")

# ---- 6. Zero guests ----------------------------------------------------------------------------
before = len(df)
df = df[(df.no_of_adults + df.no_of_children) > 0]
add("6. Bookings with zero guests removed", before - len(df), len(df), "A booking must have at least 1 guest")

# ---- 7. Complimentary (price = 0): FLAG, do not delete ----------------------------------------
df["is_complimentary"] = (df.avg_price_per_room == 0).astype(int)
add("7. Zero-price rows FLAGGED (kept)", int(df.is_complimentary.sum()), len(df),
    "Free / complimentary stays still occupy rooms (count in occupancy) but are excluded from ADR")

# ---- 8. Price outliers: FLAG with IQR rule ---------------------------------------------------
paid = df.loc[df.is_complimentary == 0, "avg_price_per_room"]
q1, q3 = paid.quantile([.25, .75]); upper = q3 + 1.5 * (q3 - q1)
df["price_outlier"] = (df.avg_price_per_room > upper).astype(int)
add("8. Price outliers FLAGGED (kept)", int(df.price_outlier.sum()), len(df),
    f"IQR rule: price > {upper:.2f}. Kept because high prices may be real peak-season rates")

# ---- 9. Tidy labels + new columns -------------------------------------------------------------
df["room_type_reserved"] = df.room_type_reserved.str.replace("Room_Type ", "RT", regex=False)
df["type_of_meal_plan"]  = df.type_of_meal_plan.str.replace("Meal Plan ", "MP", regex=False)
df["booking_status"]     = df.booking_status.replace({"Canceled": "Cancelled", "Not_Canceled": "Not Cancelled"})
df["is_cancelled"]  = (df.booking_status == "Cancelled").astype(int)
df["total_guests"]  = df.no_of_adults + df.no_of_children
df["room_revenue"]  = (df.avg_price_per_room * df.total_nights).round(2)
df["weekday_name"]  = df.arrival_dt.dt.day_name()
season_map = {12:"Winter",1:"Winter",2:"Winter",3:"Spring",4:"Spring",5:"Spring",
              6:"Summer",7:"Summer",8:"Summer",9:"Autumn",10:"Autumn",11:"Autumn"}
df["season"] = df.arrival_month.map(season_map)   # Northern-hemisphere seasons; change if you justify otherwise
df["lead_bucket"] = pd.cut(df.lead_time, [-1, 7, 30, 90, 10**6],
                           labels=["0-7 days", "8-30 days", "31-90 days", "90+ days"])
add("9. Labels tidied + derived columns added", 0, len(df),
    "total_nights, total_guests, room_revenue, season, lead_bucket, is_cancelled")

# ---- 10. Data types ---------------------------------------------------------------------------
df["lead_bucket"] = df.lead_bucket.astype(str)
for c in ["no_of_adults","no_of_children","no_of_weekend_nights","no_of_week_nights","lead_time",
          "arrival_year","arrival_month","arrival_date","no_of_special_requests"]:
    df[c] = df[c].astype(int)
add("10. Data types fixed", 0, len(df), "counts -> int, price -> float, arrival_dt -> date")

# ---- Save --------------------------------------------------------------------------------------
os.makedirs("data/clean", exist_ok=True)
df.to_csv("data/clean/hotel_clean.csv", index=False)
logdf = pd.DataFrame(log)
logdf.to_csv("data/clean/cleaning_log.csv", index=False)

print(logdf.to_string(index=False))
print(f"\nBEFORE: {len(raw):,} rows   AFTER: {len(df):,} rows   REMOVED: {len(raw)-len(df):,}")
print("\nCancellation rate:", f"{df.is_cancelled.mean():.1%}")
print("Segments:\n", df.market_segment_type.value_counts().to_string())
