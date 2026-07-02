# Dashboard, History, Insights, and Exports

Module 7 adds the portfolio-facing product experience: dashboard metrics, charts, receipt history, AI insights, and export endpoints.

## Dashboard

- Total spending
- Monthly spending
- Spending by category
- Recent receipts
- Highest expense
- Receipt count
- Pie chart and monthly bar chart with Chart.js

## History

The history page supports search, category filtering, sorting, and pagination.

## AI Insights

The insight service generates a monthly summary, largest category, spending habits, and saving suggestions from persisted expense data.

## Export

- CSV export: `/exports/csv`
- PDF export: `/exports/pdf`

Both endpoints are protected with Flask-Login and export only the current user’s data.
