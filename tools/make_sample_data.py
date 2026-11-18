"""
OPTIONAL - only for practising the scripts BEFORE you download the real Kaggle file.
Creates a FAKE file with the same columns as the Hotel Reservations dataset.
Do NOT use this for your final submission. Use the real Kaggle CSV.
Usage:  python tools/make_sample_data.py   ->  data/raw/hotel_reservations_SAMPLE.csv
"""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)
n = 36000
seg = rng.choice(["Online","Offline","Corporate","Aviation","Complementary"], n, p=[.64,.29,.055,.003,.012])
dates = pd.to_datetime("2017-07-01") + pd.to_timedelta(rng.integers(0, 548, n), unit="D")
base = {"Online":112,"Offline":92,"Corporate":82,"Aviation":100,"Complementary":0}
season_boost = 1 + 0.25*np.sin((dates.month.values-3)/12*2*np.pi)
price = np.array([base[s] for s in seg])*season_boost + rng.normal(0, 22, n)
price = np.where(seg=="Complementary", 0, np.clip(price, 30, 540)).round(2)
lead = rng.gamma(1.4, 55, n).astype(int)
cancel_p = np.clip(0.18 + lead/400 + (seg=="Online")*0.12 - (seg=="Corporate")*0.12, 0.02, 0.9)
status = np.where(rng.random(n) < cancel_p, "Canceled", "Not_Canceled")
df = pd.DataFrame({
 "Booking_ID": [f"INN{i:05d}" for i in range(1, n+1)],
 "no_of_adults": rng.choice([1,2,3,0],n,p=[.2,.72,.07,.01]),
 "no_of_children": rng.choice([0,1,2],n,p=[.92,.05,.03]),
 "no_of_weekend_nights": rng.choice([0,1,2,3],n,p=[.46,.28,.25,.01]),
 "no_of_week_nights": rng.choice([0,1,2,3,4,5],n,p=[.02,.28,.33,.2,.1,.07]),
 "type_of_meal_plan": rng.choice(["Meal Plan 1","Meal Plan 2","Meal Plan 3","Not Selected"],n,p=[.77,.09,.001,.139]),
 "required_car_parking_space": rng.choice([0,1],n,p=[.97,.03]),
 "room_type_reserved": rng.choice([f"Room_Type {i}" for i in range(1,8)],n,p=[.78,.02,.003,.16,.007,.03,.0]) if False else rng.choice([f"Room_Type {i}" for i in range(1,8)],n,p=[.77,.02,.003,.16,.007,.03,.01]),
 "lead_time": lead,
 "arrival_year": dates.year, "arrival_month": dates.month, "arrival_date": dates.day,
 "market_segment_type": seg,
 "repeated_guest": rng.choice([0,1],n,p=[.97,.03]),
 "no_of_previous_cancellations": rng.choice([0,1,2],n,p=[.99,.007,.003]),
 "no_of_previous_bookings_not_canceled": rng.choice([0,1,3,10],n,p=[.97,.015,.01,.005]),
 "avg_price_per_room": price,
 "no_of_special_requests": rng.choice([0,1,2,3],n,p=[.54,.31,.12,.03]),
 "booking_status": status})
# plant the same kinds of data-quality problems the real dataset has
bad = rng.choice(n, 37, replace=False)
df.loc[bad, ["arrival_year","arrival_month","arrival_date"]] = [2018, 2, 29]
z = rng.choice(n, 40, replace=False)
df.loc[z, ["no_of_weekend_nights","no_of_week_nights"]] = 0
df = pd.concat([df, df.sample(15, random_state=1)])   # a few duplicate rows
df.to_csv("data/raw/hotel_reservations_SAMPLE.csv", index=False)
print("Sample file written:", df.shape)
