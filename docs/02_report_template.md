# Insights & Recommendations Report - Hotel Revenue & Occupancy (RevPAR)
Deliverable 6 | 2-3 pages | Pavithra N | DA-39
(Replace every [BRACKET] with your real numbers from SQL / Python / dashboard. Delete these grey instructions.)

## 1. Business problem
A hotel wants to know how room price, season and booking channel affect revenue and occupancy, and how much revenue it loses to cancellations. Data: [N] bookings, [first date] to [last date], Kaggle "Hotel Reservations Classification Dataset" ([licence]), downloaded [date].

## 2. Data and method (5-6 lines)
- Cleaned [raw rows] -> [clean rows] rows (see table: duplicates, invalid dates such as 29-Feb-2018, zero-night stays, zero guests). Zero-price and outlier rows were flagged, not deleted.
- Revenue counted per night stayed, non-cancelled bookings only.
- **Assumption:** total rooms = [capacity] (peak night [peak] rooms sold / 0.95). RevPAR changes with this assumption - sensitivity: [table with 4 capacities].
- Tools: Python (pandas), SQL ([MySQL/PostgreSQL]), Power BI.

## 3. Headline KPIs
| KPI | Value |
|---|---|
| Occupancy | [ ]% |
| ADR | [ ] |
| RevPAR | [ ] |
| Cancellation rate | [ ]% |
| Revenue lost to cancellations | [ ] ([ ]% of booked revenue) |

## 4. Key findings (4-5, each with a number)
1. **Seasonality:** RevPAR peaks in [month(s)] ([value]) and is lowest in [month(s)] ([value]). It is driven mainly by [price / occupancy].
2. **Channels:** [Online] gives [x]% of revenue but cancels at [y]%, vs [Corporate] at [z]%.
3. **Lead time:** bookings made [90+] days ahead cancel at [x]% vs [y]% for 0-7 days.
4. **Weekday pattern:** [weak weekday(s)] run at [x]% occupancy vs [y]% on [strong day].
5. **Guests:** repeat guests cancel [less/more] ([x]% vs [y]%).

## 5. Business impact
- Cutting the cancellation rate by 5 percentage points would protect roughly [calculate: 5% x bookings x avg revenue per booking] in revenue.
- Raising ADR by [x]% in the [3 weakest months] adds about [ ] RevPAR points.

## 6. Recommendations (3-5, specific and practical)
1. **Deposit / non-refundable rate** for online bookings with lead time over [90] days (cancellation [x]%).
2. **Dynamic pricing:** raise rates by [x]% in [peak months]; run packages in [low months] to lift occupancy.
3. **Fill weak weekdays** ([days]) with corporate / long-stay offers.
4. **Loyalty programme** for repeat guests ([x]% cancel less).
5. **Overbooking buffer** of about [x]% on high-cancel segments, with a walk-guest policy.

## 7. Limitations
Capacity is assumed; no guest IDs; limited date window (edge months may be partial); price currency not stated; correlation is not causation.
