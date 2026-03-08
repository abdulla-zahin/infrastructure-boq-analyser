from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def get_project_paths():
    """Set up project folders and output file paths"""
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "outputs"
    output_dir.mkdir(exist_ok=True)

    return {
        "base_dir": base_dir,
        "output_dir": output_dir,
        "excel_report": output_dir / "boq_analysis_report_v4.xlsx",
        "bar_chart": output_dir / "category_cost_bar_chart_v4.png",
        "pie_chart": output_dir / "category_cost_pie_chart_v4.png",
    }


def list_csv_files(base_dir):
    """List all CSV files in project folder"""
    csv_files = list(base_dir.glob("*.csv"))
    return csv_files


def choose_csv_file(csv_files):
    """Let user choose which CSV file to analyze"""
    if not csv_files:
        print("❌ No CSV files found in the project folder.")
        return None

    print("\n📂 Available BOQ CSV Files:")
    print("-" * 35)
    for i, file in enumerate(csv_files, start=1):
        print(f"{i}. {file.name}")

    while True:
        choice = input("\nEnter the file number to analyze: ").strip()

        if not choice.isdigit():
            print("⚠️ Please enter a valid number.")
            continue

        choice = int(choice)

        if 1 <= choice <= len(csv_files):
            selected_file = csv_files[choice - 1]
            print(f"\n✅ Selected file: {selected_file.name}")
            return selected_file
        else:
            print("⚠️ Invalid file number. Try again.")


def load_boq_file(file_path):
    """Load selected BOQ file"""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ BOQ file loaded successfully from:\n{file_path}\n")
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None


def validate_boq_data(df):
    """Check required BOQ columns"""
    required_columns = ["Item", "Category", "Quantity", "Unit Price"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print("❌ Missing required columns:")
        for col in missing_columns:
            print(f"   - {col}")
        return False

    return True


def clean_numeric_data(df):
    """Convert numeric columns safely"""
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")

    if df["Quantity"].isnull().any() or df["Unit Price"].isnull().any():
        print("❌ Quantity or Unit Price contains invalid values.")
        return None

    return df


def get_budget_input():
    """Ask user whether they want to compare against a budget"""
    choice = input("\nDo you want to enter a project budget? (yes/no): ").strip().lower()

    if choice in ["yes", "y"]:
        while True:
            budget = input("Enter the total project budget: ₹").strip().replace(",", "")
            try:
                budget = float(budget)
                if budget < 0:
                    print("⚠️ Budget cannot be negative.")
                    continue
                return budget
            except ValueError:
                print("⚠️ Please enter a valid numeric budget.")
    return None


def analyze_boq(df, budget=None):
    """Perform BOQ analysis"""
    df["Total Cost"] = df["Quantity"] * df["Unit Price"]
    total_project_cost = df["Total Cost"].sum()

    if total_project_cost == 0:
        print("❌ Total project cost is zero. Please check your BOQ data.")
        return None

    df["Cost Share (%)"] = (df["Total Cost"] / total_project_cost) * 100

    avg_cost = df["Total Cost"].mean()
    df["Cost Level"] = df["Total Cost"].apply(
        lambda x: "High" if x > avg_cost * 1.5 else "Normal"
    )

    category_summary = (
        df.groupby("Category")["Total Cost"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
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
            budget_status = "Under Budget"
        elif variance < 0:
            budget_status = "Over Budget"
        else:
            budget_status = "On Budget"

        variance_data = {
            "Budget": budget,
            "Actual Cost": total_project_cost,
            "Variance": variance,
            "Variance (%)": variance_percent,
            "Budget Status": budget_status,
        }

    return {
        "detailed_df": df,
        "category_summary": category_summary,
        "most_expensive_item": most_expensive_item,
        "high_cost_items": high_cost_items,
        "top_5_items": top_5_items,
        "variance_data": variance_data,
    }


def filter_by_category(df):
    """Optional category filter for user"""
    print("\n📌 Available Categories:")
    categories = sorted(df["Category"].dropna().unique())

    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    choice = input(
        "\nDo you want to view items from a specific category? (yes/no): "
    ).strip().lower()

    if choice not in ["yes", "y"]:
        return None

    while True:
        selected = input("Enter category name exactly as shown above: ").strip()
        filtered_df = df[df["Category"].str.lower() == selected.lower()]

        if filtered_df.empty:
            print("⚠️ No matching category found. Try again.")
        else:
            return filtered_df


def print_analysis(results):
    """Print analysis to terminal"""
    df = results["detailed_df"]
    category_summary = results["category_summary"]
    most_expensive_item = results["most_expensive_item"]
    high_cost_items = results["high_cost_items"]
    top_5_items = results["top_5_items"]
    variance_data = results["variance_data"]

    total_project_cost = df["Total Cost"].sum()

    print("\n🔧 Infrastructure BOQ Analyzer - Version 4")
    print("=" * 60)

    print(f"\n💰 Total Project Cost: ₹{total_project_cost:,.2f}")

    if variance_data:
        print("\n📉 Budget Comparison:")
        print("-" * 40)
        print(f"Budget         : ₹{variance_data['Budget']:,.2f}")
        print(f"Actual Cost    : ₹{variance_data['Actual Cost']:,.2f}")
        print(f"Variance       : ₹{variance_data['Variance']:,.2f}")
        print(f"Variance %     : {variance_data['Variance (%)']:.2f}%")
        print(f"Budget Status  : {variance_data['Budget Status']}")

    print("\n📊 Cost Breakdown by Category:")
    print("-" * 40)
    for _, row in category_summary.iterrows():
        print(
            f"{row['Category']:<15} : ₹{row['Total Cost']:>12,.2f} "
            f"({row['Category Share (%)']:.2f}%)"
        )

    print("\n🚨 Most Expensive Item:")
    print("-" * 40)
    print(f"Item         : {most_expensive_item['Item']}")
    print(f"Category     : {most_expensive_item['Category']}")
    print(f"Quantity     : {most_expensive_item['Quantity']}")
    print(f"Unit Price   : ₹{most_expensive_item['Unit Price']:,.2f}")
    print(f"Total Cost   : ₹{most_expensive_item['Total Cost']:,.2f}")
    print(f"Cost Share   : {most_expensive_item['Cost Share (%)']:.2f}%")

    print("\n🔥 Top 5 Expensive Items:")
    print("-" * 40)
    for _, row in top_5_items.iterrows():
        print(
            f"{row['Item']} | {row['Category']} | "
            f"₹{row['Total Cost']:,.2f} | {row['Cost Share (%)']:.2f}%"
        )

    print("\n⚠️ High-Cost Items:")
    print("-" * 40)
    if high_cost_items.empty:
        print("No unusually high-cost items detected.")
    else:
        for _, row in high_cost_items.iterrows():
            print(
                f"{row['Item']} | ₹{row['Total Cost']:,.2f} "
                f"| {row['Cost Share (%)']:.2f}%"
            )

    print("\n🧠 Quick Insight:")
    print("-" * 40)
    labor_cost = (
        category_summary.loc[category_summary["Category"] == "Labor", "Total Cost"].sum()
    )
    material_cost = (
        category_summary.loc[category_summary["Category"] == "Material", "Total Cost"].sum()
    )

    if labor_cost > material_cost * 2:
        print("⚠️ Labor cost is significantly higher than material cost.")
    elif material_cost > labor_cost * 2:
        print("⚠️ Material cost is significantly higher than labor cost.")
    else:
        print("✅ Cost distribution looks balanced.")


def save_charts(category_summary, bar_chart_path, pie_chart_path):
    """Save charts as images"""
    category_data = category_summary.set_index("Category")["Total Cost"]

    plt.figure(figsize=(8, 5))
    category_data.plot(kind="bar")
    plt.title("BOQ Cost by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Cost")
    plt.tight_layout()
    plt.savefig(bar_chart_path)
    plt.close()

    plt.figure(figsize=(7, 7))
    category_data.plot(kind="pie", autopct="%1.1f%%")
    plt.title("BOQ Cost Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(pie_chart_path)
    plt.close()

    print(f"\n📁 Bar chart saved to: {bar_chart_path}")
    print(f"📁 Pie chart saved to: {pie_chart_path}")


def export_to_excel(results, excel_path):
    """Export results into a multi-sheet Excel file"""
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

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Detailed Analysis", index=False)
        category_summary.to_excel(writer, sheet_name="Category Summary", index=False)
        high_cost_items.to_excel(writer, sheet_name="High Cost Items", index=False)
        top_5_items.to_excel(writer, sheet_name="Top 5 Items", index=False)
        summary_data.to_excel(writer, sheet_name="Project Summary", index=False)
        budget_sheet.to_excel(writer, sheet_name="Budget Variance", index=False)

    print(f"📁 Excel report exported to: {excel_path}")


def print_filtered_category(filtered_df):
    """Print filtered category items"""
    if filtered_df is None:
        return

    print("\n📌 Filtered Category View")
    print("=" * 40)
    print(
        filtered_df[
            ["Item", "Category", "Quantity", "Unit Price", "Total Cost", "Cost Share (%)"]
        ].to_string(index=False)
    )


def main():
    paths = get_project_paths()

    csv_files = list_csv_files(paths["base_dir"])
    selected_file = choose_csv_file(csv_files)

    if selected_file is None:
        return

    df = load_boq_file(selected_file)
    if df is None:
        return

    if not validate_boq_data(df):
        return

    df = clean_numeric_data(df)
    if df is None:
        return

    budget = get_budget_input()
    results = analyze_boq(df, budget)

    if results is None:
        return

    print_analysis(results)

    filtered_df = filter_by_category(results["detailed_df"])
    print_filtered_category(filtered_df)

    save_charts(
        results["category_summary"],
        paths["bar_chart"],
        paths["pie_chart"],
    )

    export_to_excel(results, paths["excel_report"])

    print("\n✅ Version 4 analysis complete.")
    print("📦 All outputs saved inside the 'outputs' folder.")


if __name__ == "__main__":
    main()