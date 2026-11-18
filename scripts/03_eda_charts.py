# %% [markdown]
# # Hotel Revenue & Occupancy (RevPAR) - Python EDA
# **Project DA-39 | Hospitality**  -  Business question: *How do price and season affect revenue?*
# Run the cells top to bottom. Under EVERY chart, replace the "WRITE YOUR OBSERVATION" cell with 2-3 sentences:
# **what you see -> why it probably happens -> what the hotel should do.**

# %%
import os, pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid", font_scale=1.05)
os.makedirs("outputs/charts", exist_ok=True); os.makedirs("data/powerbi", exist_ok=True)

df  = pd.read_csv("data/clean/hotel_clean.csv", parse_dates=["arrival_dt"])
stay = pd.read_csv("data/tables/stay_nights.csv", parse_dates=["stay_date"])
cap = int(pd.read_csv("data/tables/hotel_info.csv").total_rooms[0])
print("Rows:", len(df), "| assumed capacity:", cap)
df.describe().T.round(2)

# %% [markdown]
# ## 1. KPI engine: nightly and monthly Occupancy, ADR, RevPAR
# Revenue is counted on the **night stayed** (not the arrival date) and only for **non-cancelled** bookings.
# `RevPAR = revenue / rooms available`,  `ADR = revenue / paid rooms sold`,  `Occupancy = rooms sold / rooms available`.

# %%
nights = stay.merge(df[["booking_id","avg_price_per_room","is_complimentary","market_segment_type",
                        "room_type_reserved","season"]], on="booking_id")
daily = nights.groupby("stay_date").agg(rooms_sold=("booking_id","count"),
                                        revenue=("avg_price_per_room","sum"),
                                        paid_rooms=("is_complimentary", lambda s: (s==0).sum())).reset_index()
daily["occupancy"] = daily.rooms_sold / cap
daily["adr"]       = daily.revenue / daily.paid_rooms
daily["revpar"]    = daily.revenue / cap
daily["month"]     = daily.stay_date.dt.to_period("M").astype(str)
daily["weekday"]   = daily.stay_date.dt.day_name()

monthly = daily.groupby("month").agg(rooms_sold=("rooms_sold","sum"), revenue=("revenue","sum"),
                                     paid_rooms=("paid_rooms","sum"), days=("stay_date","count")).reset_index()
monthly["occupancy"] = monthly.rooms_sold / (monthly.days * cap)
monthly["adr"]       = monthly.revenue / monthly.paid_rooms
monthly["revpar"]    = monthly.revenue / (monthly.days * cap)
daily.to_csv("data/powerbi/daily_kpi.csv", index=False)
monthly.to_csv("data/powerbi/monthly_kpi.csv", index=False)
print(f"Overall  Occupancy {daily.rooms_sold.sum()/(len(daily)*cap):.1%} | ADR {daily.revenue.sum()/daily.paid_rooms.sum():,.2f} | RevPAR {daily.revenue.sum()/(len(daily)*cap):,.2f}")
monthly.round(2)

# %% [markdown]
# ## Chart 1 - Monthly ADR, Occupancy and RevPAR (trend + seasonality)

# %%
fig, ax = plt.subplots(1, 2, figsize=(14, 4.8))
ax[0].plot(monthly.month, monthly.revpar, marker="o", label="RevPAR"); ax[0].plot(monthly.month, monthly.adr, marker="s", label="ADR")
ax[0].set_title("ADR and RevPAR by month"); ax[0].tick_params(axis="x", rotation=60); ax[0].legend(); ax[0].set_ylabel("Price per room")
ax[1].bar(monthly.month, monthly.occupancy*100, color="#4C78A8"); ax[1].set_title("Occupancy % by month"); ax[1].tick_params(axis="x", rotation=60)
plt.tight_layout(); plt.savefig("outputs/charts/01_monthly_kpis.png", dpi=150); plt.show()
# NOTE: first and last months may be partial because bookings made before/after the data window are missing.

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 1):** Which months have the highest/lowest RevPAR? Is it driven by price (ADR) or by occupancy? Why?

# %% [markdown]
# ## Chart 2 - Revenue and cancellation rate by market segment

# %%
seg = df.groupby("market_segment_type").agg(bookings=("booking_id","count"),
        revenue_kept=("room_revenue", lambda s: s[df.loc[s.index,"is_cancelled"]==0].sum()),
        cancel_rate=("is_cancelled","mean")).reset_index().sort_values("revenue_kept", ascending=False)
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
sns.barplot(data=seg, x="market_segment_type", y="revenue_kept", ax=ax[0], color="#4C78A8"); ax[0].set_title("Revenue (non-cancelled) by segment")
sns.barplot(data=seg, x="market_segment_type", y=seg.cancel_rate*100, ax=ax[1], color="#E45756"); ax[1].set_title("Cancellation rate % by segment"); ax[1].set_ylabel("%")
plt.tight_layout(); plt.savefig("outputs/charts/02_segment.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 2):** Which segment earns the most? Which cancels the most? What does that mean for distribution strategy?

# %% [markdown]
# ## Chart 3 - Price distribution by room type (paid bookings only)

# %%
paid = df[df.is_complimentary == 0]
plt.figure(figsize=(10, 5))
sns.boxplot(data=paid, x="room_type_reserved", y="avg_price_per_room", order=sorted(paid.room_type_reserved.unique()), color="#72B7B2")
plt.title("Price per room by room type"); plt.tight_layout(); plt.savefig("outputs/charts/03_price_by_room.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 3):** Which room types are premium? Any with very wide price ranges (opportunity for yield management)?

# %% [markdown]
# ## Chart 4 - Lead time vs cancellation

# %%
lt = df.groupby("lead_bucket").agg(cancel_rate=("is_cancelled","mean"), bookings=("booking_id","count"),
                                   avg_price=("avg_price_per_room","mean")).reindex(["0-7 days","8-30 days","31-90 days","90+ days"])
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(lt.index, lt.cancel_rate*100, color="#F58518")
for i, (r, n) in enumerate(zip(lt.cancel_rate*100, lt.bookings)): ax.text(i, r+0.8, f"{r:.0f}%\n(n={n:,})", ha="center", fontsize=9)
ax.set_title("Cancellation rate by lead time"); ax.set_ylabel("%"); ax.set_ylim(0, lt.cancel_rate.max()*100+12)
plt.tight_layout(); plt.savefig("outputs/charts/04_leadtime_cancel.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 4):** Does cancellation rise with lead time? By how much? What policy could you suggest (deposit, non-refundable rate)?

# %% [markdown]
# ## Chart 5 - Correlation heatmap

# %%
num = df[["avg_price_per_room","lead_time","total_nights","total_guests","no_of_special_requests",
          "repeated_guest","no_of_previous_cancellations","is_cancelled"]]
plt.figure(figsize=(8.5, 6.5))
sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0)
plt.title("Correlation matrix"); plt.tight_layout(); plt.savefig("outputs/charts/05_correlation.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 5):** Which variable correlates most with cancellation? Remember: correlation is not causation.

# %% [markdown]
# ## Chart 6 - Weekday pattern: occupancy and ADR

# %%
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
wd = daily.groupby("weekday").agg(occ=("rooms_sold","mean"), adr=("adr","mean")).reindex(order)
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].bar(wd.index, wd.occ/cap*100, color="#4C78A8"); ax[0].set_title("Average occupancy % by weekday"); ax[0].tick_params(axis="x", rotation=45)
ax[1].bar(wd.index, wd.adr, color="#54A24B"); ax[1].set_title("Average ADR by weekday"); ax[1].tick_params(axis="x", rotation=45)
plt.tight_layout(); plt.savefig("outputs/charts/06_weekday.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 6):** Which weekdays are weak? Could promotions or corporate packages fill them?

# %% [markdown]
# ## Chart 7 - Does a higher price mean more cancellations?

# %%
paid = df[df.is_complimentary == 0].copy()
paid["price_band"] = pd.qcut(paid.avg_price_per_room, 5, duplicates="drop")
pb = paid.groupby("price_band", observed=True).is_cancelled.mean()*100
plt.figure(figsize=(9, 4.5)); pb.plot(kind="bar", color="#B279A2")
plt.title("Cancellation rate by price quintile"); plt.ylabel("%"); plt.xticks(rotation=30); plt.tight_layout()
plt.savefig("outputs/charts/07_price_cancel.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 7):** Is there a price threshold above which guests cancel more?

# %% [markdown]
# ## Chart 8 - Month x Weekday occupancy heatmap

# %%
daily["mon_name"] = daily.stay_date.dt.month_name()
hm = daily.pivot_table(index="mon_name", columns="weekday", values="rooms_sold", aggfunc="mean")/cap*100
hm = hm.reindex(index=["January","February","March","April","May","June","July","August","September","October","November","December"], columns=order)
plt.figure(figsize=(10, 6)); sns.heatmap(hm, annot=True, fmt=".0f", cmap="YlOrRd")
plt.title("Average occupancy % - month x weekday"); plt.tight_layout(); plt.savefig("outputs/charts/08_heatmap.png", dpi=150); plt.show()

# %% [markdown]
# **WRITE YOUR OBSERVATION (Chart 8):** Which month/weekday combos are "hot" and "cold"? Where should the hotel raise or cut prices?

# %% [markdown]
# ## 9. Segmentation - high-value vs high-risk bookings
# Rule-based segments (easy to explain in your viva).

# %%
def seg_rule(r):
    if r.is_cancelled == 1 and r.lead_time > 90:  return "High-risk (long lead, cancelled)"
    if r.is_cancelled == 0 and r.avg_price_per_room >= df.avg_price_per_room.quantile(.75) and r.total_nights >= 3: return "High-value (premium, long stay)"
    if r.repeated_guest == 1: return "Loyal repeat guest"
    return "Standard"
df["segment_label"] = df.apply(seg_rule, axis=1)
print(df.segment_label.value_counts())
df.groupby("segment_label").agg(bookings=("booking_id","count"), avg_price=("avg_price_per_room","mean"),
                                avg_lead=("lead_time","mean"), revenue=("room_revenue","sum")).round(1)

# %% [markdown]
# ## 10. Capacity sensitivity (include this table in your report)
# Because total rooms is an assumption, show how RevPAR and occupancy change if it is wrong.

# %%
rev, sold, ndays = daily.revenue.sum(), daily.rooms_sold.sum(), len(daily)
sens = pd.DataFrame({"capacity_rooms": [int(cap*0.9), cap, int(cap*1.2), int(cap*1.5)]})
sens["occupancy_%"] = (sold / (ndays*sens.capacity_rooms)*100).round(1)
sens["revpar"]      = (rev / (ndays*sens.capacity_rooms)).round(2)
sens
