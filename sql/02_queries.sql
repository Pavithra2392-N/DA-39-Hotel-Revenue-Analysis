-- =====================================================================
-- 10 SQL QUERIES  (Rubric: Deliverable 3, 15 marks)
-- Works on SQLite (data/hotel.db), PostgreSQL and MySQL 8.
-- For each query write 2 lines under it: WHAT it answers + WHAT you found.
-- Skills shown: JOIN, GROUP BY, CASE, subquery, CTE, window functions (RANK, LAG, SUM OVER)
-- RevPAR = revenue / rooms available.  ADR = revenue / rooms sold.  Occupancy = rooms sold / rooms available.
-- Revenue is counted on the NIGHT STAYED (stay_nights) and only for non-cancelled bookings.
-- =====================================================================

-- Q1. Monthly KPIs: rooms sold, revenue, ADR, occupancy %, RevPAR      [4-table JOIN + GROUP BY]
SELECT c.year, c.month,
       COUNT(*)                                             AS rooms_sold,
       ROUND(SUM(b.avg_price_per_room), 0)                  AS room_revenue,
       ROUND(SUM(b.avg_price_per_room) * 1.0
             / NULLIF(SUM(CASE WHEN b.is_complimentary = 0 THEN 1 ELSE 0 END), 0), 2) AS adr,
       ROUND(100.0 * COUNT(*) / (COUNT(DISTINCT s.stay_date) * h.total_rooms), 1)   AS occupancy_pct,
       ROUND(SUM(b.avg_price_per_room) * 1.0 / (COUNT(DISTINCT s.stay_date) * h.total_rooms), 2) AS revpar
FROM stay_nights s
JOIN bookings   b ON b.booking_id = s.booking_id
JOIN calendar   c ON c.date_key   = s.stay_date
CROSS JOIN hotel_info h
GROUP BY c.year, c.month, h.total_rooms
ORDER BY c.year, c.month;

-- Q2. Cancellation rate and bookings by market segment                  [JOIN + GROUP BY]
SELECT sg.market_segment,
       COUNT(*)                                   AS bookings,
       SUM(b.is_cancelled)                        AS cancelled,
       ROUND(100.0 * SUM(b.is_cancelled) / COUNT(*), 1) AS cancel_rate_pct
FROM bookings b
JOIN segments sg ON sg.segment_id = b.segment_id
GROUP BY sg.market_segment
ORDER BY cancel_rate_pct DESC;

-- Q3. Revenue LOST to cancellations vs revenue kept, by room type        [JOIN + conditional SUM]
SELECT r.room_type,
       ROUND(SUM(CASE WHEN b.is_cancelled = 1 THEN b.room_revenue ELSE 0 END), 0) AS revenue_lost,
       ROUND(SUM(CASE WHEN b.is_cancelled = 0 THEN b.room_revenue ELSE 0 END), 0) AS revenue_kept,
       ROUND(100.0 * SUM(CASE WHEN b.is_cancelled = 1 THEN b.room_revenue ELSE 0 END) / SUM(b.room_revenue), 1) AS pct_lost
FROM bookings b
JOIN room_types r ON r.room_type_id = b.room_type_id
GROUP BY r.room_type
ORDER BY revenue_lost DESC;

-- Q4. Rank room types by revenue WITHIN each segment                      [CTE + RANK() window]
WITH seg_room AS (
    SELECT sg.market_segment, r.room_type, SUM(b.room_revenue) AS revenue
    FROM bookings b
    JOIN segments   sg ON sg.segment_id   = b.segment_id
    JOIN room_types r  ON r.room_type_id  = b.room_type_id
    WHERE b.is_cancelled = 0
    GROUP BY sg.market_segment, r.room_type)
SELECT market_segment, room_type, ROUND(revenue, 0) AS revenue,
       RANK() OVER (PARTITION BY market_segment ORDER BY revenue DESC) AS rank_in_segment
FROM seg_room
ORDER BY market_segment, rank_in_segment;

-- Q5. Month-over-month revenue growth %                                   [CTE + LAG() window]
WITH monthly AS (
    SELECT c.year, c.month, SUM(b.avg_price_per_room) AS revenue
    FROM stay_nights s
    JOIN bookings b ON b.booking_id = s.booking_id
    JOIN calendar c ON c.date_key   = s.stay_date
    GROUP BY c.year, c.month)
SELECT year, month, ROUND(revenue, 0) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year, month))
             / LAG(revenue) OVER (ORDER BY year, month), 1) AS mom_growth_pct
FROM monthly
ORDER BY year, month;

-- Q6. Running (cumulative) revenue within each year                       [SUM() OVER window]
WITH monthly AS (
    SELECT c.year, c.month, SUM(b.avg_price_per_room) AS revenue
    FROM stay_nights s
    JOIN bookings b ON b.booking_id = s.booking_id
    JOIN calendar c ON c.date_key   = s.stay_date
    GROUP BY c.year, c.month)
SELECT year, month, ROUND(revenue, 0) AS revenue,
       ROUND(SUM(revenue) OVER (PARTITION BY year ORDER BY month), 0) AS running_total
FROM monthly
ORDER BY year, month;

-- Q7. Does a longer lead time mean more cancellations?                    [CASE buckets + CTE]
WITH x AS (
    SELECT CASE WHEN lead_time <= 7  THEN '1) 0-7 days'
                WHEN lead_time <= 30 THEN '2) 8-30 days'
                WHEN lead_time <= 90 THEN '3) 31-90 days'
                ELSE '4) 90+ days' END AS lead_bucket,
           is_cancelled, avg_price_per_room
    FROM bookings)
SELECT lead_bucket, COUNT(*) AS bookings,
       ROUND(100.0 * AVG(is_cancelled), 1)      AS cancel_rate_pct,
       ROUND(AVG(avg_price_per_room), 2)        AS avg_price
FROM x
GROUP BY lead_bucket
ORDER BY lead_bucket;

-- Q8. Repeat guests vs new guests: price, cancellations, special requests [JOIN customers]
SELECT CASE WHEN cu.repeated_guest = 1 THEN 'Repeat guest' ELSE 'New guest' END AS guest_type,
       COUNT(*)                                          AS bookings,
       ROUND(AVG(b.avg_price_per_room), 2)               AS avg_price,
       ROUND(100.0 * AVG(b.is_cancelled), 1)             AS cancel_rate_pct,
       ROUND(AVG(b.special_requests), 2)                 AS avg_special_requests
FROM bookings b
JOIN customers cu ON cu.customer_id = b.customer_id
GROUP BY cu.repeated_guest;

-- Q9. Months whose ADR is ABOVE the overall ADR                           [subquery]
SELECT c.year, c.month, ROUND(AVG(b.avg_price_per_room), 2) AS month_adr
FROM stay_nights s
JOIN bookings b ON b.booking_id = s.booking_id
JOIN calendar c ON c.date_key   = s.stay_date
WHERE b.is_complimentary = 0
GROUP BY c.year, c.month
HAVING AVG(b.avg_price_per_room) >
       (SELECT AVG(b2.avg_price_per_room) FROM bookings b2 WHERE b2.is_complimentary = 0 AND b2.is_cancelled = 0)
ORDER BY month_adr DESC;

-- Q10. Weekend vs weekday nights by season: occupancy % and RevPAR        [calendar JOIN + GROUP BY]
WITH daily AS (
    SELECT c.date_key, c.season, c.is_weekend,
           COUNT(*) AS rooms_sold, SUM(b.avg_price_per_room) AS revenue
    FROM stay_nights s
    JOIN bookings b ON b.booking_id = s.booking_id
    JOIN calendar c ON c.date_key   = s.stay_date
    GROUP BY c.date_key, c.season, c.is_weekend)
SELECT d.season,
       CASE WHEN d.is_weekend = 1 THEN 'Sat/Sun night' ELSE 'Mon-Fri night' END AS night_type,
       COUNT(*)                                                        AS days,
       ROUND(100.0 * AVG(d.rooms_sold) / h.total_rooms, 1)             AS occupancy_pct,
       ROUND(AVG(d.revenue) / h.total_rooms, 2)                        AS revpar
FROM daily d
CROSS JOIN hotel_info h
GROUP BY d.season, d.is_weekend, h.total_rooms
ORDER BY d.season, d.is_weekend;

-- BONUS Q11. Top 10 busiest nights ever                                   [window DENSE_RANK]
WITH daily AS (
    SELECT s.stay_date, COUNT(*) AS rooms_sold FROM stay_nights s GROUP BY s.stay_date)
SELECT stay_date, rooms_sold, DENSE_RANK() OVER (ORDER BY rooms_sold DESC) AS busy_rank
FROM daily
ORDER BY busy_rank
LIMIT 10;
