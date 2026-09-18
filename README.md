# Milan Housing Market Analysis — H1 2024

> **Portfolio project** — Real estate price analysis using official open data from Comune di Milano.  
> Data Science | Python | Data Visualization | Real Estate Economics

---

## Overview

This project analyzes the Milan residential property market using **official OMI (Osservatorio del Mercato Immobiliare)** data published by the Comune di Milano under a Creative Commons CC BY 4.0 license.

The analysis covers **39 residential zones** (microzone OMI) across all 4 fascia categories: Central (B), Semi-central (C), Peripheral (D), and Suburban (E).

### Key Findings
- Central zones (Fascia B) average **€7,106/m²** — 3× the suburban average of €2,319/m²
- Duomo / Montenapoleone (B12) peaks at **€9,150/m²**
- Pearson r = **−0.55** between sale price and gross yield (higher prices → lower returns)
- Best gross yield: **Ronchetto / Lorenteggio Est (E6) at 4.8%**
- Porta Nuova (C14) commands a significant regeneration premium within semi-central zones

---

## Data Sources

| Dataset | Description | Source | License |
|---------|-------------|--------|---------|
| `DS2832_OMI_compravendita_2024-1.csv` | Sale price quotations H1 2024 | [Comune di Milano Open Data](https://dati.comune.milano.it/dataset/ds2832-quotazioni-immobiliari-omi-compravendita-semestre-2024-1) | CC BY 4.0 |
| `DS2833_OMI_locazione_2024-1.csv` | Rent quotations H1 2024 | [Comune di Milano Open Data](https://dati.comune.milano.it/dataset/ds2833-quotazioni-immobiliari-omi-locazione-semestre-2024-1) | CC BY 4.0 |
| Zone names | OMI zone code → neighborhood mapping | [Agenzia delle Entrate OMI portal](https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.php) | Public |

**OMI (Osservatorio del Mercato Immobiliare)** is the official Italian real estate observatory operated by the Agenzia delle Entrate (Revenue Agency). Data is published semi-annually and represents official property valuations used for taxation and market monitoring.

---

## Methodology

### 1. Data Collection
Downloaded directly from the Comune di Milano Open Data Portal. Both CSV files are semicolon-delimited (`;`) with UTF-8 encoding.

- Sale data: 486 rows, 18 columns (`Compr_min`, `Compr_max` in €/m²)
- Rent data: 487 rows, 18 columns (`Loc_min`, `Loc_max` in €/m²/month)

### 2. Filtering
Filtered for standard residential property:
- `Descr_Tipologia = "Abitazioni civili"` (standard apartments)
- `Stato = "NORMALE"` (normal/average condition)

This yielded **39 zones** with complete sale + rent data.

### 3. Processing
- Converted Italian decimal separator (comma) to dot
- Computed midpoint: `price = (min + max) / 2`
- Joined sale and rent datasets on `Zona` (zone code)
- Mapped zone codes (B12, C14…) to neighborhood names via Agenzia delle Entrate OMI portal

### 4. Analysis
- **Gross annual yield** = (monthly_rent × 12) / sale_price × 100
- **Pearson correlation** between sale price and gross yield
- Aggregation by `Fascia` (zone category: B/C/D/E)

### 5. Visualization
- Python / Matplotlib with Tableau 10 color palette
- 300 DPI PNG exports for all charts
- Charts: ranked bar, grouped comparison, scatter with trend line, price heatmap

---

## OMI Zone Structure

| Fascia | Description | Zones | Avg Sale Price |
|--------|-------------|-------|----------------|
| **B** | Central | 9 zones | €7,106/m² |
| **C** | Semi-central | 8 zones | €5,062/m² |
| **D** | Peripheral | 18 zones | €3,304/m² |
| **E** | Suburban | 4 zones | €2,319/m² |

---

## Project Structure

```
milan-housing-analysis/
├── analysis.py                    # Main analysis script
├── data/
│   ├── DS2832_OMI_compravendita_2024-1.csv   # Sale prices (official, CC BY 4.0)
│   ├── DS2833_OMI_locazione_2024-1.csv       # Rent prices (official, CC BY 4.0)
│   └── milan_housing_districts.csv           # Legacy reference data
├── charts/
│   ├── chart1_top15_zones.png     # Top 15 zones by sale price
│   ├── chart2_sale_vs_rent.png    # Sale vs rent by fascia category
│   ├── chart3_yield_scatter.png   # Price vs gross yield scatter
│   └── chart4_heatmap.png         # All-zone price heatmap
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
# Clone the repo
git clone https://github.com/mhmdgholami/milan-housing-analysis.git
cd milan-housing-analysis

# Install dependencies
pip install -r requirements.txt

# Run analysis (generates all 4 charts)
python analysis.py
```

**Requirements:** `matplotlib`, `numpy` (standard library `csv`, `math`, `statistics` also used)

---

## Author

**mhmd gholami**  


---

## License

- **Code:** MIT License
- **Data:** Creative Commons Attribution 4.0 (CC BY 4.0) — Comune di Milano / Agenzia delle Entrate
