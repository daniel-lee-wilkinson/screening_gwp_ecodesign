# Screening Tool for GWP in Eco-Design

This **Streamlit-based application** helps engineers and designers **screen the Global Warming Potential (GWP)** of various materials during early-stage design. The app enables real-time GWP calculations, comparisons across design alternatives, and a clear visualisation of environmental impact based on data from the ICE Database (2024) and IPCC (2021).

---

## Features

- Select materials from a predefined database (ICE & GLO data).
- Add quantities to a "Current Design".
- Calculate total GWP (in kg CO₂e) automatically.
- Create and save **Alternative Designs**.
- visualise GWP differences using bar charts.
- Referenced databases ensure accuracy.

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

```bash
git clone https://github.com/yourusername/gwp-eco-design-tool.git
cd gwp-eco-design-tool
pip install -r requirements.txt
streamlit run app.py
```

---

## Technologies Used

- [Streamlit](https://streamlit.io/) – For building the user interface.
- [Pandas](https://pandas.pydata.org/) – For managing tabular data.
- [Matplotlib](https://matplotlib.org/) – For generating GWP comparison charts.

---

## File Structure

```
gwp-eco-design-tool/
├── app.py              # Main Streamlit application script
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## Example Workflow

1. Select a material (e.g., Concrete 35MPa).
2. Enter a quantity (e.g., 1000 kg).
3. Click "Add to Current Design".
4. View the GWP calculated in real-time.
5. Enter and save alternative scenarios.
6. Compare all design options visually.

---

## Future Roadmap

- Export design data to Excel/CSV.
- Include transportation GWP factors.
- Enable user-imported materials or datasets.
- Enable multi-mode transportation.

---

## Data Sources

- **ICE Advanced Database 2024 Version 4**
- **IPCC 2021 Report**

---

## Author

**Daniel Lee Wilkinson**  
GitHub: [@daniel-lee-wilkinson](https://github.com/daniel-lee-wilkinson)


