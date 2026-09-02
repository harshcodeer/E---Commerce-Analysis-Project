create database project_one

-- Check table Records Count--
select 'orders' as table_name, count(*) as record_count from orders
UNION ALL
select 'order_items' , count(*) from order_items
UNION ALL
select 'order_item_refunds', count(*) from order_item_refunds
UNION ALL
select 'products', count(*) from products
UNION ALL
select 'website_pageviews', count(*) from website_pageviews
UNION ALL
select 'website_sessions', count(*) from website_sessions

--Check Duplicates Primary Key in each tables--
--ORDERS--
select order_id, count(*) as duplicate_count from orders
group by order_id
having count(*) >1;
--ORDER_ITEMS--
select order_item_id, count(*) as duplicate_count from order_items
group by order_item_id
having count(*) >1;
--ORDER_ITEM_REFUNDS--
select order_item_refund_id, count(*) as duplicate_count from order_item_refunds
group by order_item_refund_id
having count(*) >1;
--PRODUCTS--
select product_id, count(*) as duplicate_count from products
group by product_id
having count(*) >1; 
--WEBSITE_PAGEVIEWS--
select website_pageview_id, count(*) as duplicate_count from website_pageviews
group by website_pageview_id
having count(*) >1;
--WEBSITE_SESSIONS--
select website_session_id, count(*) as duplicate_count from website_sessions
group by website_session_id
having count(*) >1;
/*Duplicate IDs can cause:
Incorrect order counts
Inflated revenue
Incorrect customer counts
Incorrect product performance
Incorrect website metrics*/

--Checking null and missing values in order table--
select
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS missing_order_id,
    SUM(CASE WHEN created_at IS NULL THEN 1 ELSE 0 END) AS missing_created_at,
    SUM(CASE WHEN website_session_id IS NULL THEN 1 ELSE 0 END) AS missing_session_id,
    SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) AS missing_user_id,
    SUM(CASE WHEN primary_product_id IS NULL THEN 1 ELSE 0 END) AS missing_product_id,
    SUM(CASE WHEN items_purchased IS NULL THEN 1 ELSE 0 END) AS missing_item_purchased,
    SUM(CASE WHEN price_usd IS NULL THEN 1 ELSE 0 END) AS missing_price,
    SUM(CASE WHEN cogs_usd IS NULL THEN 1 ELSE 0 END) AS missing_cogs
from orders;
/* Missing values in important fields can affect:
Revenue,Profit,Customer analysis,Product analysis,Website conversion,Marketing analysis,Predictive models*/

--Check negative or invalid financial values--
select * from orders
where price_usd < 0 or cogs_usd < 0;

select * from order_items
where price_usd < 0 or cogs_usd < 0;

select * from order_item_refunds
where refund_amount_usd < 0;

--check zero value transactions--
select * from orders
where price_usd=0 or cogs_usd=0;
/*A zero value might represent:
Free product,Promotional item,Data-entry issue,Missing cost,Special transaction*/

--check logical price vs cogs issues--
select * from order_items
where cogs_usd>price_usd

--check foreign key relationships--
--orders and website session--
select o.* from orders o
left join website_sessions ws on o.website_session_id = ws.website_session_id
where ws.website_session_id is null;
--orders and order_items--
select o.* from orders o
left join order_items oi on o.order_id = oi.order_id
where oi.order_id is null;
--order_items and products--
select oi.* from order_items oi
left join products p on oi.product_id = p.product_id
where p.product_id is null;
--order_item_refunds and order_items--
select r.* from order_item_refunds r
left join order_items oi on r.order_item_id = oi.order_item_id
where oi.order_item_id is null;
--order_item_refunds and orders--
select r.* from order_item_refunds r
left join orders o on r.order_id = o.order_id
where o.order_id is null;

--check order_id consistency in refunds table--
-- Check whether the order_id in the refund matches
-- the order_id associated with the refunded order item

select 
    r.order_item_refund_id, r.order_id AS refund_order_id, r.order_item_id, oi.order_id AS actual_order_id  from order_item_refunds r
join order_items oi on r.order_item_id = oi.order_item_id
where r.order_id <> oi.order_id;

--check primary item consistency--
-- Check the distinct values of is_primary_item--
select is_primary_item, COUNT(*) AS record_count from order_items
group by is_primary_item;

-- Each order should normally have one primary item--
select order_id, SUM(CASE WHEN is_primary_item = 1 THEN 1 ELSE 0 END) AS primary_item_count from order_items
group by order_id
having SUM(CASE WHEN is_primary_item = 1 THEN 1 ELSE 0 END) <> 1;

--check date/time consistency--
-- Check for missing or invalid order dates
select * from orders
where created_at IS NULL;

-- Check whether an order was created before the associated website session
select o.order_id, o.created_at as order_created_at, ws.created_at as session_created_at from orders o
join website_sessions ws on o.website_session_id = ws.website_session_id
where o.created_at < ws.created_at;

--check pageview and session integrity--
select wp.* from website_pageviews wp
left join website_sessions ws on wp.website_session_id = ws.website_session_id
where ws.website_session_id is null;

--check product creation dates--
select * from products
where created_at is null;

-- check refund amount against item price --
select r.order_item_refund_id, r.order_item_id, r.refund_amount_usd, oi.price_usd from order_item_refunds r
join order_items oi on r.order_item_id = oi.order_item_id
where r.refund_amount_usd > oi.price_usd;

--order items that have multiple refund records--
select order_item_id, count(*) AS refund_count, sum(refund_amount_usd) AS total_refunded from order_item_refunds
group by order_item_id
having count(*) > 1;

-- Check the distribution of first-time and repeat sessions
select is_repeat_session, count(*) AS session_count from website_sessions
group by is_repeat_session;
-- invalid repeat-session indicators
select * from website_sessions
where is_repeat_session not in  (0,1) or is_repeat_session is null;

-- Review marketing sources
select utm_source, count(*) AS session_count from website_sessions
group by utm_source
order by session_count desc;

select utm_campaign,count(*) AS session_count from website_sessions
group by utm_campaign
order by session_count desc;

-- Review the most frequently visited website pages
select pageview_url, count(*) AS pageview_count from website_pageviews
group by pageview_url
order by pageview_count desc;

-- Compare the number of order items with the quantity recorded in the order
select o.order_id, o.items_purchased, count(oi.order_item_id) AS order_item_count from orders o
left join order_items oi on o.order_id = oi.order_id
group by o.order_id, o.items_purchased
having o.items_purchased <> count(oi.order_item_id);

-- Compare order-level price with the sum of item-level prices
select o.order_id, o.price_usd AS order_price, sum(oi.price_usd) AS item_price_total from orders o
join order_items oi on o.order_id = oi.order_id
group by o.order_id, o.price_usd
having o.price_usd <> sum(oi.price_usd);