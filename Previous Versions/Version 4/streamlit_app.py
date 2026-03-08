from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Infrastructure BOQ Cost Report",
    page_icon="🏗",
    layout="wide",
)

# -----------------------------
# Helpers
# -----------------------------

def rupee(x):
    return f"₹{x:,.2f}"


def validate_boq_data(df):
    required = ["Item", "Category", "Quantity", "Unit Price"]
    return [c for c in required if c not in df.columns]


def analyze_boq(df):

    df = df.copy()
    df["Total Cost"] = df["Quantity"] * df["Unit Price"]

    total_cost = df["Total Cost"].sum()

    df["Cost Share (%)"] = (df["Total Cost"] / total_cost) * 100

    category_summary = (
        df.groupby("Category", as_index=False)["Total Cost"]
        .sum()
        .sort_values("Total Cost", ascending=False)
    )

    category_summary["Category Share (%)"] = (
        category_summary["Total Cost"] / total_cost
    ) * 100

    most_expensive = df.loc[df["Total Cost"].idxmax()]
    top5 = df.sort_values("Total Cost", ascending=False).head(5)

    return df, category_summary, most_expensive, top5, total_cost


def make_excel(results):

    df, category_summary, most_expensive, top5, total = results

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

        df.to_excel(writer, sheet_name="Detailed BOQ", index=False)
        category_summary.to_excel(writer, sheet_name="Category Summary", index=False)
        top5.to_excel(writer, sheet_name="Top Items", index=False)

    buffer.seek(0)
    return buffer


# -----------------------------
# Header
# -----------------------------

st.title("Infrastructure BOQ Cost Report")
st.caption("Engineering Cost Review Dashboard")

uploaded_file = st.file_uploader("Upload BOQ CSV", type=["csv"])

if uploaded_file is None:
    st.info("Upload a BOQ file to generate the report.")
    st.stop()

df = pd.read_csv(uploaded_file)

missing = validate_boq_data(df)

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

results = analyze_boq(df)

df, category_summary, most_expensive, top5, total_cost = results

# -----------------------------
# Project Overview
# -----------------------------

st.subheader("Project Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Project Cost", rupee(total_cost))
c2.metric("BOQ Items", len(df))
c3.metric("Categories", df["Category"].nunique())

# -----------------------------
# Cost Distribution
# -----------------------------

st.subheader("Cost Distribution")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots()

    ax.bar(category_summary["Category"], category_summary["Total Cost"])
    ax.set_title("Cost by Category")
    ax.set_ylabel("Total Cost")

    st.pyplot(fig)

with col2:

    fig2, ax2 = plt.subplots()

    ax2.pie(
        category_summary["Total Cost"],
        labels=category_summary["Category"],
        autopct="%1.1f%%",
    )

    ax2.set_title("Category Share")

    st.pyplot(fig2)

# -----------------------------
# Key Cost Drivers
# -----------------------------

st.subheader("Key Cost Drivers")

st.write("Most Expensive Item")

st.dataframe(
    pd.DataFrame([most_expensive])[
        ["Item", "Category", "Quantity", "Unit Price", "Total Cost"]
    ]
)

st.write("Top 5 Cost Items")

st.dataframe(
    top5[["Item", "Category", "Quantity", "Unit Price", "Total Cost"]],
    use_container_width=True,
)

# -----------------------------
# Cost Risk Insight
# -----------------------------

st.subheader("Cost Insight")

top_category = category_summary.iloc[0]

share = top_category["Category Share (%)"]

if share > 40:
    st.warning(
        f"⚠ Cost concentration risk: {share:.1f}% of project cost comes from **{top_category['Category']}**."
    )
else:
    st.success("Cost distribution appears balanced.")

# -----------------------------
# Filtering
# -----------------------------

st.subheader("BOQ Item Review")

search = st.text_input("Search Item")

category_filter = st.selectbox(
    "Filter Category",
    ["All"] + sorted(df["Category"].unique()),
)

filtered = df.copy()

if search:
    filtered = filtered[filtered["Item"].str.contains(search, case=False)]

if category_filter != "All":
    filtered = filtered[filtered["Category"] == category_filter]

st.dataframe(
    filtered[
        ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)"]
    ],
    use_container_width=True,
)

# -----------------------------
# Export
# -----------------------------

st.subheader("Export Report")

excel_file = make_excel(results)

st.download_button(
    "Download Excel Report",
    data=excel_file,
    file_name="boq_cost_report.xlsx",
)