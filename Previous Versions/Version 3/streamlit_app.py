from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Infrastructure BOQ Analyzer",
    page_icon="🏗️",
    layout="wide",
)


def validate_boq_data(df):
    required_columns = ["Item", "Category", "Quantity", "Unit Price"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns


def clean_numeric_data(df):
    df = df.copy()
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
    return df


def analyze_boq(df, budget=None):
    df = df.copy()
    df["Total Cost"] = df["Quantity"] * df["Unit Price"]
    total_project_cost = df["Total Cost"].sum()

    if total_project_cost == 0:
        return None

    df["Cost Share (%)"] = (df["Total Cost"] / total_project_cost) * 100

    avg_cost = df["Total Cost"].mean()
    df["Cost Level"] = df["Total Cost"].apply(
        lambda x: "High" if x > avg_cost * 1.5 else "Normal"
    )

    category_summary = (
        df.groupby("Category", as_index=False)["Total Cost"]
        .sum()
        .sort_values(by="Total Cost", ascending=False)
    )

    category_summary["Category Share (%)"] = (
        category_summary["Total Cost"] / total_project_cost
    ) * 100

    most_expensive_item = df.loc[df["Total Cost"].idxmax()]
    high_cost_items = df[df["Cost Level"] == "High"].copy()
    top_5_items = df.sort_values(by="Total Cost", ascending=False).head(5).copy()

    variance_data = None
    if budget is not None:
        variance = budget - total_project_cost
        variance_percent = (variance / budget * 100) if budget != 0 else 0

        if variance > 0:
            status = "Under Budget"
        elif variance < 0:
            status = "Over Budget"
        else:
            status = "On Budget"

        variance_data = {
            "Budget": budget,
            "Actual Cost": total_project_cost,
            "Variance": variance,
            "Variance (%)": variance_percent,
            "Budget Status": status,
        }

    return {
        "detailed_df": df,
        "category_summary": category_summary,
        "most_expensive_item": most_expensive_item,
        "high_cost_items": high_cost_items,
        "top_5_items": top_5_items,
        "variance_data": variance_data,
        "total_project_cost": total_project_cost,
    }


def create_excel_report(results):
    output = BytesIO()

    df = results["detailed_df"]
    category_summary = results["category_summary"]
    high_cost_items = results["high_cost_items"]
    top_5_items = results["top_5_items"]
    variance_data = results["variance_data"]

    summary_data = pd.DataFrame({
        "Metric": [
            "Total Project Cost",
            "Number of BOQ Items",
            "Number of Categories",
            "Number of High-Cost Items",
            "Most Expensive Item",
        ],
        "Value": [
            df["Total Cost"].sum(),
            len(df),
            df["Category"].nunique(),
            len(high_cost_items),
            results["most_expensive_item"]["Item"],
        ]
    })

    if variance_data:
        budget_sheet = pd.DataFrame({
            "Metric": list(variance_data.keys()),
            "Value": list(variance_data.values()),
        })
    else:
        budget_sheet = pd.DataFrame({
            "Metric": ["Budget Comparison"],
            "Value": ["Not Provided"],
        })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Detailed Analysis", index=False)
        category_summary.to_excel(writer, sheet_name="Category Summary", index=False)
        high_cost_items.to_excel(writer, sheet_name="High Cost Items", index=False)
        top_5_items.to_excel(writer, sheet_name="Top 5 Items", index=False)
        summary_data.to_excel(writer, sheet_name="Project Summary", index=False)
        budget_sheet.to_excel(writer, sheet_name="Budget Variance", index=False)

    output.seek(0)
    return output


def rupee(value):
    return f"₹{value:,.2f}"


def inject_custom_css():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            color: #666;
            margin-bottom: 1.2rem;
        }
        .info-box {
            padding: 1rem;
            border-radius: 12px;
            background-color: #f5f7fa;
            margin-bottom: 1rem;
        }
        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()

st.markdown('<div class="main-title">🏗️ Infrastructure BOQ Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Upload a BOQ CSV file and get a polished cost analysis dashboard.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Controls")
    use_budget = st.checkbox("Enable budget comparison")
    budget = None

    if use_budget:
        budget = st.number_input(
            "Enter project budget",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    st.markdown("---")
    st.markdown("### 📄 Required CSV Columns")
    st.write("Item")
    st.write("Category")
    st.write("Quantity")
    st.write("Unit Price")

uploaded_file = st.file_uploader("Upload your BOQ CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to begin the analysis.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

missing_columns = validate_boq_data(df)
if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

df = clean_numeric_data(df)

if df["Quantity"].isnull().any() or df["Unit Price"].isnull().any():
    st.error("Quantity or Unit Price contains invalid numeric values.")
    st.stop()

results = analyze_boq(df, budget if use_budget else None)

if results is None:
    st.error("Total project cost is zero. Please check your BOQ data.")
    st.stop()

detailed_df = results["detailed_df"]
category_summary = results["category_summary"]
most_expensive_item = results["most_expensive_item"]
high_cost_items = results["high_cost_items"]
top_5_items = results["top_5_items"]
variance_data = results["variance_data"]
total_project_cost = results["total_project_cost"]

top_category = category_summary.iloc[0]["Category"]
top_category_cost = category_summary.iloc[0]["Total Cost"]
top_category_share = category_summary.iloc[0]["Category Share (%)"]

st.markdown("### 📌 Project Overview")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Project Cost", rupee(total_project_cost))
k2.metric("BOQ Items", f"{len(detailed_df)}")
k3.metric("Categories", f"{detailed_df['Category'].nunique()}")
k4.metric("High-Cost Items", f"{len(high_cost_items)}")

st.markdown("### 🧠 Smart Insights")
i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(
        f"""
        <div class="info-box">
        <b>Top Cost Category</b><br>
        {top_category}<br>
        {rupee(top_category_cost)} ({top_category_share:.2f}%)
        </div>
        """,
        unsafe_allow_html=True,
    )

with i2:
    st.markdown(
        f"""
        <div class="info-box">
        <b>Most Expensive Item</b><br>
        {most_expensive_item['Item']}<br>
        {rupee(most_expensive_item['Total Cost'])}
        </div>
        """,
        unsafe_allow_html=True,
    )

with i3:
    if high_cost_items.empty:
        insight_text = "No unusually high-cost items detected."
    else:
        insight_text = f"{len(high_cost_items)} high-cost item(s) detected."

    st.markdown(
        f"""
        <div class="info-box">
        <b>Cost Alert</b><br>
        {insight_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

if variance_data:
    st.markdown("### 📉 Budget Comparison")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Budget", rupee(variance_data["Budget"]))
    b2.metric("Actual Cost", rupee(variance_data["Actual Cost"]))
    b3.metric("Variance", rupee(variance_data["Variance"]))
    b4.metric("Status", variance_data["Budget Status"])

    if variance_data["Budget Status"] == "Over Budget":
        st.error("Project is currently over budget.")
    elif variance_data["Budget Status"] == "Under Budget":
        st.success("Project is currently under budget.")
    else:
        st.info("Project is exactly on budget.")

st.markdown("### 📊 Visual Analysis")
col1, col2 = st.columns(2)

with col1:
    fig_bar, ax_bar = plt.subplots(figsize=(8, 5))
    ax_bar.bar(category_summary["Category"], category_summary["Total Cost"])
    ax_bar.set_title("BOQ Cost by Category")
    ax_bar.set_xlabel("Category")
    ax_bar.set_ylabel("Total Cost")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig_bar)

with col2:
    fig_pie, ax_pie = plt.subplots(figsize=(7, 7))
    ax_pie.pie(
        category_summary["Total Cost"],
        labels=category_summary["Category"],
        autopct="%1.1f%%"
    )
    ax_pie.set_title("BOQ Cost Distribution")
    st.pyplot(fig_pie)

st.markdown("### 🚨 Most Expensive Item")
most_expensive_display = pd.DataFrame([most_expensive_item])[
    ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)"]
]
st.dataframe(most_expensive_display, use_container_width=True)

st.markdown("### 🔥 Top 5 Expensive Items")
st.dataframe(
    top_5_items[
        ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)"]
    ],
    use_container_width=True
)

st.markdown("### ⚠️ High-Cost Items")
if high_cost_items.empty:
    st.success("No unusually high-cost items detected.")
else:
    st.dataframe(
        high_cost_items[
            ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)", "Cost Level"]
        ],
        use_container_width=True
    )

st.markdown("### 📂 Category Filter")
categories = ["All"] + sorted(detailed_df["Category"].dropna().unique().tolist())
selected_category = st.selectbox("Choose category", categories)

if selected_category == "All":
    filtered_df = detailed_df.copy()
else:
    filtered_df = detailed_df[detailed_df["Category"] == selected_category].copy()

st.dataframe(
    filtered_df[
        ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)", "Cost Level"]
    ],
    use_container_width=True
)

st.markdown("### ⬇️ Download Report")
excel_data = create_excel_report(results)
st.download_button(
    label="Download Excel Report",
    data=excel_data,
    file_name="boq_analysis_report_v6.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)