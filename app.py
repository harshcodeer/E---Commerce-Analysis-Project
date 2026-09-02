import joblib

model = joblib.load(
    "purchase_prediction_model.pkl"
)
# ============================================================
# E-COMMERCE ANALYTICS STREAMLIT APP
# DESCRIPTIVE + DIAGNOSTIC + PREDICTIVE ANALYTICS 
# ============================================================ 
import streamlit as st
import pandas as pd
import numpy as np
import pyodbc
import plotly.express as px
import plotly.graph_objects as go 
from sklearn.model_selection import train_test_split 
from sklearn.compose import ColumnTransformer 
from sklearn.pipeline import Pipeline 
from sklearn.preprocessing import OneHotEncoder, StandardScaler 
from sklearn.impute import SimpleImputer 
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier 
from sklearn.metrics import ( accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report, roc_curve )
# ---------------- LOGIN DETAILS ----------------
USERNAME = "PankajKumar"
PASSWORD = "harshydv"


def login():
    st.title("🔐 E-Commerce Analytics Dashboard")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# ---------------- CHECK LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()
# ============================================================ 
# 1. PAGE CONFIGURATION 
# ============================================================ 
st.set_page_config( page_title="E-Commerce Analytics", page_icon="🛒", layout="wide" ) 
st.title("🛒 E-Commerce Analytics Dashboard") 
st.markdown( """ 
                 **Descriptive Analytics | Diagnostic Analytics | Predictive Analytics** 
                 Business objective: Analyze business performance, website behavior, marketing effectiveness, product performance and customer purchase behavior.              """ )
# ============================================================ 
# 2. SQL SERVER CONNECTION 
# ============================================================
import streamlit as st
import pandas as pd
import pyodbc

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=PANKAJ\SQLEXPRESS;"
    "DATABASE=project_one;"
    "Trusted_Connection=yes;"
)


@st.cache_data
def load_data():
    conn = pyodbc.connect(CONNECTION_STRING)

    orders = pd.read_sql("SELECT * FROM dbo.Orders", conn)
    order_items = pd.read_sql("SELECT * FROM dbo.Order_items", conn)
    refunds = pd.read_sql("SELECT * FROM dbo.Order_item_refunds", conn)
    sessions = pd.read_sql("SELECT * FROM dbo.Website_sessions", conn)
    pageviews = pd.read_sql("SELECT * FROM dbo.Website_pageviews", conn)
    products = pd.read_sql("SELECT * FROM dbo.Products", conn)

    conn.close()

    return orders, order_items, refunds, sessions, pageviews, products


orders, order_items, refunds, sessions, pageviews, products = load_data()
# ============================================================ 
# 4. DATA CLEANING 
# ============================================================
for df in [ orders, order_items, refunds, sessions, pageviews, products ]:
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime( df["created_at"], errors="coerce" )
# Remove duplicate records
orders = orders.drop_duplicates() 
order_items = order_items.drop_duplicates() 
refunds = refunds.drop_duplicates() 
sessions = sessions.drop_duplicates( subset=["website_session_id"] ) 
pageviews = pageviews.drop_duplicates() 
products = products.drop_duplicates( subset=["product_id"] )
# Fill numerical missing values
for df in [orders, order_items]:
    for col in ["price_usd", "cogs_usd"]:
        if col in df.columns: df[col] = pd.to_numeric( df[col], errors="coerce" ) 
refunds["refund_amount_usd"] = pd.to_numeric( refunds["refund_amount_usd"], errors="coerce" )
# ============================================================
# 5. CREATE PRODUCT-LEVEL DATASET 
# ============================================================ 
order_items = order_items.merge( products[ ["product_id", "product_name"] ], on="product_id", how="left" )
# ============================================================ 
# 6. SIDEBAR FILTERS 
# ============================================================ 
st.sidebar.header("🔎 Filters") 
min_date = min( orders["created_at"].min(), sessions["created_at"].min() ).date() 
max_date = max( orders["created_at"].max(), sessions["created_at"].max() ).date() 
selected_date = st.sidebar.date_input( "Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date ) 
if len(selected_date) == 2:
    start_date = pd.Timestamp( selected_date[0] ) 
    end_date = ( pd.Timestamp(selected_date[1]) + pd.Timedelta(days=1) ) 
else: 
    start_date = pd.Timestamp(min_date) 
    end_date = ( pd.Timestamp(max_date) + pd.Timedelta(days=1) )
# Device filter 
device_list = sorted( sessions["device_type"] .dropna() .unique() )
selected_devices = st.sidebar.multiselect( "Device Type", device_list, default=device_list )    
# Marketing source 
source_list = sorted( sessions["utm_source"] .dropna() .unique() ) 
selected_sources = st.sidebar.multiselect( "UTM Source", source_list, default=source_list ) 
# ============================================================
# 7. APPLY FILTERS 
# ============================================================ 
filtered_sessions = sessions[ (sessions["created_at"] >= start_date) & (sessions["created_at"] < end_date) & (sessions["device_type"].isin(selected_devices)) & (sessions["utm_source"].isin(selected_sources)) ] 
filtered_orders = orders[ (orders["created_at"] >= start_date) & (orders["created_at"] < end_date) ] 
filtered_order_ids = filtered_orders[ "order_id" ].unique() 
filtered_order_items = order_items[ order_items["order_id"].isin( filtered_order_ids ) ] 
filtered_refunds = refunds[ (refunds["created_at"] >= start_date) & (refunds["created_at"] < end_date) ]
# ============================================================
# 8. CALCULATE KPIs 
# ============================================================
total_revenue = filtered_order_items[ "price_usd" ].sum() 
total_orders = filtered_orders[ "order_id" ].nunique()
total_customers = filtered_orders[ "user_id" ].nunique()
total_cogs = filtered_order_items[ "cogs_usd" ].sum() 
gross_profit = ( total_revenue - total_cogs ) 
gross_margin = ( gross_profit / total_revenue * 100 if total_revenue > 0 else 0 ) 
aov = ( total_revenue / total_orders if total_orders > 0 else 0 ) 
total_sessions = filtered_sessions[ "website_session_id" ].nunique() 
total_pageviews = pageviews[ (pageviews["created_at"] >= start_date) & (pageviews["created_at"] < end_date) ][ "website_pageview_id" ].nunique() 
conversion_rate = ( total_orders / total_sessions * 100 if total_sessions > 0 else 0 )
total_refunds = filtered_refunds[ "refund_amount_usd" ].sum() 
refund_rate = ( total_refunds / total_revenue * 100 if total_revenue > 0 else 0 )
# ============================================================
# 9. CREATE TABS 
# ============================================================
tab1, tab2, tab3 = st.tabs( [ "📊 Descriptive Analytics", "🔍 Diagnostic Analytics", "🤖 Predictive Analytics" ] )
# ============================================================
# ============================================================ 
# TAB 1 — DESCRIPTIVE ANALYTICS 
# ============================================================
# ============================================================
with tab1: 
    st.header("📊 Descriptive Analytics") 
    st.write( "Descriptive analytics explains what happened in the business." )
    # -------------------------------------------------------- 
    # KPI CARDS 
    # --------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5) 
    col1.metric( "Total Revenue", f"${total_revenue:,.2f}" ) 
    col2.metric( "Total Orders", f"{total_orders:,}" ) 
    col3.metric( "Total Customers", f"{total_customers:,}" ) 
    col4.metric( "Gross Profit", f"${gross_profit:,.2f}" ) 
    col5.metric( "AOV", f"${aov:,.2f}" ) 
    col6, col7, col8, col9, col10 = st.columns(5) 
    col6.metric( "Gross Margin", f"{gross_margin:.2f}%" ) 
    col7.metric( "Sessions", f"{total_sessions:,}" ) 
    col8.metric( "Pageviews", f"{total_pageviews:,}" ) 
    col9.metric( "Conversion Rate", f"{conversion_rate:.2f}%" ) 
    col10.metric( "Refund Amount", f"${total_refunds:,.2f}" ) 
    st.divider()
    # -------------------------------------------------------- 
    # REVENUE TREND 
    # --------------------------------------------------------
    monthly_revenue = ( filtered_order_items .assign( month=lambda x: x["created_at"] .dt.to_period("M") .astype(str) ) .groupby("month") .agg( revenue=("price_usd", "sum") ) .reset_index() )
    fig = px.line( monthly_revenue, x="month", y="revenue", markers=True, title="Monthly Revenue Trend" ) 
    st.plotly_chart( fig, use_container_width=True )
    #-------------------------------------------------------- 
    # PRODUCT PERFORMANCE 
    # -------------------------------------------------------- 
    product_performance = ( filtered_order_items .groupby("product_name") .agg( revenue=("price_usd", "sum"), cogs=("cogs_usd", "sum"), orders=("order_id", "nunique") ) .reset_index() ) 
    product_performance["gross_profit"] = ( product_performance["revenue"] - product_performance["cogs"] ) 
    top_products = ( product_performance .sort_values( "revenue", ascending=False ) .head(10) ) 
    col1, col2 = st.columns(2)
    with col1: 
        fig = px.bar( top_products, x="revenue", y="product_name", orientation="h", title="Top 10 Products by Revenue" ) 
        st.plotly_chart( fig, use_container_width=True )
    # -------------------------------------------------------- 
    # REFUND TREND 
    # -------------------------------------------------------- 
    monthly_refunds = ( filtered_refunds .assign( month=lambda x: x["created_at"] .dt.to_period("M") .astype(str) ) .groupby("month") .agg( refunds=("refund_amount_usd", "sum") ) .reset_index() )    
    with col2:
        fig = px.line( monthly_refunds, x="month", y="refunds", markers=True, title="Monthly Refund Trend" )
        st.plotly_chart( fig, use_container_width=True )
    # -------------------------------------------------------- 
    # DEVICE DISTRIBUTION 
    # -------------------------------------------------------- 
    device_data = ( filtered_sessions .groupby("device_type") .agg( sessions=( "website_session_id", "nunique" ) ) .reset_index() ) 
    fig = px.pie( device_data, names="device_type", values="sessions", title="Website Sessions by Device" ) 
    st.plotly_chart( fig, use_container_width=True )
# ============================================================
# ============================================================
# TAB 2 — DIAGNOSTIC ANALYTICS 
# ============================================================
# ============================================================
with tab2:
    st.header("🔍 Diagnostic Analytics") 
    st.write( "Diagnostic analytics explains why business performance changed." )
    # -------------------------------------------------------- 
    # REVENUE BY MARKETING SOURCE 
    # -------------------------------------------------------- 
    order_session_data = filtered_orders.merge( filtered_sessions[ [ "website_session_id", "utm_source", "utm_campaign", "device_type" ] ], on="website_session_id", how="left" ) 
    source_revenue = ( order_session_data .groupby("utm_source") .agg( orders=("order_id", "nunique"), revenue=("price_usd", "sum") ) .reset_index() )    
    col1, col2 = st.columns(2) 
    with col1:
        fig = px.bar( source_revenue, x="utm_source", y="revenue", title="Revenue by Marketing Source" ) 
        st.plotly_chart( fig, use_container_width=True )
    # -------------------------------------------------------- 
    # SOURCE CONVERSION 
    # -------------------------------------------------------- 
    source_sessions = ( filtered_sessions .groupby("utm_source") .agg( sessions=( "website_session_id", "nunique" ) ) .reset_index() ) 
    source_orders = ( order_session_data .groupby("utm_source") .agg( orders=("order_id", "nunique") ) .reset_index() ) 
    source_conversion = source_sessions.merge( source_orders, on="utm_source", how="left" ) 
    source_conversion["orders"] = ( source_conversion["orders"] .fillna(0) ) 
    source_conversion["conversion_rate"] = ( source_conversion["orders"] / source_conversion["sessions"] * 100 ) 
    with col2:
        fig = px.bar( source_conversion, x="utm_source", y="conversion_rate", title="Conversion Rate by Marketing Source" )
        st.plotly_chart( fig, use_container_width=True )
    # --------------------------------------------------------
    # DEVICE PERFORMANCE 
    # -------------------------------------------------------- 
    device_sessions = ( filtered_sessions .groupby("device_type") .agg( sessions=( "website_session_id", "nunique" ) ) .reset_index() ) 
    device_orders = ( order_session_data .groupby("device_type") .agg( orders=("order_id", "nunique") ) .reset_index() )
    device_analysis = device_sessions.merge( device_orders, on="device_type", how="left" ) 
    device_analysis["orders"] = ( device_analysis["orders"] .fillna(0) ) 
    device_analysis["conversion_rate"] = ( device_analysis["orders"] / device_analysis["sessions"] * 100 ) 
    fig = px.bar( device_analysis, x="device_type", y="conversion_rate", title="Website Conversion Rate by Device" ) 
    st.plotly_chart( fig, use_container_width=True )
    # -------------------------------------------------------- 
    # PRODUCT PROFITABILITY 
    # --------------------------------------------------------
    product_diagnostic = ( filtered_order_items .groupby("product_name") .agg( revenue=("price_usd", "sum"), cogs=("cogs_usd", "sum"), orders=("order_id", "nunique") ) .reset_index() ) 
    product_diagnostic["gross_profit"] = ( product_diagnostic["revenue"] - product_diagnostic["cogs"] ) 
    product_diagnostic["gross_margin"] = ( product_diagnostic["gross_profit"] / product_diagnostic["revenue"] * 100 ) 
    st.subheader( "Product Profitability Analysis" ) 
    st.dataframe( product_diagnostic .sort_values( "gross_profit", ascending=False ) .head(10), use_container_width=True )
    # -------------------------------------------------------- 
    # CORRELATION ANALYSIS 
    # -------------------------------------------------------- 
    st.subheader( "Correlation Analysis" ) 
    monthly_data = ( filtered_order_items .assign( month=lambda x: x["created_at"] .dt.to_period("M") .astype(str) ) .groupby("month") .agg( revenue=("price_usd", "sum"), cogs=("cogs_usd", "sum"), orders=("order_id", "nunique") ) .reset_index() ) 
    monthly_sessions_data = ( filtered_sessions .assign( month=lambda x: x["created_at"] .dt.to_period("M") .astype(str) ) .groupby("month") .agg( sessions=( "website_session_id", "nunique" ) ) .reset_index() ) 
    correlation_data = monthly_data.merge( monthly_sessions_data, on="month", how="left" ) 
    correlation_matrix = correlation_data[ [ "revenue", "cogs", "orders", "sessions" ] ].corr() 
    fig = px.imshow( correlation_matrix, text_auto=True, aspect="auto", title="Business Metric Correlation" ) 
    st.plotly_chart( fig, use_container_width=True )
    # --------------------------------------------------------
    # HIGH REFUND PRODUCTS 
    # -------------------------------------------------------- 
    refund_product = filtered_refunds.merge( filtered_order_items[ [ "order_item_id", "product_id", "product_name" ] ], on="order_item_id", how="left" )      
    refund_by_product = ( refund_product .groupby("product_name") .agg( refund_amount=( "refund_amount_usd", "sum" ) ) .reset_index() .sort_values( "refund_amount", ascending=False ) .head(10) ) 
    fig = px.bar( refund_by_product, x="refund_amount", y="product_name", orientation="h", title="Products with Highest Refund Amount" ) 
    st.plotly_chart( fig, use_container_width=True )
# ============================================================ 
# ============================================================ 
# TAB 3 — PREDICTIVE ANALYTICS
# ============================================================ 
# ============================================================ 
with tab3:
    st.header("🤖 Customer Purchase Prediction")
    st.write( """ Predict whether a website session will result in a purchase. **0 = No Purchase** **1 = Purchase** """ )
    # --------------------------------------------------------
    # CREATE PURCHASE TARGET 
    # -------------------------------------------------------- 
    purchase_sessions = set( orders[ "website_session_id" ].dropna() ) 
    prediction_data = sessions.copy() 
    prediction_data["purchase"] = ( prediction_data[ "website_session_id" ] .isin(purchase_sessions) .astype(int) )
    # --------------------------------------------------------
    # PAGEVIEWS 
    # -------------------------------------------------------- 
    pageview_count = ( pageviews .groupby("website_session_id") .size() .reset_index( name="total_pageviews" ) ) 
    prediction_data = prediction_data.merge( pageview_count, on="website_session_id", how="left" ) 
    prediction_data["total_pageviews"] = ( prediction_data["total_pageviews"] .fillna(0) )
    # -------------------------------------------------------- 
    #TIME FEATURES 
    # -------------------------------------------------------- 
    prediction_data["hour"] = ( prediction_data["created_at"].dt.hour ) 
    prediction_data["day_of_week"] = ( prediction_data["created_at"].dt.dayofweek )
    prediction_data["month"] = ( prediction_data["created_at"].dt.month )
    # -------------------------------------------------------- 
    # MODEL DATA 
    # -------------------------------------------------------- 
    model_features = [ "is_repeat_session", "utm_source", "utm_campaign", "utm_content", "device_type", "http_referer", "total_pageviews", "hour", "day_of_week", "month" ]
    X = prediction_data[ model_features ] 
    y = prediction_data[ "purchase" ]
    # -------------------------------------------------------- 
    # SHOW TOP 5 MODELING ROWS 
    # -------------------------------------------------------- 
    st.subheader( "Top 5 Rows Used for Predictive Modeling" ) 
    display_data = prediction_data[ [ "website_session_id" ] + model_features + [ "purchase" ] ] 
    st.dataframe( display_data.head(5), use_container_width=True )
    # -------------------------------------------------------- 
    # TARGET DISTRIBUTION 
    # -------------------------------------------------------- 
    target_counts = ( y.value_counts() .reset_index() ) 
    target_counts.columns = [ "purchase", "count" ] 
    fig = px.pie( target_counts, names="purchase", values="count", title="Purchase vs No Purchase" )
    st.plotly_chart( fig, use_container_width=True )
    # --------------------------------------------------------
    # TRAIN TEST SPLIT
    # --------------------------------------------------------
    X_train, X_test, y_train, y_test = ( train_test_split( X, y, test_size=0.20, random_state=42, stratify=y ) ) 
    # -------------------------------------------------------- 
    # PREPROCESSING 
    # -------------------------------------------------------- 
    numerical_features = [ "is_repeat_session", "total_pageviews", "hour", "day_of_week", "month" ] 
    categorical_features = [ "utm_source", "utm_campaign", "utm_content", "device_type", "http_referer" ] 
    numerical_pipeline = Pipeline( steps=[ ( "imputer", SimpleImputer( strategy="median" ) ), ( "scaler", StandardScaler() ) ] ) 
    categorical_pipeline = Pipeline( steps=[ ( "imputer", SimpleImputer( strategy="most_frequent" ) ), ( "encoder", OneHotEncoder( handle_unknown="ignore" ) ) ] ) 
    preprocessor = ColumnTransformer( transformers=[ ( "num", numerical_pipeline, numerical_features ), ( "cat", categorical_pipeline, categorical_features ) ] )
    # -------------------------------------------------------- 
    # MODELS 
    # -------------------------------------------------------- 
    logistic_model = Pipeline( steps=[ ( "preprocessor", preprocessor ), ( "classifier", LogisticRegression( max_iter=1000, class_weight="balanced" ) ) ] ) 
    random_forest_model = Pipeline( steps=[ ( "preprocessor", preprocessor ), ( "classifier", RandomForestClassifier( n_estimators=200, random_state=42, class_weight="balanced", n_jobs=-1 ) ) ] )
    # -------------------------------------------------------- 
    # TRAIN MODELS 
    # -------------------------------------------------------- 
    logistic_model.fit( X_train, y_train ) 
    random_forest_model.fit( X_train, y_train )
    # -------------------------------------------------------- 
    # PREDICTIONS 
    # -------------------------------------------------------- 
    lr_pred = logistic_model.predict( X_test ) 
    lr_prob = logistic_model.predict_proba( X_test )[:, 1] 
    rf_pred = random_forest_model.predict( X_test ) 
    rf_prob = random_forest_model.predict_proba( X_test )[:, 1]
    # -------------------------------------------------------- 
    # METRICS FUNCTION 
    # -------------------------------------------------------- 
    def calculate_metrics( y_true, prediction, probability ):
        return { "Accuracy": accuracy_score( y_true, prediction ), "Precision": precision_score( y_true, prediction, zero_division=0 ), "Recall": recall_score( y_true, prediction, zero_division=0 ), "F1 Score": f1_score( y_true, prediction, zero_division=0 ), "ROC-AUC": roc_auc_score( y_true, probability ) } 
    lr_metrics = calculate_metrics( y_test, lr_pred, lr_prob ) 
    rf_metrics = calculate_metrics( y_test, rf_pred, rf_prob )
    # -------------------------------------------------------- 
    # MODEL COMPARISON 
    # --------------------------------------------------------
    comparison = pd.DataFrame({ "Metric": [ "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC" ], 
                                "Logistic Regression": [ lr_metrics["Accuracy"], lr_metrics["Precision"], lr_metrics["Recall"], lr_metrics["F1 Score"], lr_metrics["ROC-AUC"] ], 
                                "Random Forest": [ rf_metrics["Accuracy"], rf_metrics["Precision"], rf_metrics["Recall"], rf_metrics["F1 Score"], rf_metrics["ROC-AUC"] ] }) 
    st.subheader( "Model Performance Comparison" ) 
    st.dataframe( comparison.style.format( { "Logistic Regression": "{:.4f}", "Random Forest": "{:.4f}" } ), use_container_width=True )
    # -------------------------------------------------------- 
    # DISPLAY BEST MODEL 
    # --------------------------------------------------------
    if ( rf_metrics["ROC-AUC"] > lr_metrics["ROC-AUC"] ):
        best_model_name = ( "Random Forest" )
        best_predictions = rf_pred 
        best_probabilities = rf_prob 
    else:
        best_model_name = ( "Logistic Regression" ) 
        best_predictions = lr_pred 
        best_probabilities = lr_prob
    st.success( f"Best Model based on ROC-AUC: {best_model_name}" )
    # -------------------------------------------------------- 
    # BEST MODEL KPI 
    # -------------------------------------------------------- 
    col1, col2, col3, col4, col5 = st.columns(5) 
    best_metrics = ( rf_metrics if best_model_name == "Random Forest" else lr_metrics ) 
    col1.metric( "Accuracy", f"{best_metrics['Accuracy']:.2%}" )
    col2.metric( "Precision", f"{best_metrics['Precision']:.2%}" ) 
    col3.metric( "Recall", f"{best_metrics['Recall']:.2%}" ) 
    col4.metric( "F1 Score", f"{best_metrics['F1 Score']:.2%}" ) 
    col5.metric( "ROC-AUC", f"{best_metrics['ROC-AUC']:.2%}" )
    # --------------------------------------------------------
    # CONFUSION MATRIX 
    # --------------------------------------------------------
    st.subheader( f"{best_model_name} Confusion Matrix" ) 
    cm = confusion_matrix( y_test, best_predictions )
    fig = px.imshow( cm, text_auto=True, x=[ "Predicted No Purchase", "Predicted Purchase" ], y=[ "Actual No Purchase", "Actual Purchase" ], title="Confusion Matrix" ) 
    st.plotly_chart( fig, use_container_width=True )   
    # --------------------------------------------------------
    # ROC CURVE 
    # -------------------------------------------------------- 
    lr_fpr, lr_tpr, _ = roc_curve( y_test, lr_prob ) 
    rf_fpr, rf_tpr, _ = roc_curve( y_test, rf_prob ) 
    fig = go.Figure()
    fig.add_trace( go.Scatter( x=lr_fpr, y=lr_tpr, mode="lines", name=( f"Logistic Regression " f"(AUC={lr_metrics['ROC-AUC']:.3f})" ) ) ) 
    fig.add_trace( go.Scatter( x=rf_fpr, y=rf_tpr, mode="lines", name=( f"Random Forest " f"(AUC={rf_metrics['ROC-AUC']:.3f})" ) ) )
    fig.add_trace( go.Scatter( x=[0, 1], y=[0, 1], mode="lines", name="Random Classifier" ) ) 
    fig.update_layout( title="ROC Curve Comparison", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate" ) 
    st.plotly_chart( fig, use_container_width=True )
    # -------------------------------------------------------- 
    # CLASSIFICATION REPORT 
    # --------------------------------------------------------
    st.subheader( "Classification Report" ) 
    report = classification_report( y_test, best_predictions, output_dict=True, zero_division=0 ) 
    report_df = pd.DataFrame( report ).transpose() 
    st.dataframe( report_df, use_container_width=True )
    # -------------------------------------------------------- 
    # RANDOM FOREST FEATURE IMPORTANCE 
    # -------------------------------------------------------- 
    if best_model_name == "Random Forest":
        st.subheader( "Top Features Influencing Purchase Prediction" ) 
        rf_classifier = ( random_forest_model .named_steps["classifier"] )
        rf_preprocessor = ( random_forest_model .named_steps["preprocessor"] ) 
        feature_names = ( rf_preprocessor .get_feature_names_out() )
        importance_df = pd.DataFrame({ "Feature": feature_names, "Importance": rf_classifier .feature_importances_ }) 
        importance_df = ( importance_df .sort_values( "Importance", ascending=False ) .head(15) )
        fig = px.bar( importance_df, x="Importance", y="Feature", orientation="h", title="Top 15 Predictive Features" ) 
        st.plotly_chart( fig, use_container_width=True )
# ============================================================ 
# FOOTER 
# ============================================================ 
st.divider() 
st.caption( "E-Commerce Analytics Project | " "SQL Server + Python + Machine Learning + Streamlit" )
    