# Shortfall findings report

40 findings. Amounts and finding types come from deterministic matching; explanations were written by `claude-sonnet-5-5` and checked against the evidence.

## Summary

| Finding type | Count | Net difference (actual - expected) | Low confidence | Amount mismatches |
|---|---:|---:|---:|---:|
| wrong_commission_rate | 7 | $22.44 | 0 | 0 |
| missing_from_payout | 7 | -$303.53 | 0 | 0 |
| refund_deducted_twice | 7 | $342.02 | 0 | 0 |
| refund_without_pos_refund | 7 | $186.18 | 0 | 0 |
| commission_on_cancelled_order | 6 | $45.92 | 0 | 0 |
| tip_not_fully_passed_through | 6 | -$19.72 | 0 | 0 |
| **Total** | **40** | **$273.31** | | |

## Findings

### F-0001: missing_from_payout (MPB-500024)

Marketplace B, LOC-1

| | |
|---|---|
| Field | net_payout |
| Expected | 32.78 |
| Actual | 0.00 |
| Difference | -32.78 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-000050 (delivery, completed, 2026-06-02 18:47) |
| POS subtotal / promo / tip / refund | 40.97 / 0.00 / 0.00 / 0.00 |
| Contract rate on order date | 0.20 |

**Explanation** (confidence: high): Order MPB-500024 from Marketplace B (delivery, placed June 2, 2026) was completed and should have produced a net payout of $32.78, but no payout row for it appears in the marketplace's payout records. The shortfall is the full $32.78, since the actual payout recorded for this order is $0.00. Because the order was completed and not cancelled, the contract requires it to be paid, so it's worth asking Marketplace B why it was left out.

### F-0002: tip_not_fully_passed_through (MPB-500105)

Marketplace B, LOC-3, payout PB-2026W23

| | |
|---|---|
| Field | tip_passed_through |
| Expected | 13.44 |
| Actual | 6.72 |
| Difference | -6.72 |
| Match status | matched |
| Contract rule | Rule 5: tips pass through at 100%. |
| POS order | HTC-000215 (delivery, completed, 2026-06-07 19:33) |
| POS subtotal / promo / tip / refund | 53.75 / 0.00 / 13.44 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W23 (paid 2026-06-10) |
| Payout gross / rate / commission | 53.75 / 0.20 / 10.75 |
| Payout tip / refund / adjustments / net | 6.72 / 0.00 / 0.00 / 49.72 |

**Explanation** (confidence: high): Order MPB-500105 on Marketplace B had a $13.44 tip, and under the contract tips should pass through to the restaurant at 100%. The payout PB-2026W23 passed through only $6.72, so the restaurant was shorted by $6.72. The sales amount ($53.75) and the 20% commission ($10.75) match the contract, so the tip is the only issue on this order.

### F-0003: refund_deducted_twice (MPA-100133)

Marketplace A, LOC-1, payout PA-2026W24

| | |
|---|---|
| Field | refund_deducted |
| Expected | 36.29 |
| Actual | 72.58 |
| Difference | 36.29 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-000257 (delivery, refunded, 2026-06-09 13:49) |
| POS subtotal / promo / tip / refund | 84.39 / 0.00 / 0.00 / 36.29 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W24 (paid 2026-06-17) |
| Payout gross / rate / commission | 84.39 / 0.25 / 21.10 |
| Payout tip / refund / adjustments / net | 0.00 / 72.58 / 0.00 / -9.29 |

**Explanation** (confidence: high): Order MPA-100133 (HTC-000257) was partially refunded to the customer for $36.29, but the Marketplace A payout PA-2026W24 deducted $72.58 for the refund, which is the refund taken out twice. Under the contract a refund should be deducted only once, so the payout is short by $36.29. The gross sales of $84.39 and the $21.10 commission at the 25% rate are correct, so the refund deduction is the only error.

### F-0004: tip_not_fully_passed_through (MPA-100173)

Marketplace A, LOC-3, payout PA-2026W24

| | |
|---|---|
| Field | tip_passed_through |
| Expected | 7.27 |
| Actual | 5.09 |
| Difference | -2.18 |
| Match status | matched |
| Contract rule | Rule 5: tips pass through at 100%. |
| POS order | HTC-000325 (delivery, completed, 2026-06-11 17:28) |
| POS subtotal / promo / tip / refund | 72.67 / 0.00 / 7.27 / 0.00 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W24 (paid 2026-06-17) |
| Payout gross / rate / commission | 72.67 / 0.25 / 18.17 |
| Payout tip / refund / adjustments / net | 5.09 / 0.00 / 0.00 / 59.59 |

**Explanation** (confidence: high): Order MPA-100173 (a delivery order on June 11) had a $7.27 tip, and the contract says tips pass through to the restaurant at 100%. The Marketplace A payout PA-2026W24 passed through only $5.09, which is $2.18 less than it should have been. The sales amount of $72.67 and the 25% commission of $18.17 match the contract, so the shortfall comes only from the tip.

### F-0005: refund_deducted_twice (MPA-100182)

Marketplace A, LOC-1, payout PA-2026W24

| | |
|---|---|
| Field | refund_deducted |
| Expected | 14.52 |
| Actual | 29.04 |
| Difference | 14.52 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-000337 (delivery, refunded, 2026-06-11 20:47) |
| POS subtotal / promo / tip / refund | 14.52 / 0.00 / 0.00 / 14.52 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W24 (paid 2026-06-17) |
| Payout gross / rate / commission | 14.52 / 0.25 / 3.63 |
| Payout tip / refund / adjustments / net | 0.00 / 29.04 / 0.00 / -18.15 |

**Explanation** (confidence: high): Order MPA-100182 (HTC-000337) was a delivery order for $14.52 that was fully refunded to the customer, so the contract says $14.52 should come out of the payout once. Marketplace A's payout PA-2026W24 deducted $29.04 instead, which is $14.52 too much, so the refund was taken out twice. The commission of $3.63 and the 0.25 rate are correct, so you should ask Marketplace A to return the extra $14.52.

### F-0006: missing_from_payout (MPB-500165)

Marketplace B, LOC-3

| | |
|---|---|
| Field | net_payout |
| Expected | 53.98 |
| Actual | 0.00 |
| Difference | -53.98 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-000367 (delivery, completed, 2026-06-12 17:51) |
| POS subtotal / promo / tip / refund | 59.35 / 3.00 / 8.90 / 0.00 |
| Contract rate on order date | 0.20 |

**Explanation** (confidence: high): Order MPB-500165 from Marketplace B (HTC-000367, a completed delivery order placed on June 12, 2026) has no payout row, so nothing was paid for it. Under the contract, a completed order should have produced a net payout of $53.98, so the full $53.98 is missing. You can raise this order with Marketplace B and ask them to pay it or explain why it was left out.

### F-0007: wrong_commission_rate (MPB-500170)

Marketplace B, LOC-2, payout PB-2026W24

| | |
|---|---|
| Field | commission_amount |
| Expected | 1.21 |
| Actual | 3.01 |
| Difference | 1.80 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.08; applied: 0.20. |
| POS order | HTC-000378 (pickup, completed, 2026-06-12 20:03) |
| POS subtotal / promo / tip / refund | 25.07 / 10.00 / 0.00 / 0.00 |
| Contract rate on order date | 0.08 |
| Payout row | PB-2026W24 (paid 2026-06-17) |
| Payout gross / rate / commission | 15.07 / 0.20 / 3.01 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / 12.06 |

**Explanation** (confidence: high): Marketplace B charged commission on pickup order MPB-500170 at 20%, but the contract rate for a Marketplace B pickup order on June 12, 2026 is 8%. Commission is charged on gross sales of $15.07 (the $25.07 subtotal minus the $10.00 promo), so the correct commission is $1.21, not the $3.01 that was taken. That means the payout was short by $1.80.

### F-0008: refund_deducted_twice (MPB-500173)

Marketplace B, LOC-3, payout PB-2026W24

| | |
|---|---|
| Field | refund_deducted |
| Expected | 63.69 |
| Actual | 127.38 |
| Difference | 63.69 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-000387 (delivery, refunded, 2026-06-13 11:46) |
| POS subtotal / promo / tip / refund | 63.69 / 0.00 / 0.00 / 63.69 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W24 (paid 2026-06-17) |
| Payout gross / rate / commission | 63.69 / 0.20 / 12.74 |
| Payout tip / refund / adjustments / net | 0.00 / 127.38 / 0.00 / -76.43 |

**Explanation** (confidence: high): Order MPB-500173 (Marketplace B, delivery) was fully refunded to the customer for $63.69, but the payout PB-2026W24 deducted $127.38 for the refund, which is twice the correct amount. Under the contract a refund is deducted once, so the payout is short by $63.69. The sales, the 20% commission of $12.74, and the tip all match the contract; only the refund deduction is wrong.

### F-0009: commission_on_cancelled_order (MPB-500174)

Marketplace B, LOC-2, payout PB-2026W24

| | |
|---|---|
| Field | commission_amount |
| Expected | 0.00 |
| Actual | 4.81 |
| Difference | 4.81 |
| Match status | matched |
| Contract rule | Rule 9: a cancelled order has no commission and no payout row. |
| POS order | HTC-000388 (delivery, cancelled, 2026-06-13 11:56) |
| POS subtotal / promo / tip / refund | 34.04 / 10.00 / 8.51 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W24 (paid 2026-06-17) |
| Payout gross / rate / commission | 0.00 / 0.20 / 4.81 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / -4.81 |

**Explanation** (confidence: high): Order MPB-500174 (HTC-000388) from Marketplace B was cancelled, so under the contract it should have produced no sales, no commission, and no payout row. However, the June 17 payout PB-2026W24 charged a commission of $4.81 on it, which left that order with a net payout of -$4.81. The $4.81 should be returned to Harbor Taco Co. by Marketplace B.

### F-0010: refund_without_pos_refund (MPB-500259)

Marketplace B, LOC-1, payout PB-2026W25

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 11.64 |
| Difference | 11.64 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-000603 (delivery, completed, 2026-06-19 13:57) |
| POS subtotal / promo / tip / refund | 50.59 / 0.00 / 7.59 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W25 (paid 2026-06-24) |
| Payout gross / rate / commission | 50.59 / 0.20 / 10.12 |
| Payout tip / refund / adjustments / net | 7.59 / 11.64 / 0.00 / 36.42 |

**Explanation** (confidence: high): Marketplace B's payout PB-2026W25 deducted an $11.64 refund from order MPB-500259 (POS order HTC-000603), but the POS shows no refund on this order ($0.00). Commission ($10.12 at the contract rate of 0.20) and the $7.59 tip were handled correctly, so the only problem is this $11.64 deduction, which left the net payout at $36.42 instead of what it should have been without a refund. You may want to ask Marketplace B to document the refund or return the $11.64 if it was not actually given to the customer.

### F-0011: missing_from_payout (MPA-100460)

Marketplace A, LOC-2

| | |
|---|---|
| Field | net_payout |
| Expected | 71.78 |
| Actual | 0.00 |
| Difference | -71.78 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-000793 (delivery, completed, 2026-06-25 11:37) |
| POS subtotal / promo / tip / refund | 79.28 / 10.00 / 19.82 / 0.00 |
| Contract rate on order date | 0.25 |

**Explanation** (confidence: high): Order MPA-100460 from Marketplace A (delivery, placed June 25, 2026) was completed, so it should have appeared in a payout, but no payout row exists for it. The expected net payout is $71.78, and the amount actually received is $0.00, leaving Harbor Taco Co. short by $71.78. Because this is a missing row rather than a timing slip near the end of a payout week, it is worth raising with Marketplace A.

### F-0012: tip_not_fully_passed_through (MPA-100507)

Marketplace A, LOC-2, payout PA-2026W26

| | |
|---|---|
| Field | tip_passed_through |
| Expected | 3.90 |
| Actual | 0.00 |
| Difference | -3.90 |
| Match status | matched |
| Contract rule | Rule 5: tips pass through at 100%. |
| POS order | HTC-000877 (delivery, completed, 2026-06-27 13:26) |
| POS subtotal / promo / tip / refund | 21.64 / 0.00 / 3.90 / 0.00 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W26 (paid 2026-07-01) |
| Payout gross / rate / commission | 21.64 / 0.25 / 5.41 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / 16.23 |

**Explanation** (confidence: high): Order MPA-100507 (Marketplace A, payout PA-2026W26) included a $3.90 tip, but the payout passed through $0.00 of it. Under Rule 5, tips go to the merchant at 100%, so the payout is short by $3.90. The sales amount of $21.64 and the commission of $5.41 at the contract rate of 25% are correct, so the tip is the only issue.

### F-0013: refund_deducted_twice (MPB-500374)

Marketplace B, LOC-1, payout PB-2026W26

| | |
|---|---|
| Field | refund_deducted |
| Expected | 82.31 |
| Actual | 164.62 |
| Difference | 82.31 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-000884 (delivery, refunded, 2026-06-27 17:54) |
| POS subtotal / promo / tip / refund | 82.31 / 0.00 / 0.00 / 82.31 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W26 (paid 2026-07-01) |
| Payout gross / rate / commission | 82.31 / 0.20 / 16.46 |
| Payout tip / refund / adjustments / net | 0.00 / 164.62 / 0.00 / -98.77 |

**Explanation** (confidence: high): Order MPB-500374 (HTC-000884) was fully refunded to the customer for $82.31, but Marketplace B's payout PB-2026W26 deducted $164.62, which is the refund taken out twice. Under the contract a refund is deducted only once, so the payout was short by $82.31. The commission rate of 0.20 and the $16.46 commission match the contract, so the refund deduction is the only problem.

### F-0014: refund_deducted_twice (MPB-500386)

Marketplace B, LOC-2, payout PB-2026W26

| | |
|---|---|
| Field | refund_deducted |
| Expected | 14.56 |
| Actual | 29.12 |
| Difference | 14.56 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-000900 (delivery, refunded, 2026-06-28 11:15) |
| POS subtotal / promo / tip / refund | 84.91 / 4.00 / 0.00 / 14.56 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W26 (paid 2026-07-01) |
| Payout gross / rate / commission | 80.91 / 0.20 / 16.18 |
| Payout tip / refund / adjustments / net | 0.00 / 29.12 / 0.00 / 35.61 |

**Explanation** (confidence: high): Order MPB-500386 was refunded $14.56 to the customer, but Marketplace B deducted $29.12 from payout PB-2026W26, which is the refund taken out twice. Under the contract a refund is deducted only once, so the payout was short by $14.56. The sales ($80.91), commission ($16.18) and 20% rate all match the contract, so the double-counted refund is the only problem.

### F-0015: refund_without_pos_refund (MPA-100528)

Marketplace A, LOC-3, payout PA-2026W26

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 20.02 |
| Difference | 20.02 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-000929 (delivery, completed, 2026-06-28 20:04) |
| POS subtotal / promo / tip / refund | 28.20 / 0.00 / 4.23 / 0.00 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W26 (paid 2026-07-01) |
| Payout gross / rate / commission | 28.20 / 0.25 / 7.05 |
| Payout tip / refund / adjustments / net | 4.23 / 20.02 / 0.00 / 5.36 |

**Explanation** (confidence: high): Marketplace A's payout PA-2026W26 deducted a $20.02 refund from order MPA-100528 (POS order HTC-000929), but the POS shows no refund on this order ($0.00). The commission of $7.05 at the contract's 0.25 rate, the $28.20 in gross sales, and the $4.23 tip all match the contract, so the only error is the refund, which brought the net payout down to $5.36. Unless the refund was issued to the customer outside the POS, the $20.02 should be disputed with the marketplace, or the refund recorded in the POS if it was actually given.

### F-0016: refund_without_pos_refund (MPA-100543)

Marketplace A, LOC-3, payout PA-2026W27

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 42.31 |
| Difference | 42.31 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-000957 (delivery, completed, 2026-06-29 18:18) |
| POS subtotal / promo / tip / refund | 70.52 / 0.00 / 17.63 / 0.00 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W27 (paid 2026-07-08) |
| Payout gross / rate / commission | 70.52 / 0.25 / 17.63 |
| Payout tip / refund / adjustments / net | 17.63 / 42.31 / 0.00 / 28.21 |

**Explanation** (confidence: high): For order MPA-100543 (POS order HTC-000957), Marketplace A's payout PA-2026W27 deducted a $42.31 refund, but the POS shows no refund on this order (refund amount $0.00), so the expected deduction is $0.00. The gross sales ($70.52), the 25% commission ($17.63) and the tip ($17.63) all match the contract, so the only problem is the unexplained refund, which left the net payout at $28.21 instead of what it should have been. We suggest asking Marketplace A to document or reverse the $42.31 refund, or checking whether a refund was given to the customer that the POS never recorded.

### F-0017: refund_deducted_twice (MPA-100553)

Marketplace A, LOC-1, payout PA-2026W27

| | |
|---|---|
| Field | refund_deducted |
| Expected | 78.77 |
| Actual | 157.54 |
| Difference | 78.77 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-000979 (delivery, refunded, 2026-06-30 11:54) |
| POS subtotal / promo / tip / refund | 78.77 / 0.00 / 19.69 / 78.77 |
| Contract rate on order date | 0.25 |
| Payout row | PA-2026W27 (paid 2026-07-08) |
| Payout gross / rate / commission | 78.77 / 0.25 / 19.69 |
| Payout tip / refund / adjustments / net | 19.69 / 157.54 / 0.00 / -78.77 |

**Explanation** (confidence: high): Order MPA-100553 was fully refunded to the customer for $78.77, so under the contract that amount should have been deducted from the Marketplace A payout (PA-2026W27) only once. The payout instead deducted $157.54, which is $78.77 more than it should have been. The commission rate of 0.25, the gross sales, and the tip all match the contract, so the over-deduction is the only issue on this order.

### F-0018: commission_on_cancelled_order (MPA-100580)

Marketplace A, LOC-3, payout PA-2026W27

| | |
|---|---|
| Field | commission_amount |
| Expected | 0.00 |
| Actual | 6.30 |
| Difference | 6.30 |
| Match status | matched |
| Contract rule | Rule 9: a cancelled order has no commission and no payout row. |
| POS order | HTC-001035 (delivery, cancelled, 2026-07-01 20:42) |
| POS subtotal / promo / tip / refund | 38.64 / 10.00 / 9.66 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W27 (paid 2026-07-08) |
| Payout gross / rate / commission | 0.00 / 0.22 / 6.30 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / -6.30 |

**Explanation** (confidence: high): Order MPA-100580 from Marketplace A on July 1 was cancelled, so under the contract it should have produced no sales, no commission, and no payout row. The payout PA-2026W27 (dated July 8) still charged $6.30 in commission on it, which left a net payout of -6.30 for an order that never happened. The $6.30 commission should be refunded or credited back by the marketplace.

### F-0019: commission_on_cancelled_order (MPB-500456)

Marketplace B, LOC-1, payout PB-2026W27

| | |
|---|---|
| Field | commission_amount |
| Expected | 0.00 |
| Actual | 3.87 |
| Difference | 3.87 |
| Match status | matched |
| Contract rule | Rule 9: a cancelled order has no commission and no payout row. |
| POS order | HTC-001040 (delivery, cancelled, 2026-07-01 23:33) |
| POS subtotal / promo / tip / refund | 29.33 / 10.00 / 2.93 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W27 (paid 2026-07-08) |
| Payout gross / rate / commission | 0.00 / 0.20 / 3.87 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / -3.87 |

**Explanation** (confidence: high): Order MPB-500456 from Marketplace B on July 1 was cancelled, so under the contract it should have produced no sales, no commission, and no payout row. However, payout PB-2026W27 still charged a commission of $3.87, which left a net payout of -$3.87 for that order. The $3.87 commission should be refunded or credited back, since it was charged on an order that never went through.

### F-0020: wrong_commission_rate (MPA-100710)

Marketplace A, LOC-3, payout PA-2026W28

| | |
|---|---|
| Field | commission_amount |
| Expected | 7.17 |
| Actual | 15.76 |
| Difference | 8.59 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.10; applied: 0.22. |
| POS order | HTC-001245 (pickup, completed, 2026-07-07 22:30) |
| POS subtotal / promo / tip / refund | 71.65 / 0.00 / 0.00 / 0.00 |
| Contract rate on order date | 0.10 |
| Payout row | PA-2026W28 (paid 2026-07-15) |
| Payout gross / rate / commission | 71.65 / 0.22 / 15.76 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / 55.89 |

**Explanation** (confidence: high): Marketplace A charged commission at a 22% rate on this pickup order (MPA-100710), but the contract rate for Marketplace A pickup orders on July 7 is 10%. On the $71.65 of gross sales, the commission should have been $7.17 instead of the $15.76 taken, so the payout was short by $8.59.

### F-0021: wrong_commission_rate (MPA-100740)

Marketplace A, LOC-1, payout PA-2026W28

| | |
|---|---|
| Field | commission_amount |
| Expected | 7.61 |
| Actual | 8.65 |
| Difference | 1.04 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.22; applied: 0.25. |
| POS order | HTC-001303 (delivery, completed, 2026-07-10 11:19) |
| POS subtotal / promo / tip / refund | 34.61 / 0.00 / 8.65 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W28 (paid 2026-07-15) |
| Payout gross / rate / commission | 34.61 / 0.25 / 8.65 |
| Payout tip / refund / adjustments / net | 8.65 / 0.00 / 0.00 / 34.61 |

**Explanation** (confidence: high): For delivery order MPA-100740 (placed July 10, 2026), Marketplace A charged commission at 25% instead of the contract rate of 22%. On gross sales of $34.61, that made the commission $8.65 when it should have been $7.61, so the payout was short by $1.04. The tip ($8.65), refund ($0.00) and adjustments ($0.00) all match the contract, so the commission rate is the only problem.

### F-0022: wrong_commission_rate (MPA-100779)

Marketplace A, LOC-1, payout PA-2026W28

| | |
|---|---|
| Field | commission_amount |
| Expected | 10.30 |
| Actual | 11.71 |
| Difference | 1.41 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.22; applied: 0.25. |
| POS order | HTC-001355 (delivery, completed, 2026-07-11 17:26) |
| POS subtotal / promo / tip / refund | 46.84 / 0.00 / 8.43 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W28 (paid 2026-07-15) |
| Payout gross / rate / commission | 46.84 / 0.25 / 11.71 |
| Payout tip / refund / adjustments / net | 8.43 / 0.00 / 0.00 / 43.56 |

**Explanation** (confidence: high): Marketplace A charged a 25% commission on delivery order MPA-100779 (placed July 11, 2026), but the contract rate that applied on that date is 22%. On the $46.84 of gross sales, the commission should have been $10.30 and the payout shows $11.71, so the restaurant was overcharged $1.41. The sales, tip, and refund amounts all match, so only the commission rate is wrong.

### F-0023: tip_not_fully_passed_through (MPA-100784)

Marketplace A, LOC-1, payout PA-2026W28

| | |
|---|---|
| Field | tip_passed_through |
| Expected | 2.94 |
| Actual | 2.35 |
| Difference | -0.59 |
| Match status | matched |
| Contract rule | Rule 5: tips pass through at 100%. |
| POS order | HTC-001369 (delivery, completed, 2026-07-12 11:48) |
| POS subtotal / promo / tip / refund | 19.60 / 0.00 / 2.94 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W28 (paid 2026-07-15) |
| Payout gross / rate / commission | 19.60 / 0.22 / 4.31 |
| Payout tip / refund / adjustments / net | 2.35 / 0.00 / 0.00 / 17.64 |

**Explanation** (confidence: high): Order MPA-100784 (Marketplace A, payout PA-2026W28) had a $2.94 tip at the point of sale, but the payout passed through only $2.35, which is $0.59 less than the contract's 100% tip pass-through requires. The sales and commission on this order look correct (gross sales of $19.60, commission of $4.31 at the contracted 22% delivery rate), so the shortfall comes from the tip alone. You may want to ask Marketplace A to explain the reduced tip and pay the missing $0.59.

### F-0024: refund_without_pos_refund (MPB-500628)

Marketplace B, LOC-1, payout PB-2026W29

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 16.34 |
| Difference | 16.34 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-001456 (delivery, completed, 2026-07-14 19:43) |
| POS subtotal / promo / tip / refund | 68.09 / 0.00 / 17.02 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 68.09 / 0.20 / 13.62 |
| Payout tip / refund / adjustments / net | 17.02 / 16.34 / 0.00 / 55.15 |

**Explanation** (confidence: high): Marketplace B's payout PB-2026W29 deducted a $16.34 refund from order MPB-500628 (POS order HTC-001456), but the POS shows no refund on this order ($0.00). Gross sales of $68.09, the 20% commission of $13.62, and the $17.02 tip all match the contract, so the refund is the only difference and the net payout of $55.15 is $16.34 lower than expected. You may want to ask Marketplace B for documentation of this refund, or check whether it was issued to the customer but never entered in your POS.

### F-0025: wrong_commission_rate (MPA-100844)

Marketplace A, LOC-1, payout PA-2026W29

| | |
|---|---|
| Field | commission_amount |
| Expected | 7.04 |
| Actual | 15.49 |
| Difference | 8.45 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.10; applied: 0.22. |
| POS order | HTC-001484 (pickup, completed, 2026-07-15 18:32) |
| POS subtotal / promo / tip / refund | 76.43 / 6.00 / 0.00 / 0.00 |
| Contract rate on order date | 0.10 |
| Payout row | PA-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 70.43 / 0.22 / 15.49 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / 54.94 |

**Explanation** (confidence: high): Marketplace A charged commission on pickup order MPA-100844 at 22%, but the contract rate that applied on July 15 was 10%. On the $70.43 of gross sales (the $76.43 subtotal less the $6.00 promo), the commission should have been $7.04, not the $15.49 that was taken. That means the payout was short by $8.45, which you can ask Marketplace A to correct.

### F-0026: refund_without_pos_refund (MPA-100884)

Marketplace A, LOC-1, payout PA-2026W29

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 42.49 |
| Difference | 42.49 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-001557 (delivery, completed, 2026-07-17 18:42) |
| POS subtotal / promo / tip / refund | 74.54 / 0.00 / 14.91 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 74.54 / 0.22 / 16.40 |
| Payout tip / refund / adjustments / net | 14.91 / 42.49 / 0.00 / 30.56 |

**Explanation** (confidence: high): Marketplace A deducted a $42.49 refund from payout PA-2026W29 for order MPA-100884, but your POS shows no refund on this order (refund amount $0.00). The commission of $16.40 at the contract rate of 0.22, the gross sales of $74.54, and the tip of $14.91 all match the contract, so the refund deduction is the only problem and it lowered the net payout to $30.56. You should ask Marketplace A for documentation of the refund, and if the customer was not actually refunded, request that the $42.49 be repaid.

### F-0027: missing_from_payout (MPB-500675)

Marketplace B, LOC-2

| | |
|---|---|
| Field | net_payout |
| Expected | 36.39 |
| Actual | 0.00 |
| Difference | -36.39 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-001559 (delivery, completed, 2026-07-17 19:09) |
| POS subtotal / promo / tip / refund | 44.39 / 10.00 / 8.88 / 0.00 |
| Contract rate on order date | 0.20 |

**Explanation** (confidence: high): Order MPB-500675 from Marketplace B, a completed delivery order placed on July 17, 2026, does not appear in any payout, so nothing was paid for it. Based on the contract, the payout should have been $36.39, which is the sales after the $10.00 promo, less the commission, plus the $8.88 tip. The full $36.39 is therefore unpaid and worth raising with Marketplace B.

### F-0028: commission_on_cancelled_order (MPA-100893)

Marketplace A, LOC-2, payout PA-2026W29

| | |
|---|---|
| Field | commission_amount |
| Expected | 0.00 |
| Actual | 10.82 |
| Difference | 10.82 |
| Match status | matched |
| Contract rule | Rule 9: a cancelled order has no commission and no payout row. |
| POS order | HTC-001577 (delivery, cancelled, 2026-07-18 13:48) |
| POS subtotal / promo / tip / refund | 57.16 / 8.00 / 14.29 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 0.00 / 0.22 / 10.82 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / -10.82 |

**Explanation** (confidence: high): Order MPA-100893 (Harbor Taco Co. order HTC-001577, placed July 18, 2026) was cancelled, so under the contract it should have produced no sales, no commission, and no payout row. Marketplace A nonetheless charged a commission of $10.82 on it in payout PA-2026W29, which left that row with a net payout of -$10.82. The $10.82 should be recovered from Marketplace A, since the expected commission is $0.00.

### F-0029: wrong_commission_rate (MPA-100902)

Marketplace A, LOC-2, payout PA-2026W29

| | |
|---|---|
| Field | commission_amount |
| Expected | 5.85 |
| Actual | 6.65 |
| Difference | 0.80 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.22; applied: 0.25. |
| POS order | HTC-001593 (delivery, completed, 2026-07-18 23:04) |
| POS subtotal / promo / tip / refund | 36.58 / 10.00 / 5.49 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 26.58 / 0.25 / 6.65 |
| Payout tip / refund / adjustments / net | 5.49 / 0.00 / 0.00 / 25.42 |

**Explanation** (confidence: high): For order MPA-100902 (a delivery order placed July 18 at 11:04 PM), Marketplace A charged commission at a 25% rate, but the contract rate that applies to this order is 22%. On gross sales of $26.58 (the $36.58 subtotal minus the $10.00 promo), that means commission should have been $5.85 rather than the $6.65 charged, so the payout was short by $0.80. You can ask Marketplace A to correct the rate and refund the $0.80 difference.

### F-0030: commission_on_cancelled_order (MPB-500703)

Marketplace B, LOC-3, payout PB-2026W29

| | |
|---|---|
| Field | commission_amount |
| Expected | 0.00 |
| Actual | 12.06 |
| Difference | 12.06 |
| Match status | matched |
| Contract rule | Rule 9: a cancelled order has no commission and no payout row. |
| POS order | HTC-001627 (delivery, cancelled, 2026-07-19 20:32) |
| POS subtotal / promo / tip / refund | 60.30 / 0.00 / 9.05 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 0.00 / 0.20 / 12.06 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / -12.06 |

**Explanation** (confidence: high): Order MPB-500703 from Marketplace B (HTC-001627, placed July 19 for delivery) was cancelled, so under the contract it should have produced no sales, no commission, and no payout row. Marketplace B still charged a $12.06 commission on it in payout PB-2026W29, which left that order with a net payout of -$12.06. The commission should be $0.00, so you can ask Marketplace B to reverse the $12.06 charge.

### F-0031: wrong_commission_rate (MPA-100928)

Marketplace A, LOC-2, payout PA-2026W29

| | |
|---|---|
| Field | commission_amount |
| Expected | 2.57 |
| Actual | 2.92 |
| Difference | 0.35 |
| Match status | matched |
| Contract rule | Rule 3: commission rate is the contract rate for the marketplace and order type with the latest effective date on or before the order date. Applicable rate: 0.22; applied: 0.25. |
| POS order | HTC-001632 (delivery, completed, 2026-07-19 22:56) |
| POS subtotal / promo / tip / refund | 17.69 / 6.00 / 4.42 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W29 (paid 2026-07-22) |
| Payout gross / rate / commission | 11.69 / 0.25 / 2.92 |
| Payout tip / refund / adjustments / net | 4.42 / 0.00 / 0.00 / 13.19 |

**Explanation** (confidence: high): Order MPA-100928, a delivery order placed on July 19, 2026, was charged commission at 25% when the contract rate that applies to it is 22%. On gross sales of $11.69 (the $17.69 subtotal less the $6.00 promo), that produced commission of $2.92 instead of the expected $2.57, so the payout was short by $0.35. The order was otherwise handled correctly: the $4.42 tip passed through in full and no refund or adjustment applied.

### F-0032: missing_from_payout (MPB-500757)

Marketplace B, LOC-1

| | |
|---|---|
| Field | net_payout |
| Expected | 40.61 |
| Actual | 0.00 |
| Difference | -40.61 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-001734 (delivery, completed, 2026-07-23 12:43) |
| POS subtotal / promo / tip / refund | 50.76 / 0.00 / 0.00 / 0.00 |
| Contract rate on order date | 0.20 |

**Explanation** (confidence: high): Order MPB-500757 (delivery, placed July 23, 2026 at 12:43) was completed, but Marketplace B's payout records have no row for it. Under the contract, a completed order must be paid out, and based on the order's details the payout should have been $40.61, so the full $40.61 is unpaid. This is not a timing issue, since the order was placed midday and not near the end of a payout week.

### F-0033: refund_deducted_twice (MPB-500763)

Marketplace B, LOC-2, payout PB-2026W30

| | |
|---|---|
| Field | refund_deducted |
| Expected | 51.88 |
| Actual | 103.76 |
| Difference | 51.88 |
| Match status | matched |
| Contract rule | Rule 6: a refund is deducted once, in the amount refunded to the customer. |
| POS order | HTC-001751 (delivery, refunded, 2026-07-23 18:24) |
| POS subtotal / promo / tip / refund | 51.88 / 0.00 / 0.00 / 51.88 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W30 (paid 2026-07-29) |
| Payout gross / rate / commission | 51.88 / 0.20 / 10.38 |
| Payout tip / refund / adjustments / net | 0.00 / 103.76 / 0.00 / -62.26 |

**Explanation** (confidence: high): Order MPB-500763 on Marketplace B was fully refunded to the customer for $51.88, but the payout PB-2026W30 deducted $103.76, which is the refund taken out twice. Under the contract a refund is deducted only once, so the extra $51.88 was wrongly taken from the restaurant. The commission rate of 0.20 and the $10.38 commission match the contract, so the refund deduction is the only problem.

### F-0034: refund_without_pos_refund (MPB-500772)

Marketplace B, LOC-1, payout PB-2026W30

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 40.35 |
| Difference | 40.35 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-001765 (pickup, completed, 2026-07-24 11:29) |
| POS subtotal / promo / tip / refund | 43.86 / 0.00 / 0.00 / 0.00 |
| Contract rate on order date | 0.08 |
| Payout row | PB-2026W30 (paid 2026-07-29) |
| Payout gross / rate / commission | 43.86 / 0.08 / 3.51 |
| Payout tip / refund / adjustments / net | 0.00 / 40.35 / 0.00 / 0.00 |

**Explanation** (confidence: high): Marketplace B deducted a $40.35 refund from payout PB-2026W30 for order MPB-500772, but the POS shows no refund on the matching order HTC-001765 ($0.00 refunded), so the expected deduction is $0.00. Because of this deduction, the payout's net for this order came to $0.00 even though the order was completed and the sales ($43.86) and commission ($3.51 at the contract's 8% pickup rate) are otherwise correct. Check whether a refund was actually given to the customer and not entered in the POS, or whether the marketplace deducted it in error and should reimburse the $40.35.

### F-0035: missing_from_payout (MPA-101035)

Marketplace A, LOC-2

| | |
|---|---|
| Field | net_payout |
| Expected | 47.00 |
| Actual | 0.00 |
| Difference | -47.00 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-001849 (delivery, completed, 2026-07-26 13:34) |
| POS subtotal / promo / tip / refund | 48.96 / 0.00 / 8.81 / 0.00 |
| Contract rate on order date | 0.22 |

**Explanation** (confidence: high): Order MPA-101035 from Marketplace A (delivery, placed July 26, 2026) was completed and should have paid out $47.00, but no payout row exists for it, so the actual payout is $0.00 and you are short $47.00. Under the contract, every completed order must appear in a payout, and nothing in the evidence suggests a normal end-of-week timing delay or a cancellation. You may want to ask Marketplace A to locate or issue this payout, and to check the following week's payout in case it settled there.

### F-0036: tip_not_fully_passed_through (MPB-500837)

Marketplace B, LOC-1, payout PB-2026W31

| | |
|---|---|
| Field | tip_passed_through |
| Expected | 5.37 |
| Actual | 0.00 |
| Difference | -5.37 |
| Match status | matched |
| Contract rule | Rule 5: tips pass through at 100%. |
| POS order | HTC-001895 (delivery, completed, 2026-07-27 13:30) |
| POS subtotal / promo / tip / refund | 53.69 / 0.00 / 5.37 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W31 (paid 2026-08-05) |
| Payout gross / rate / commission | 53.69 / 0.20 / 10.74 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / 42.95 |

**Explanation** (confidence: high): Order MPB-500837 on Marketplace B (payout PB-2026W31) had a $5.37 tip, but the payout passed through $0.00 of it. The contract says tips go to the restaurant at 100%, so the restaurant is short $5.37. The sales amount of $53.69 and the commission of $10.74 at the 20% rate are correct, so the tip is the only problem with this order.

### F-0037: tip_not_fully_passed_through (MPA-101070)

Marketplace A, LOC-1, payout PA-2026W31

| | |
|---|---|
| Field | tip_passed_through |
| Expected | 1.93 |
| Actual | 0.97 |
| Difference | -0.96 |
| Match status | matched |
| Contract rule | Rule 5: tips pass through at 100%. |
| POS order | HTC-001912 (delivery, completed, 2026-07-27 20:59) |
| POS subtotal / promo / tip / refund | 12.87 / 0.00 / 1.93 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W31 (paid 2026-08-05) |
| Payout gross / rate / commission | 12.87 / 0.22 / 2.83 |
| Payout tip / refund / adjustments / net | 0.97 / 0.00 / 0.00 / 11.01 |

**Explanation** (confidence: high): For order MPA-101070 (Marketplace A, payout PA-2026W31), the customer left a $1.93 tip, and the contract says tips pass through to the restaurant at 100%. The payout only passed through $0.97, which is $0.96 less than it should have been. The commission rate of 0.22 and the gross sales of $12.87 match the contract, so the shortfall is only in the tip.

### F-0038: refund_without_pos_refund (MPA-101096)

Marketplace A, LOC-3, payout PA-2026W31

| | |
|---|---|
| Field | refund_deducted |
| Expected | 0.00 |
| Actual | 13.03 |
| Difference | 13.03 |
| Match status | matched |
| Contract rule | Rule 6: only refunds recorded in the POS are deducted from a payout. |
| POS order | HTC-001953 (delivery, completed, 2026-07-28 23:30) |
| POS subtotal / promo / tip / refund | 29.61 / 0.00 / 4.44 / 0.00 |
| Contract rate on order date | 0.22 |
| Payout row | PA-2026W31 (paid 2026-08-05) |
| Payout gross / rate / commission | 29.61 / 0.22 / 6.51 |
| Payout tip / refund / adjustments / net | 4.44 / 13.03 / 0.00 / 14.51 |

**Explanation** (confidence: high): Marketplace A's payout PA-2026W31 deducted a $13.03 refund from order MPA-101096, but our POS shows no refund for this order (refund amount $0.00). The commission of $6.51 at the contract rate of 22% and the $4.44 tip are correct, so the only error is the refund, and the net payout of $14.51 is $13.03 lower than it should be. Ask the marketplace for documentation of the refund, or request that they reimburse the $13.03.

### F-0039: commission_on_cancelled_order (MPB-500861)

Marketplace B, LOC-3, payout PB-2026W31

| | |
|---|---|
| Field | commission_amount |
| Expected | 0.00 |
| Actual | 8.06 |
| Difference | 8.06 |
| Match status | matched |
| Contract rule | Rule 9: a cancelled order has no commission and no payout row. |
| POS order | HTC-001962 (delivery, cancelled, 2026-07-29 11:54) |
| POS subtotal / promo / tip / refund | 40.28 / 0.00 / 10.07 / 0.00 |
| Contract rate on order date | 0.20 |
| Payout row | PB-2026W31 (paid 2026-08-05) |
| Payout gross / rate / commission | 0.00 / 0.20 / 8.06 |
| Payout tip / refund / adjustments / net | 0.00 / 0.00 / 0.00 / -8.06 |

**Explanation** (confidence: high): Order MPB-500861 on Marketplace B (delivery, July 29) was cancelled, so under the contract it should have produced no sales, no commission, and no payout row. Payout PB-2026W31 still charged a commission of $8.06 on it, which drove that row's net payout to -$8.06. The $8.06 should be recovered from Marketplace B, since the expected commission is $0.00.

### F-0040: missing_from_payout (MPB-500886)

Marketplace B, LOC-2

| | |
|---|---|
| Field | net_payout |
| Expected | 20.99 |
| Actual | 0.00 |
| Difference | -20.99 |
| Match status | no_payout_row |
| Contract rule | Rules 8-9: every completed or refunded order must appear in a payout. |
| POS order | HTC-002024 (delivery, completed, 2026-07-30 23:12) |
| POS subtotal / promo / tip / refund | 23.32 / 0.00 / 2.33 / 0.00 |
| Contract rate on order date | 0.20 |

**Explanation** (confidence: high): Order MPB-500886 from Marketplace B (delivery, placed July 30, 2026 at 11:12 PM at LOC-2) was completed and should have paid out $20.99, but no payout row exists for it, so $0.00 was received and the shortfall is $20.99. This order was not placed at the end of a Sunday, so the late-week timing allowance does not explain its absence. The order appears to have been left out of the payouts entirely and should be raised with Marketplace B.
