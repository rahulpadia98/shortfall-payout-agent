# Marketplace Contract Summary: Harbor Taco Co.

Applies to Marketplace A and Marketplace B delivery and pickup orders. All
amounts are in dollars and rounded half-up to the cent.

## Sales and commission

1. **Gross sales** for an order are the order subtotal minus any promo discount.
   Promos are funded by the merchant, so they reduce both the merchant's sales
   and the amount commission is charged on.
2. **Commission** is gross sales multiplied by the commission rate, rounded
   half-up to the cent. Commission is never charged on tax or tips.
3. **Commission rate** comes from the contract rate table. For an order, use the
   rate for its marketplace and order type (delivery or pickup) with the latest
   effective date on or before the order's date (local time). A rate change
   applies to orders placed on or after its effective date, including orders
   placed just after midnight, and does not apply to earlier orders. Pickup
   orders have their own, lower rates than delivery.

## Tax, tips, and refunds

4. **Tax** is collected and remitted by the marketplace. It is not part of the
   payout.
5. **Tips** pass through to the merchant at 100%. The payout's tip equals the
   order's tip.
6. **Refunds** (full or partial) are deducted from the payout once, in the
   amount refunded to the customer. Refunds do not reverse the commission, so a
   fully refunded order shows a negative net payout. That is expected.
7. **Adjustments** are zero unless a separate written agreement says otherwise.

## Net payout

8. Net payout = gross sales - commission + tip - refund + adjustments.

## Cancelled orders

9. A cancelled order generates no sales, no commission, and no payout row.

## Payout timing

10. Payouts are made weekly per marketplace. Weeks run Monday to Sunday and the
    payout is dated the Wednesday after the week ends.
11. An order is paid in the payout for the week of its order date. Orders placed
    near the very end of a payout week (Sunday from 11:00 PM) may settle in the
    following week's payout. This is normal timing, not a discrepancy, provided
    the amounts are correct.
