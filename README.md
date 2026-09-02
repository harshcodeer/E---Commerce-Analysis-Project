# 📊 Project Overview

The objective of this project is to develop a comprehensive analytics solution for an e-commerce startup selling stuffed animal toys.

The application combines data from:

- Orders
- Order Items
- Refunds
- Website Sessions
- Website Pageviews
- Products

The data is stored in **Microsoft SQL Server** and accessed through Python using **PyODBC**.

The cleaned and analyzed data is presented through an interactive **Streamlit dashboard**.

The dashboard allows business stakeholders to monitor important KPIs, identify trends, diagnose business problems, and make data-driven decisions.

---

# 🏢 Business Context

The company is a newly launched e-commerce retail startup specializing in stuffed animal toys.

The company is preparing for its next round of funding and needs a strong data-driven story to demonstrate:

- Business growth
- Revenue performance
- Product performance
- Customer behavior
- Website performance
- Marketing effectiveness
- Refund patterns
- Growth opportunities

The CEO and other business stakeholders need an analytics solution that provides a centralized view of business performance.

Instead of relying on basic reports, the company wants to move toward **data-driven decision-making**.

---

# ❓ Problem Statement

The company has data distributed across multiple business areas including sales, products, refunds, website activity, and marketing sources.

The major business problems are:

1. Lack of a centralized view of business performance.
2. Difficulty in monitoring revenue, orders, customers, profit, and AOV.
3. Limited understanding of product-level revenue contribution.
4. Difficulty identifying high-performing and underperforming marketing sources.
5. Lack of visibility into website sessions and customer browsing behavior.
6. Increasing refund activity that requires investigation.
7. Difficulty identifying opportunities for business growth.
8. Need for stakeholder-specific dashboards and KPIs.
9. Need to transform raw transactional data into actionable business insights.
10. Need for analytics-driven recommendations to support future funding and growth decisions.

---

# 🎯 Project Objectives

The main objectives of this project are:

- Build an end-to-end e-commerce analytics solution.
- Integrate multiple business data sources.
- Store and manage data using SQL Server.
- Perform data analysis using Python.
- Calculate important business KPIs.
- Analyze revenue and order trends.
- Evaluate product performance.
- Analyze website traffic and customer behavior.
- Measure marketing-source performance.
- Analyze refunds and identify unusual patterns.
- Create stakeholder-specific dashboards.
- Provide actionable business recommendations.
- Build an interactive Streamlit application.
- Provide secure access through a username/password login interface.
- Support data-driven decision-making for future business growth.

---

# 👥 Business Stakeholders

## 1. Cindy Sharp — CEO

The CEO needs a high-level overview of the company's overall performance.

### Key requirements:

- Total Revenue
- Total Orders
- Total Customers
- Gross Profit
- Gross Margin
- Average Order Value
- Revenue Trends
- Product Performance
- Refund Performance
- Overall Business Growth

### Business Goal:

Understand whether the company is growing sustainably and identify areas that can support the next funding round.

---

## 2. Morgan Rockwell — Website Manager

The Website Manager focuses on website traffic and customer browsing behavior.

### Key requirements:

- Website Sessions
- Repeat Sessions
- New vs Repeat Visitors
- Pageviews
- Device Performance
- Landing Page Performance
- Website Conversion
- Traffic Trends

### Business Goal:

Improve website performance and identify opportunities to increase conversion.

---

## 3. Tom Parmesan — Marketing Director

The Marketing Director focuses on marketing channels and campaign performance.

### Key requirements:

- Revenue by Marketing Source
- Revenue by Campaign
- Marketing Traffic
- Marketing Performance
- Source-level performance
- Campaign-level performance
- Customer acquisition opportunities

### Business Goal:

Identify the highest-performing marketing sources and optimize marketing investment.

---

# 🔍 Key Business Questions

The project addresses questions such as:

### Business Performance

- What is the total revenue?
- How many orders were generated?
- What is the average order value?
- How much gross profit was generated?
- What is the gross margin?
- How is revenue changing over time?

### Product Performance

- Which products generate the most revenue?
- Which products contribute the most to sales?
- Is revenue concentrated in a small number of products?
- Which products should receive more marketing attention?

### Marketing Performance

- Which marketing source generates the highest revenue?
- Which sources contribute the least revenue?
- Which traffic sources should receive additional investment?
- Is there a significant amount of unattributed traffic?

### Website Performance

- How many website sessions are generated?
- What proportion of visitors are repeat visitors?
- Which devices generate the most activity?
- Which website pages receive the most views?
- How effectively does website traffic convert into orders?

### Refund Analysis

- How much money is being refunded?
- How are refunds changing over time?
- Are there unusual spikes in refunds?
- Which products contribute to refunds?

---

# 🗄️ Dataset

The project uses six major relational tables.

## 1. Orders

Contains order-level information.

| Column | Description |
|---|---|
| order_id | Unique order identifier |
| created_at | Order creation timestamp |
| website_session_id | Website session associated with the order |
| user_id | Customer identifier |
| primary_product_id | Primary product purchased |
| item_purchased | Number of items purchased |
| price_usd | Order/product selling price |
| cogs_usd | Cost of Goods Sold |

---

## 2. Order_items

Contains individual products purchased within orders.

| Column | Description |
|---|---|
| order_item_id | Unique order item identifier |
| created_at | Order item creation timestamp |
| order_id | Order identifier |
| product_id | Product identifier |
| is_primary_item | Indicates primary product |
| price_usd | Product selling price |
| cogs_usd | Cost of Goods Sold |

---

## 3. Order_items_refunds

Contains refund information.

| Column | Description |
|---|---|
| order_items_refund_id | Unique refund identifier |
| created_at | Refund timestamp |
| order_item_id | Order item identifier |
| order_id | Order identifier |
| refund_amount_usd | Refund amount |

---

## 4. Website_sessions

Contains website session and marketing information.

| Column | Description |
|---|---|
| website_session_id | Unique session identifier |
| created_at | Session timestamp |
| user_id | Customer identifier |
| is_repeat_session | Indicates repeat session |
| utm_source | Marketing source |
| utm_campaign | Marketing campaign |
| utm_content | Marketing content |
| device_type | Device used |
| http_referer | Referral source |

---

## 5. Website_pageviews

Contains individual website pageview information.

| Column | Description |
|---|---|
| website_pageview_id | Unique pageview identifier |
| created_at | Pageview timestamp |
| website_session_id | Website session identifier |
| pageview_url | URL/page visited |

---

## 6. Products

Contains product master information.

| Column | Description |
|---|---|
| product_id | Unique product identifier |
| created_at | Product creation date |
| product_name | Product name |

---

# 🔗 Database Relationships

The major relationships are:

```text
                    ┌──────────────┐
                    │   Products   │
                    │  product_id  │
                    └───────┬──────┘
                            │
                            │
                    ┌───────▼────────┐
                    │  Order_items   │
                    │ order_item_id  │
                    │ product_id     │
                    │ order_id       │
                    └───────┬────────┘
                            │
                            │
                    ┌───────▼──────────────┐
                    │ Order_items_refunds  │
                    │ order_items_refund_id│
                    │ order_item_id        │
                    │ order_id             │
                    └──────────────────────┘

                    ┌──────────────┐
                    │    Orders    │
                    │   order_id   │
                    │   user_id    │
                    │ session_id   │
                    └───────┬──────┘
                            │
                            │
                    ┌───────▼────────────┐
                    │ Website_sessions   │
                    │ website_session_id │
                    │ user_id            │
                    │ utm_source         │
                    │ utm_campaign       │
                    └────────┬───────────┘
                             │
                             │
                    ┌────────▼────────────┐
                    │ Website_pageviews  │
                    │ website_pageview_id│
                    │ website_session_id │
                    └─────────────────────┘
