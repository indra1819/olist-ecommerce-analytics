
import os
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Olist Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# =====================================================
# 2. PROFESSIONAL THEME
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
    color: #F1F5F9;
}

[data-testid="stSidebar"] {
    background-color: #111C30;
    border-right: 1px solid #263650;
}

[data-testid="stHeader"] {
    background-color: #0B1220;
}

h1, h2, h3, h4 {
    color: #F8FAFC !important;
}

p, label, span {
    color: #CBD5E1;
}

div[data-testid="stMetric"] {
    background: #162238;
    border: 1px solid #263A56;
    padding: 18px;
    border-radius: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #AAB8D0 !important;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

div[data-testid="stExpander"] {
    background-color: #162238;
    border: 1px solid #263A56;
    border-radius: 10px;
}

.stButton button {
    border-radius: 8px;
}

hr {
    border-color: #263650;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. DATABASE CONNECTION
# =====================================================

@st.cache_resource
def get_engine():

    password = os.getenv("DB_PASSWORD")

    if not password:
        raise ValueError(
            "DB_PASSWORD missing in .env file"
        )

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER", "postgres"),
        password=password,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv(
            "DB_NAME",
            "client_pipeline_db"
        )
    )

    return create_engine(
        url,
        pool_pre_ping=True
    )


def fetch_data(query, params=None):

    with get_engine().connect() as connection:

        return pd.read_sql(
            text(query),
            connection,
            params=params
        )


# =====================================================
# 4. LOAD DASHBOARD DATA
# =====================================================

@st.cache_data(ttl=300)
def load_dashboard_data(start_date, end_date):

    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    date_filter = """
        o.order_purchase_timestamp::date
        BETWEEN :start_date AND :end_date
    """

    # -------------------------------------------------
    # KPI DATA - CORRECT UNIQUE CUSTOMER ID
    # -------------------------------------------------

    kpi = fetch_data(f"""
        SELECT

            COUNT(*) AS total_orders,

            COUNT(*) FILTER (
                WHERE o.order_status = 'delivered'
            ) AS delivered_orders,

            COUNT(*) FILTER (
                WHERE o.order_status = 'canceled'
            ) AS cancelled_orders,

            COUNT(DISTINCT c.customer_unique_id)
                AS customers

        FROM olist_orders_dataset_cleaned o

        JOIN olist_customers_dataset_cleaned c
            ON o.customer_id = c.customer_id

        WHERE {date_filter}
    """, params)

    # -------------------------------------------------
    # REVENUE
    # -------------------------------------------------

    revenue = fetch_data(f"""
        SELECT
            COALESCE(
                SUM(p.payment_value), 0
            ) AS total_revenue

        FROM olist_orders_dataset_cleaned o

        JOIN olist_order_payments_dataset_cleaned p
            ON o.order_id = p.order_id

        WHERE {date_filter}
        AND o.order_status = 'delivered'
    """, params)

    # -------------------------------------------------
    # MONTHLY REVENUE
    # -------------------------------------------------

    monthly = fetch_data(f"""
        SELECT

            DATE_TRUNC(
                'month',
                o.order_purchase_timestamp
            ) AS month,

            SUM(p.payment_value) AS revenue

        FROM olist_orders_dataset_cleaned o

        JOIN olist_order_payments_dataset_cleaned p
            ON o.order_id = p.order_id

        WHERE {date_filter}
        AND o.order_status = 'delivered'

        GROUP BY 1
        ORDER BY 1
    """, params)

    # -------------------------------------------------
    # ORDER STATUS
    # -------------------------------------------------

    status = fetch_data(f"""
        SELECT

            o.order_status,

            COUNT(*) AS total_orders

        FROM olist_orders_dataset_cleaned o

        WHERE {date_filter}

        GROUP BY o.order_status

        ORDER BY total_orders DESC
    """, params)

    # -------------------------------------------------
    # PRODUCT CATEGORY
    # -------------------------------------------------

    category = fetch_data(f"""
        SELECT

            COALESCE(
                p.product_category_name,
                'Unknown'
            ) AS category,

            COUNT(DISTINCT oi.order_id)
                AS orders,

            ROUND(
                SUM(oi.price)::numeric,
                2
            ) AS revenue

        FROM olist_order_items_dataset_cleaned oi

        JOIN olist_orders_dataset_cleaned o
            ON oi.order_id = o.order_id

        JOIN olist_products_dataset_cleaned p
            ON oi.product_id = p.product_id

        WHERE {date_filter}
        AND o.order_status = 'delivered'

        GROUP BY 1

        ORDER BY revenue DESC
    """, params)

    # -------------------------------------------------
    # PAYMENT ANALYSIS
    # -------------------------------------------------

    payment = fetch_data(f"""
        SELECT

            p.payment_type,

            COUNT(DISTINCT p.order_id) AS orders,

            ROUND(
                SUM(p.payment_value)::numeric,
                2
            ) AS revenue

        FROM olist_order_payments_dataset_cleaned p

        JOIN olist_orders_dataset_cleaned o
            ON p.order_id = o.order_id

        WHERE {date_filter}
        AND o.order_status = 'delivered'

        GROUP BY p.payment_type

        ORDER BY revenue DESC
    """, params)

    # -------------------------------------------------
    # STATE-WISE REVENUE
    # -------------------------------------------------

    state = fetch_data(f"""
        SELECT

            c.customer_state AS state,

            COUNT(DISTINCT o.order_id) AS orders,

            COUNT(
                DISTINCT c.customer_unique_id
            ) AS customers,

            ROUND(
                SUM(p.payment_value)::numeric,
                2
            ) AS revenue

        FROM olist_orders_dataset_cleaned o

        JOIN olist_customers_dataset_cleaned c
            ON o.customer_id = c.customer_id

        JOIN olist_order_payments_dataset_cleaned p
            ON o.order_id = p.order_id

        WHERE {date_filter}
        AND o.order_status = 'delivered'

        GROUP BY c.customer_state

        ORDER BY revenue DESC
    """, params)

    # -------------------------------------------------
    # CUSTOMER REVIEWS
    # -------------------------------------------------

    reviews = fetch_data(f"""
        SELECT

            r.review_score,

            COUNT(*) AS total_reviews

        FROM olist_order_reviews_dataset_cleaned r

        JOIN olist_orders_dataset_cleaned o
            ON r.order_id = o.order_id

        WHERE {date_filter}

        GROUP BY r.review_score

        ORDER BY r.review_score
    """, params)

    # -------------------------------------------------
    # DELIVERY ANALYSIS
    # -------------------------------------------------

    delivery = fetch_data(f"""
        SELECT

            ROUND(
                AVG(
                    EXTRACT(
                        EPOCH FROM (
                            o.order_delivered_customer_date
                            - o.order_purchase_timestamp
                        )
                    ) / 86400
                )::numeric,
                2
            ) AS avg_delivery_days,

            COUNT(*) FILTER (
                WHERE
                    o.order_delivered_customer_date
                    > o.order_estimated_delivery_date
            ) AS late_deliveries,

            COUNT(*) AS completed_deliveries

        FROM olist_orders_dataset_cleaned o

        WHERE {date_filter}
        AND o.order_status = 'delivered'
        AND o.order_delivered_customer_date IS NOT NULL
        AND o.order_estimated_delivery_date IS NOT NULL
    """, params)

    return {
        "kpi": kpi,
        "revenue": revenue,
        "monthly": monthly,
        "status": status,
        "category": category,
        "payment": payment,
        "state": state,
        "reviews": reviews,
        "delivery": delivery
    }


# =====================================================
# 5. CHART DESIGN
# =====================================================

def style_chart(fig, height=370):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111C30",
        plot_bgcolor="#111C30",

        font=dict(
            color="#E2E8F0",
            family="Arial",
            size=12
        ),

        title_font=dict(
            size=18,
            color="#FFFFFF"
        ),

        height=height,

        margin=dict(
            l=25,
            r=25,
            t=65,
            b=35
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#334155"
    )

    fig.update_yaxes(
        gridcolor="#263650",
        zerolinecolor="#334155"
    )

    return fig


# =====================================================
# 6. EXCEL EXPORT
# =====================================================

def create_excel_report(data):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        for name, dataframe in data.items():

            dataframe.to_excel(
                writer,
                sheet_name=name[:31],
                index=False
            )

    output.seek(0)

    return output.getvalue()


# =====================================================
# 7. SIDEBAR
# =====================================================

st.sidebar.markdown(
    """
    <h2 style="color:#FFFFFF;">
    📊 OLIST ANALYTICS
    </h2>

    <p style="color:#94A3B8;">
    Business Intelligence Platform
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.subheader("📅 Date Filter")

try:

    date_info = fetch_data("""
        SELECT

            MIN(
                order_purchase_timestamp
            )::date AS min_date,

            MAX(
                order_purchase_timestamp
            )::date AS max_date

        FROM olist_orders_dataset_cleaned
    """)

    min_date = date_info.iloc[0]["min_date"]
    max_date = date_info.iloc[0]["max_date"]

    if pd.isna(min_date) or pd.isna(max_date):

        st.error("Order dates are unavailable.")
        st.stop()

    date_range = st.sidebar.date_input(
        "Select analysis period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) != 2:

        st.info("Select both start and end dates.")
        st.stop()

    start_date, end_date = date_range

    if start_date > end_date:

        st.error("Invalid date range.")
        st.stop()

    if st.sidebar.button(
        "🔄 Refresh Dashboard",
        use_container_width=True
    ):

        st.cache_data.clear()
        st.rerun()

    st.sidebar.divider()

    st.sidebar.success("PostgreSQL Connected")

    st.sidebar.caption(
        "Source: Olist PostgreSQL Database"
    )

    # =================================================
    # 8. LOAD DATA
    # =================================================

    data = load_dashboard_data(
        start_date,
        end_date
    )

    kpi = data["kpi"].iloc[0]

    total_orders = int(
        kpi["total_orders"] or 0
    )

    delivered = int(
        kpi["delivered_orders"] or 0
    )

    cancelled = int(
        kpi["cancelled_orders"] or 0
    )

    customers = int(
        kpi["customers"] or 0
    )

    total_revenue = float(
        data["revenue"].iloc[0]["total_revenue"] or 0
    )

    cancel_rate = (
        cancelled / total_orders * 100
        if total_orders else 0
    )

    avg_order_value = (
        total_revenue / delivered
        if delivered else 0
    )

    # =================================================
    # 9. HEADER
    # =================================================

    st.markdown("""
    <h1 style="
        color:#FFFFFF;
        font-size:36px;
    ">
    📊 Olist E-Commerce Intelligence
    </h1>

    <p style="
        color:#94A3B8;
        font-size:17px;
    ">
    Executive Business Performance & Analytics
    </p>
    """, unsafe_allow_html=True)

    st.caption(
        f"Reporting Period: {start_date} to {end_date}"
    )

    st.divider()

    # =================================================
    # 10. EXECUTIVE OVERVIEW
    # =================================================

    st.subheader("Executive Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💰 Total Revenue",
        f"R$ {total_revenue:,.0f}"
    )

    c2.metric(
        "📦 Total Orders",
        f"{total_orders:,}"
    )

    c3.metric(
        "👥 Unique Customers",
        f"{customers:,}"
    )

    c4.metric(
        "❌ Cancellation Rate",
        f"{cancel_rate:.2f}%"
    )

    c5, c6, c7 = st.columns(3)

    c5.metric(
        "🚚 Delivered Orders",
        f"{delivered:,}"
    )

    c6.metric(
        "🛒 Average Order Value",
        f"R$ {avg_order_value:,.2f}"
    )

    c7.metric(
        "⚠️ Cancelled Orders",
        f"{cancelled:,}"
    )

    st.divider()

    # =================================================
    # 11. REVENUE ANALYSIS
    # =================================================

    st.subheader("💰 Revenue Performance")

    monthly = data["monthly"]

    if not monthly.empty:

        col1, col2 = st.columns(2)

        with col1:

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=monthly["month"],
                    y=monthly["revenue"],
                    mode="lines+markers",
                    name="Revenue",

                    line=dict(
                        color="#22D3EE",
                        width=3
                    ),

                    fill="tozeroy",
                    fillcolor="rgba(34,211,238,0.10)"
                )
            )

            fig.update_layout(
                title="Monthly Revenue Trend",
                xaxis_title="Month",
                yaxis_title="Revenue (R$)",
                hovermode="x unified"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                monthly.tail(12),
                x="month",
                y="revenue",
                title="Monthly Revenue Comparison",
                color="revenue",
                color_continuous_scale=[
                    "#164E63",
                    "#22D3EE"
                ]
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    else:

        st.info("No revenue data available.")

    st.divider()

    # =================================================
    # 12. ORDER ANALYSIS
    # =================================================

    st.subheader("📦 Order Performance")

    status = data["status"]

    if not status.empty:

        col1, col2 = st.columns(2)

        with col1:

            fig = px.pie(
                status,
                names="order_status",
                values="total_orders",
                hole=0.60,
                title="Order Status Distribution",
                color_discrete_sequence=[
                    "#22C55E",
                    "#EF4444",
                    "#3B82F6",
                    "#F59E0B",
                    "#A78BFA"
                ]
            )

            fig.update_traces(
                textinfo="percent+label"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                status,
                x="total_orders",
                y="order_status",
                orientation="h",
                title="Orders by Status",
                color="total_orders",
                color_continuous_scale="Blues"
            )

            fig.update_layout(
                yaxis=dict(
                    categoryorder="total ascending"
                )
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    st.divider()

    # =================================================
    # 13. PRODUCT ANALYSIS
    # =================================================

    st.subheader("🛍️ Product Category Analysis")

    category = data["category"]

    if not category.empty:

        top_categories = category.head(10)

        fig = px.bar(
            top_categories.sort_values(
                "revenue",
                ascending=True
            ),
            x="revenue",
            y="category",
            orientation="h",
            title="Top 10 Categories by Revenue",
            color="revenue",
            color_continuous_scale="Teal",
            hover_data=["orders"]
        )

        st.plotly_chart(
            style_chart(fig, 430),
            use_container_width=True
        )

    st.divider()

    # =================================================
    # 14. PAYMENT ANALYSIS
    # =================================================

    st.subheader("💳 Payment Analysis")

    payment = data["payment"]

    if not payment.empty:

        col1, col2 = st.columns(2)

        with col1:

            fig = px.pie(
                payment,
                names="payment_type",
                values="revenue",
                hole=0.55,
                title="Revenue by Payment Method",
                color_discrete_sequence=[
                    "#22D3EE",
                    "#A78BFA",
                    "#34D399",
                    "#F59E0B"
                ]
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                payment,
                x="payment_type",
                y="orders",
                title="Orders by Payment Method",
                color="orders",
                color_continuous_scale="Purples"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    st.divider()

    # =================================================
    # 15. BRAZIL INTERACTIVE MAP
    # =================================================

    st.subheader("🌎 Brazil Geographical Revenue Map")

    state = data["state"]

    # Approximate geographic centers of Brazilian states

    state_coordinates = {
        "AC": (-9.02, -70.81),
        "AL": (-9.57, -36.78),
        "AP": (1.41, -51.77),
        "AM": (-3.47, -65.10),
        "BA": (-12.97, -41.70),
        "CE": (-5.20, -39.53),
        "DF": (-15.79, -47.88),
        "ES": (-19.19, -40.34),
        "GO": (-15.83, -49.84),
        "MA": (-5.42, -45.44),
        "MT": (-12.64, -55.42),
        "MS": (-20.51, -54.54),
        "MG": (-18.51, -44.55),
        "PA": (-3.79, -52.48),
        "PB": (-7.24, -36.78),
        "PR": (-24.89, -51.55),
        "PE": (-8.28, -37.95),
        "PI": (-7.72, -42.73),
        "RJ": (-22.91, -43.20),
        "RN": (-5.79, -36.59),
        "RS": (-30.03, -51.23),
        "RO": (-10.83, -63.34),
        "RR": (2.82, -60.67),
        "SC": (-27.25, -50.21),
        "SP": (-23.55, -46.63),
        "SE": (-10.57, -37.45),
        "TO": (-10.25, -48.25)
    }

    if not state.empty:

        map_data = state.copy()

        map_data["lat"] = map_data["state"].map(
            lambda x: state_coordinates.get(x, (None, None))[0]
        )

        map_data["lon"] = map_data["state"].map(
            lambda x: state_coordinates.get(x, (None, None))[1]
        )

        map_data = map_data.dropna(
            subset=["lat", "lon"]
        )

        if not map_data.empty:

            fig = px.scatter_geo(
                map_data,
                lat="lat",
                lon="lon",
                size="revenue",
                color="revenue",
                hover_name="state",
                hover_data=[
                    "orders",
                    "customers",
                    "revenue"
                ],
                title="State-wise Revenue Distribution",
                color_continuous_scale="Turbo",
                projection="mercator",
                scope="south america",
                size_max=35
            )

            fig.update_geos(
                showcountries=True,
                countrycolor="#64748B",
                showland=True,
                landcolor="#162238",
                showocean=True,
                oceancolor="#0B1220",
                showcoastlines=True,
                coastlinecolor="#475569",
                center=dict(
                    lat=-14,
                    lon=-52
                ),
                projection_scale=2.5
            )

            st.plotly_chart(
                style_chart(fig, 550),
                use_container_width=True
            )

            st.caption(
                "Map markers represent approximate state centers. "
                "Marker size and color represent revenue."
            )

    st.divider()

    # =================================================
    # 16. STATE & CATEGORY DRILL-DOWN
    # =================================================

    st.subheader("🔎 Interactive Business Drill-Down")

    tab1, tab2 = st.tabs([
        "State Analysis",
        "Category Analysis"
    ])

    with tab1:

        if not state.empty:

            selected_state = st.selectbox(
                "Choose a Brazilian State",
                sorted(state["state"].dropna().unique())
            )

            selected_state_data = state[
                state["state"] == selected_state
            ]

            if not selected_state_data.empty:

                row = selected_state_data.iloc[0]

                a, b, c = st.columns(3)

                a.metric(
                    "State Revenue",
                    f"R$ {row['revenue']:,.2f}"
                )

                b.metric(
                    "Total Orders",
                    f"{int(row['orders']):,}"
                )

                c.metric(
                    "Unique Customers",
                    f"{int(row['customers']):,}"
                )

                fig = px.bar(
                    state,
                    x="state",
                    y="revenue",
                    title="Compare State Revenue",
                    color="revenue",
                    color_continuous_scale="Teal"
                )

                fig.add_hline(
                    y=float(row["revenue"]),
                    line_dash="dash",
                    line_color="#F59E0B"
                )

                st.plotly_chart(
                    style_chart(fig),
                    use_container_width=True
                )

        else:

            st.info("No state data available.")

    with tab2:

        if not category.empty:

            selected_category = st.selectbox(
                "Choose a Product Category",
                sorted(category["category"].dropna().unique())
            )

            selected_category_data = category[
                category["category"] == selected_category
            ]

            if not selected_category_data.empty:

                row = selected_category_data.iloc[0]

                a, b = st.columns(2)

                a.metric(
                    "Category Revenue",
                    f"R$ {row['revenue']:,.2f}"
                )

                b.metric(
                    "Total Orders",
                    f"{int(row['orders']):,}"
                )

                fig = px.bar(
                    category.head(15),
                    x="category",
                    y="revenue",
                    title="Category Revenue Comparison",
                    color="revenue",
                    color_continuous_scale="Viridis"
                )

                st.plotly_chart(
                    style_chart(fig, 430),
                    use_container_width=True
                )

        else:

            st.info("No category data available.")

    st.divider()

    # =================================================
    # 17. CUSTOMER SATISFACTION
    # =================================================

    st.subheader("⭐ Customer Satisfaction")

    reviews = data["reviews"]

    if not reviews.empty:

        total_reviews = int(
            reviews["total_reviews"].sum()
        )

        avg_rating = (
            (
                reviews["review_score"]
                * reviews["total_reviews"]
            ).sum() / total_reviews
            if total_reviews else 0
        )

        positive_reviews = reviews.loc[
            reviews["review_score"] >= 4,
            "total_reviews"
        ].sum()

        positive_rate = (
            positive_reviews / total_reviews * 100
            if total_reviews else 0
        )

        r1, r2, r3 = st.columns(3)

        r1.metric(
            "Average Rating",
            f"{avg_rating:.2f}/5"
        )

        r2.metric(
            "Total Reviews",
            f"{total_reviews:,}"
        )

        r3.metric(
            "Positive Reviews",
            f"{positive_rate:.1f}%"
        )

        fig = px.bar(
            reviews,
            x="review_score",
            y="total_reviews",
            title="Review Score Distribution",
            color="review_score",
            color_continuous_scale="RdYlGn"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    st.divider()

    # =================================================
    # 18. DELIVERY ANALYSIS
    # =================================================

    st.subheader("🚚 Delivery Performance")

    delivery = data["delivery"].iloc[0]

    avg_delivery = float(
        delivery["avg_delivery_days"] or 0
    )

    late_deliveries = int(
        delivery["late_deliveries"] or 0
    )

    completed_deliveries = int(
        delivery["completed_deliveries"] or 0
    )

    late_rate = (
        late_deliveries / completed_deliveries * 100
        if completed_deliveries else 0
    )

    d1, d2, d3 = st.columns(3)

    d1.metric(
        "Average Delivery Time",
        f"{avg_delivery:.1f} Days"
    )

    d2.metric(
        "Late Deliveries",
        f"{late_deliveries:,}"
    )

    d3.metric(
        "Late Delivery Rate",
        f"{late_rate:.2f}%"
    )

    st.divider()

    # =================================================
    # 19. AUTOMATED BUSINESS INSIGHTS
    # =================================================

    st.subheader("💡 Business Intelligence Insights")

    if not monthly.empty:

        monthly_sorted = monthly.sort_values("month")

        if len(monthly_sorted) >= 2:

            previous = float(
                monthly_sorted.iloc[-2]["revenue"]
            )

            current = float(
                monthly_sorted.iloc[-1]["revenue"]
            )

            growth = (
                (current - previous) / previous * 100
                if previous else 0
            )

            if growth >= 0:

                st.success(
                    f"📈 Monthly revenue increased by "
                    f"{growth:.2f}% compared with the previous month."
                )

            else:

                st.warning(
                    f"📉 Monthly revenue decreased by "
                    f"{abs(growth):.2f}% compared with the previous month."
                )

    if not category.empty:

        top = category.iloc[0]

        st.success(
            f"🏆 Top revenue category: {top['category']} "
            f"(R$ {top['revenue']:,.2f})"
        )

    if not state.empty:

        top = state.iloc[0]

        st.info(
            f"🌎 Highest revenue state: {top['state']} "
            f"(R$ {top['revenue']:,.2f})"
        )

    if not payment.empty:

        top = payment.iloc[0]

        st.info(
            f"💳 Leading payment method: "
            f"{top['payment_type']}"
        )

    if cancel_rate > 5:

        st.warning(
            "⚠️ Cancellation rate is above 5%. "
            "Investigate cancellation reasons."
        )

    else:

        st.success(
            "✅ Cancellation rate is below 5% "
            "for the selected period."
        )

    if late_rate > 10:

        st.warning(
            "⚠️ Late delivery rate needs attention."
        )

    # =================================================
    # 20. REPORT DOWNLOADS
    # =================================================

    st.divider()

    st.subheader("📥 Download Business Reports")

    export_data = {
        "Executive_KPIs": data["kpi"],
        "Monthly_Revenue": data["monthly"],
        "Order_Status": data["status"],
        "Product_Categories": data["category"],
        "Payment_Analysis": data["payment"],
        "State_Revenue": data["state"],
        "Customer_Reviews": data["reviews"],
        "Delivery_Analysis": data["delivery"]
    }

    col1, col2 = st.columns(2)

    with col1:

        csv_buffer = data["category"].to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📄 Download Category CSV",
            data=csv_buffer,
            file_name="olist_category_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:

        excel_file = create_excel_report(
            export_data
        )

        st.download_button(
            label="📊 Download Complete Excel Report",
            data=excel_file,
            file_name="olist_business_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )

    # =================================================
    # 21. RAW DATA PREVIEW
    # =================================================

    with st.expander("📋 View Detailed Business Data"):

        selected_data = st.selectbox(
            "Choose a report",
            list(export_data.keys())
        )

        st.dataframe(
            export_data[selected_data],
            use_container_width=True
        )

    # =================================================
    # 22. FOOTER
    # =================================================

    st.divider()

    st.markdown("""
    <div style="
        text-align:center;
        padding:20px;
        color:#94A3B8;
    ">

        <h3 style="color:#E2E8F0;">
        Olist Business Intelligence Dashboard
        </h3>

        <p>
        Powered by Python | PostgreSQL |
        Streamlit | Plotly
        </p>

        <p>
        Automated Data Analytics & Business Insights
        </p>

    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 23. ERROR HANDLING
# =====================================================

except Exception as e:

    st.error(
        f"Dashboard Error: {e}"
    )

    st.info(
        "Check PostgreSQL connection, "
        "credentials, table names and column names."
    )
