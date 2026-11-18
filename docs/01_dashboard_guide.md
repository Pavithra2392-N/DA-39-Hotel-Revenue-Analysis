# Dashboard Guide (Power BI) - Deliverable 5, 20 marks
Requirement: interactive dashboard with KPI cards, filters and 4-6 visuals. Clear layout, correct KPIs, useful filters.

## 1. Load data (Home > Get Data > Text/CSV, load all from `data/tables/`)
`bookings, customers, room_types, segments, meal_plans, calendar, stay_nights, hotel_info`
(Optional: `data/powerbi/daily_kpi.csv` for quick visuals, but the model below is better and shows more skill.)

## 2. Data types (Power Query > Transform)
- `calendar[date_key]`, `stay_nights[stay_date]`, `bookings[arrival_date]` -> **Date**
- Sort `calendar[month_name]` by `calendar[month]` (Column tools > Sort by column) and `weekday` by a weekday-number column if you add one.

## 3. Model view - create these relationships (many-to-one, single direction)
| From (many) | To (one) |
|---|---|
| bookings[customer_id] | customers[customer_id] |
| bookings[room_type_id] | room_types[room_type_id] |
| bookings[segment_id] | segments[segment_id] |
| bookings[meal_plan_id] | meal_plans[meal_plan_id] |
| stay_nights[booking_id] | bookings[booking_id] |
| stay_nights[stay_date] | calendar[date_key] |

`hotel_info` stays unconnected (it only holds the capacity number).

## 4. DAX measures (Modeling > New measure) - paste one by one
```
Total Rooms = MAX ( hotel_info[total_rooms] )

Rooms Sold = COUNTROWS ( stay_nights )

Room Revenue =
SUMX ( stay_nights, RELATED ( bookings[avg_price_per_room] ) )

Paid Rooms Sold =
CALCULATE ( COUNTROWS ( stay_nights ), FILTER ( bookings, bookings[is_complimentary] = 0 ) )

Days in Period = DISTINCTCOUNT ( stay_nights[stay_date] )

Rooms Available = [Days in Period] * [Total Rooms]

Occupancy % = DIVIDE ( [Rooms Sold], [Rooms Available] )

ADR = DIVIDE ( [Room Revenue], [Paid Rooms Sold] )

RevPAR = DIVIDE ( [Room Revenue], [Rooms Available] )

Total Bookings = COUNTROWS ( bookings )

Cancellation Rate = DIVIDE ( SUM ( bookings[is_cancelled] ), [Total Bookings] )

Revenue Lost to Cancellations =
CALCULATE ( SUM ( bookings[room_revenue] ), bookings[is_cancelled] = 1 )

Avg Lead Time = AVERAGE ( bookings[lead_time] )

Avg Length of Stay = AVERAGE ( bookings[total_nights] )
```
Check: `RevPAR` must equal `ADR x Occupancy %` (when there are no complimentary stays). Compare Occupancy, ADR and RevPAR with your Python output - they should match closely.

Caution: `Rooms Sold`, `Room Revenue`, `Occupancy`, `ADR` and `RevPAR` use stay_nights (non-cancelled nights only). `Cancellation Rate` and `Revenue Lost` use the bookings table. Do not mix them in one visual without a label.

## 5. What-if capacity slicer (impressive for the viva)
Modeling > New parameter > Numeric range: name "Capacity", min = 0.8x, max = 2x your capacity, step 10, default = your capacity.
Then change: `Total Rooms = SELECTEDVALUE ( Capacity[Capacity Value], MAX ( hotel_info[total_rooms] ) )`

## 6. Page layout (1 page, 16:9)
```
+--------------------------------------------------------------+
| Title: Hotel Revenue & Occupancy Dashboard      [Slicers: Year | Season | Segment | Room type | Meal plan] |
+----------+----------+----------+----------+----------+-------+
| RevPAR   | ADR      | Occupancy| Revenue  | Cancel % | Avg   |
| (card)   | (card)   | % (card) | (card)   | (card)   | Lead  |
+----------+----------+----------+----------+----------+-------+
| 1. Line + column: RevPAR & Occupancy by month  | 2. Bar: Revenue by segment |
+------------------------------------------------+----------------------------+
| 3. Clustered bar: ADR by room type             | 4. Column: Cancel rate by lead bucket |
+------------------------------------------------+----------------------------+
| 5. Matrix heatmap: Month x Weekday occupancy (conditional formatting)       |
+--------------------------------------------------------------+
```
- Visual 1: x = calendar[year]+calendar[month_name], y = [RevPAR] (line), [Occupancy %] (secondary axis).
- Visual 2: x = segments[market_segment], y = [Room Revenue].
- Visual 3: x = room_types[room_type], y = [ADR].
- Visual 4: x = bookings[lead_bucket], y = [Cancellation Rate].
- Visual 5: Matrix rows = calendar[month_name], columns = calendar[weekday], values = [Occupancy %], Cells > Background color > Gradient.
- Optional 6th: Donut of cancellations by meal plan or a Decomposition tree.

## 7. Design rules (what graders look at)
- One colour palette (max 3 colours + red for cancellations). Same font everywhere.
- KPI cards on top, left-to-right = most important first.
- Every visual has a clear title with units; format RevPAR/ADR with the currency you chose (the dataset does not state currency - say "currency units" or state your assumption).
- Add a text box "Insight" under 2-3 visuals (e.g. "Online bookings cancel 2x more than Corporate").
- Test every slicer. Add a Reset (bookmark) button if you can.
- Publish a PDF export + screenshots for the report.

## Tableau users
Same logic: join tables in Data Source tab, create calculated fields `RevPAR = SUM([Revenue]) / ([Days]*[Capacity])`, Capacity as a Parameter.
