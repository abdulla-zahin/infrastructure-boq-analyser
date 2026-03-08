from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Infrastructure BOQ Analyzer", layout="wide")


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
        ],
        "Value": [
            df["Total Cost"].sum(),
            len(df),
            df["Category"].nunique(),
            len(high_cost_items),
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


st.title("🔧 Infrastructure BOQ Analyzer")
st.markdown("Upload a BOQ CSV file and get a clean cost analysis dashboard.")

uploaded_file = st.file_uploader("Upload your BOQ CSV file", type=["csv"])

with st.sidebar:
    st.header("Controls")
    use_budget = st.checkbox("Enable budget comparison")
    budget = None

    if use_budget:
        budget = st.number_input(
            "Enter project budget",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

if uploaded_file is not None:
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

    st.subheader("📌 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Project Cost", f"₹{results['total_project_cost']:,.2f}")
    c2.metric("BOQ Items", f"{len(detailed_df)}")
    c3.metric("Categories", f"{detailed_df['Category'].nunique()}")
    c4.metric("High-Cost Items", f"{len(high_cost_items)}")

    if variance_data:
        st.subheader("📉 Budget Comparison")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Budget", f"₹{variance_data['Budget']:,.2f}")
        b2.metric("Actual Cost", f"₹{variance_data['Actual Cost']:,.2f}")
        b3.metric("Variance", f"₹{variance_data['Variance']:,.2f}")
        b4.metric("Status", variance_data["Budget Status"])

    st.subheader("📊 Category Breakdown")
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

    st.subheader("🚨 Most Expensive Item")
    st.dataframe(
        pd.DataFrame([most_expensive_item])[
            ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)"]
        ],
        use_container_width=True
    )

    st.subheader("🔥 Top 5 Expensive Items")
    st.dataframe(
        top_5_items[
            ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)"]
        ],
        use_container_width=True
    )

    st.subheader("⚠️ High-Cost Items")
    if high_cost_items.empty:
        st.success("No unusually high-cost items detected.")
    else:
        st.dataframe(
            high_cost_items[
                ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)", "Cost Level"]
            ],
            use_container_width=True
        )

    st.subheader("📂 Filter by Category")
    categories = ["All"] + sorted(detailed_df["Category"].dropna().unique().tolist())
    selected_category = st.selectbox("Choose category", categories)

    if selected_category == "All":
        filtered_df = detailed_df
    else:
        filtered_df = detailed_df[detailed_df["Category"] == selected_category]

    st.dataframe(
        filtered_df[
            ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)", "Cost Level"]
        ],
        use_container_width=True
    )

    st.subheader("⬇️ Download Report")
    excel_data = create_excel_report(results)
    st.download_button(
        label="Download Excel Report",
        data=excel_data,
        file_name="boq_analysis_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("Upload a CSV file to begin the analysis.")