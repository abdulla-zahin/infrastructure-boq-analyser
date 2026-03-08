
# 🏗 Infrastructure BOQ Analyzer

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Data Analysis](https://img.shields.io/badge/Focus-Data%20Analysis-green)
![Construction](https://img.shields.io/badge/Domain-Construction-orange)

*Turning BOQ spreadsheets into engineering insights.*

Because no engineer should have to scroll through **500 rows of a spreadsheet** just to find the most expensive pipe.

The **Infrastructure BOQ Analyzer** is a Python-based analytical tool designed to process **Bill of Quantities (BOQ)** datasets used in construction and infrastructure projects.

Instead of manually analyzing spreadsheets, the analyzer automatically evaluates the dataset and highlights:

- Total project cost
- Category-wise cost distribution
- Key cost drivers
- Cost concentration risks
- Visual insights through charts and dashboards

---

# 📌 Project Overview

In construction projects, **Bill of Quantities (BOQ)** documents are used to describe:

- materials
- labor
- quantities
- unit costs
- total costs

These documents are critical for **project estimation and budgeting**, but large BOQ spreadsheets can be difficult to interpret.

The **BOQ Analyzer** automates this process by converting raw BOQ data into **clear analytical insights and visual dashboards**, helping engineers and planners quickly understand where the project budget is going.

---

# ⚙️ Features

The analyzer automatically performs the following tasks:

✔ Validate BOQ dataset structure  
✔ Calculate **total project cost**  
✔ Analyze **cost distribution by category**  
✔ Identify **top cost drivers**  
✔ Detect **cost concentration alerts**  
✔ Generate **visual charts and dashboards**  
✔ Allow **searchable BOQ item review**  
✔ Export analysis as an **Excel report**

---

# 🧠 System Workflow

```
BOQ CSV Dataset
      ↓
Data Processing (Python + Pandas)
      ↓
Cost Analysis Engine
      ↓
Visualization Dashboard
      ↓
Cost Alerts & Key Drivers
      ↓
Exportable Excel Report
```

---

# 🖥 System Interface

Users upload a BOQ CSV dataset and provide project information.

The system then processes the dataset and generates analytical insights automatically.

![System Interface](images/system_interface.png)

---

# 📊 Cost Distribution Analysis

The analyzer generates visual summaries showing how project costs are distributed across categories such as **materials and labor**.

![Cost Distribution](images/cost_distribution.png)

---

# 🚨 Key Cost Drivers

The system highlights the **most expensive BOQ items** and identifies the **top cost contributors**.

![Key Cost Drivers](images/key_cost_drivers.png)

---

# 🔍 BOQ Item Review

Users can inspect individual BOQ items through a searchable interface and export the results as an **Excel report**.

![BOQ Review](images/boq_review.png)

---

# 📄 Example BOQ Dataset

The analyzer processes structured BOQ datasets containing:

- Item Description
- Category
- Quantity
- Unit Price
- Total Cost

![BOQ Dataset](images/boq_dataset.png)

---

# 🧪 Project Evolution

This project evolved through several development stages.

| Version | Description |
|------|-------------|
| **v1 – Basic Script** | Initial Python script for BOQ cost calculations |
| **v2 – Chart Analysis** | Added visualization of cost distribution |
| **v3 – Generated Web Version** | First web-based interface prototype |
| **v4 – Final Version** | Fully structured Streamlit application with dashboards, alerts, and reporting |

Earlier development versions are preserved inside the **versions/** folder.

---

# 📂 Repository Structure

```
Infrastructure-BOQ-Analyzer
│
├── streamlit_app.py
├── requirements.txt
├── README.md
│
├── data
│   └── sample_boq.csv
│
├── images
│
├── versions
│   ├── v1_basic_script
│   ├── v2_chart_analysis
│   ├── v3_web_generator
│   └── v4_final_reference
│
└── docs
    └── technical_report.md
```

---

# 🛠 Technologies Used

- **Python**
- **Pandas**
- **Matplotlib**
- **Streamlit**
- **AI-assisted development tools**

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/infrastructure-boq-analyzer.git
```

Navigate to the project directory:

```bash
cd infrastructure-boq-analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

Run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

Then open the browser and upload a BOQ CSV dataset.

---

# 🔮 Future Improvements

Planned enhancements include:

- Budget allocation analysis
- Contractor profit and overhead estimation
- Multi-project cost comparison
- Advanced dashboards
- Machine learning based cost prediction

---

# 👷 Author

**Abdulla Zahin**

Independent Technical Project  
Engineering + Data Analysis

---

# 🤖 Development Note

Parts of the development workflow were supported using **AI-assisted coding tools** for development assistance, debugging, and documentation.
