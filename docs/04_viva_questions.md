# Viva Practice - answer each in 3-4 sentences out loud

## Concepts
1. What is RevPAR? How is it different from ADR and occupancy? (RevPAR = revenue / rooms available = ADR x occupancy.)
2. Why is RevPAR better than ADR alone? (ADR can be high with empty rooms.)
3. Why do you count revenue on the night stayed and not on the booking date?
4. Why exclude cancelled bookings from revenue but include them in cancellation analysis?

## Your decisions
5. The dataset has no room count. How did you get capacity? Show the sensitivity table. What changes if it is wrong? (Occupancy and RevPAR change, ADR does not.)
6. Why flag zero-price rows instead of dropping them?
7. Why did you remove 29-Feb-2018 dates?
8. How did you create customer_id and what is the limitation?
9. How did you define seasons? Would that be different in the southern hemisphere or in India?

## SQL
10. Explain your RANK / LAG / running total query line by line.
11. Difference between WHERE and HAVING? Where did you use each?
12. Why CROSS JOIN with hotel_info?
13. What is the difference between INNER and LEFT JOIN? Would results change in any query?

## Python
14. Why did you pick a box plot for price by room type?
15. What does a correlation of 0.3 mean? Does it prove cause?
16. How did you expand bookings into nights (stay_nights)?

## Dashboard
17. How is Occupancy % calculated in DAX? What happens when I filter to one month?
18. What does the capacity slicer do?

## Business
19. Which single recommendation would you start with, and why?
20. What other data would improve this analysis? (room inventory, cost per room, competitor rates, actual guest IDs.)
