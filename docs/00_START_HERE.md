# DA-39 Hotel Revenue & Occupancy (RevPAR) - Do-it-one-by-one Guide
Student: Pavithra N | Batch 2 | Total 100 marks. Tick each step as you finish.

## Folder map
| Folder | What is inside |
|---|---|
| `data/raw` | put the Kaggle CSV here |
| `scripts` | 01 clean, 02 tables, 03 EDA (script + notebook) |
| `sql` | schema + 11 queries |
| `docs` | this guide, dashboard guide, report template, slides outline, viva Q&A |
| `DA39_Data_Dictionary_and_Tracker.xlsx` | Deliverable 1 draft + marks tracker |

## One-time setup (30 min)
- [ ] Install Python 3.10+, then run: `pip install pandas numpy matplotlib seaborn jupyter`
- [ ] Install MySQL Workbench (or PostgreSQL + pgAdmin) and Power BI Desktop (free, Windows). Mac users: use Tableau Public instead.
- [ ] Make a free Kaggle account. Search **"Hotel Reservations Classification Dataset"** (by Ahsan Raza). Download the CSV.
- [ ] Rename it `hotel_reservations.csv` and put it in `data/raw/`.
- [ ] Note down: dataset URL, licence, download date (needed in Deliverable 1).
- [ ] In the Student Assignment sheet set "Dataset finalised? = Y".
- [ ] Optional dry-run: `python tools/make_sample_data.py` makes a FAKE file so you can test scripts. Delete sample outputs before the real run.

IMPORTANT: always run commands from the project root folder (the one containing `data` and `scripts`).

---
## DAY 1 - Deliverable 1: Problem statement and data dictionary (10 marks)
- [ ] Open the Excel file, sheet "Data Dictionary". Check every column against YOUR csv (`df.info()`), fix descriptions.
- [ ] Write the 1-page problem statement (use sheet "Problem Statement" as a base): business problem, 6 KPIs, source and licence, assumptions.
- [ ] Write the capacity assumption (see Day 3) - leave a gap for the final number.

## DAY 2 - Deliverable 2: Data cleaning (15 marks)
- [ ] `python scripts/01_clean_data.py`
- [ ] Open `data/clean/cleaning_log.csv`. This IS your before/after table. Copy it into the report.
- [ ] Write 1 sentence per step: WHY you did it (the script already has reasons - rewrite in your own words).
- [ ] Also do a quick Excel pass: open `hotel_clean.csv`, make a pivot of bookings by segment to double-check counts. (Tool required: Excel / Power Query / Pandas - pandas counts.)
- Viva point: why flag zero-price and outliers instead of deleting.

## DAY 3 - Deliverable 3 part A: Tables and database (15 marks shared)
- [ ] `python scripts/02_build_tables.py` -> 8 CSVs in `data/tables/` + `data/hotel.db`
- [ ] Note the printed **ASSUMED HOTEL CAPACITY**. Write it in your report. (Peak occupied rooms / 0.95, rounded up. You may override with `CAPACITY = number` in the script.)
- [ ] MySQL/PostgreSQL: create DB, run `sql/01_schema.sql`, import the CSVs in this order: room_types, segments, meal_plans, customers, calendar, hotel_info, bookings, stay_nights.
- [ ] Draw the ER diagram (draw.io, free): bookings in the centre, linked to customers, room_types, segments, meal_plans; stay_nights links bookings to calendar. Screenshot it for the report.
- Be honest in the viva: the dataset has no guest ID, so one customer profile is created per booking.

## DAYS 4-5 - Deliverable 3 part B: SQL analysis
- [ ] Run each query in `sql/02_queries.sql` one at a time. Check the output is sensible.
- [ ] Under each query write 2 lines: question answered + finding with numbers.
- [ ] Save as `DA39_SQL_Analysis.sql` with comments + screenshots of 3-4 results.
- Rubric needs: JOINs across 3-4 tables (Q1, Q4, Q10), subquery (Q9), CTE (Q4-Q7, Q10), window function (Q4, Q5, Q6, Q11). All covered.

## DAYS 6-8 - Deliverable 4: Python EDA (20 marks)
- [ ] `jupyter notebook scripts/03_eda_notebook.ipynb` and Run All (or `python scripts/03_eda_charts.py` for charts only).
- [ ] Under each of the 8 charts replace the "WRITE YOUR OBSERVATION" cell with 2-3 sentences: **what you see -> why -> what to do**.
- [ ] Keep the segmentation table and capacity sensitivity table.
- [ ] Charts are also saved in `outputs/charts/`.
- This step also creates `data/powerbi/daily_kpi.csv` and `monthly_kpi.csv` for the dashboard.

## DAYS 9-11 - Deliverable 5: Dashboard (20 marks)
- [ ] Follow `docs/01_dashboard_guide.md` (layout + all DAX measures ready to paste).
- [ ] Screenshot every page; export a PDF too.

## DAYS 12-13 - Deliverable 6: Report (10 marks)
- [ ] Fill `docs/02_report_template.md`, then paste into Word and export PDF. 2-3 pages only.

## DAY 14 - Deliverable 7: Presentation and viva (10 marks)
- [ ] Build slides from `docs/03_slides_outline.md` (7 slides, 5 minutes).
- [ ] Practise `docs/04_viva_questions.md` out loud, twice.

## Final checklist before submission
- [ ] Numbers in report = numbers in dashboard = numbers in SQL/Python (same capacity!)
- [ ] Every chart has a written observation
- [ ] Capacity assumption and its sensitivity table are visible
- [ ] Sample/fake data is NOT used anywhere
- [ ] Source + licence stated
