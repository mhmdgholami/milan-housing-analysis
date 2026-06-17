"""
Milan Housing Market Analysis — 2024 H1
Data source: OMI (Osservatorio del Mercato Immobiliare) — Comune di Milano Open Data
License: Creative Commons Attribution 4.0 (CC BY 4.0)
Source URLs:
  Sale: https://dati.comune.milano.it/dataset/ds2832-quotazioni-immobiliari-omi-compravendita-semestre-2024-1
  Rent: https://dati.comune.milano.it/dataset/ds2833-quotazioni-immobiliari-omi-locazione-semestre-2024-1
"""

import csv
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.gridspec import GridSpec

# ─────────────────────────────────────────────────────────────────────────────
# 1. ZONE → NEIGHBORHOOD NAME MAPPING
#    Source: Agenzia delle Entrate OMI portal + CasaLens.it
# ─────────────────────────────────────────────────────────────────────────────
ZONE_NAMES = {
    # Fascia B — Centrale
    'B12': 'Duomo / Montenapoleone',
    'B13': 'Università Statale / S. Lorenzo',
    'B15': 'Brera / Centro Storico',
    'B16': 'Sant\'Ambrogio / Cadorna',
    'B17': 'Parco Sempione / Corso Magenta',
    'B18': 'Turati / Moscova',
    'B19': 'Venezia / Porta Vittoria',
    'B20': 'Porta Vigentina / Porta Romana',
    'B21': 'Porta Ticinese / Porta Genova',
    # Fascia C — Semicentrale
    'C12': 'Pisani / Buenos Aires',
    'C13': 'City Life',
    'C14': 'Porta Nuova',
    'C15': 'Stazione Centrale / Viale Stelvio',
    'C16': 'Cenisio / Farini / Sarpi',
    'C17': 'Sempione / Pagano / Washington',
    'C18': 'Solari / Porta Genova S.',
    'C19': 'Tabacchi / Sarfatti / Crema',
    'C20': 'Libia / XXII Marzo',
    # Fascia D — Periferica
    'D10': 'Parco Lambro / Feltre / Udine',
    'D12': 'Piola / Argonne / Corsica',
    'D13': 'Lambrate / Rubattino',
    'D15': 'Corvetto / Chiaravalle',
    'D16': 'Tito Livio / Ortomercato',
    'D18': 'Vigentino / Chiesa Rossa',
    'D20': 'Ortles / Spadolini',
    'D21': 'Barona / Famagosta',
    'D24': 'Segesta / Vespri Siciliani',
    'D25': 'Baggio / Sella Nuova',
    'D28': 'Ippodromo / Monte Stella',
    'D30': 'QT8 / Gallaratese',
    'D31': 'Bovisa / Bausan / Imbonati',
    'D32': 'Quarto Oggiaro / Vialba',
    'D33': 'Niguarda / Bignami',
    'D34': 'Sarca / Bicocca',
    'D35': 'Monza / Crescenzago / Gorla',
    'D36': 'Maggiolina / Parco Trotter',
    # Fascia E — Suburbana
    'E5':  'Chiaravalle / Gratosoglio S.',
    'E6':  'Ronchetto / Lorenteggio Est',
    'E7':  'Quinto Romano / Muggiano',
    'E8':  'Bruzzano / Affori',
}

FASCIA_LABEL = {
    'B': 'Central',
    'C': 'Semi-central',
    'D': 'Peripheral',
    'E': 'Suburban',
}

FASCIA_ORDER = ['B', 'C', 'D', 'E']

# ─────────────────────────────────────────────────────────────────────────────
# 2. LOAD & PROCESS OMI DATA
# ─────────────────────────────────────────────────────────────────────────────

def load_omi(filepath, min_col, max_col):
    """Load OMI CSV and return {zone: midpoint} for 'Abitazioni civili' NORMALE."""
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            zona = row['Zona'].strip()
            tipologia = row['Descr_Tipologia'].strip()
            stato = row['Stato'].strip()
            # Focus on standard residential (Abitazioni civili, NORMALE condition)
            if tipologia != 'Abitazioni civili' or stato != 'NORMALE':
                continue
            try:
                vmin = float(row[min_col].replace(',', '.'))
                vmax = float(row[max_col].replace(',', '.'))
                midpoint = (vmin + vmax) / 2
                data[zona] = midpoint
            except (ValueError, KeyError):
                continue
    return data

sale_data = load_omi('/home/user/workspace/omi_raw.csv', 'Compr_min', 'Compr_max')
rent_data = load_omi('/home/user/workspace/omi_rent_raw.csv', 'Loc_min', 'Loc_max')

# Build unified dataset — only zones present in both datasets
zones_common = sorted(set(sale_data.keys()) & set(rent_data.keys()))

records = []
for z in zones_common:
    fascia = z[0]
    name = ZONE_NAMES.get(z, z)
    sale_mid = sale_data[z]
    rent_mid = rent_data[z]  # €/m²/month
    # Gross annual yield = (rent * 12) / sale_price * 100
    gross_yield = (rent_mid * 12) / sale_mid * 100
    records.append({
        'zone': z,
        'name': name,
        'fascia': fascia,
        'fascia_label': FASCIA_LABEL.get(fascia, fascia),
        'sale': sale_mid,
        'rent': rent_mid,
        'yield': gross_yield,
    })

# Sort by sale price descending
records.sort(key=lambda r: r['sale'], reverse=True)

print(f"Zones in analysis: {len(records)}")
for r in records[:10]:
    print(f"  {r['zone']:4s} {r['name'][:35]:35s} sale={r['sale']:,} rent={r['rent']:.1f} yield={r['yield']:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# 3. TABLEAU COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
T_BLUE   = '#4E79A7'
T_ORANGE = '#F28E2B'
T_TEAL   = '#76B7B2'
T_RED    = '#E15759'
T_GREEN  = '#59A14F'
T_PURPLE = '#B07AA1'
T_DARK   = '#2D2D2D'
T_MID    = '#4A4A4A'
T_LIGHT  = '#F5F5F5'
T_GRID   = '#E8E8E8'
T_DARKBG = '#1B2533'

FASCIA_COLORS = {
    'B': T_ORANGE,
    'C': T_BLUE,
    'D': T_TEAL,
    'E': T_GREEN,
}

def style_ax(ax, title='', xlabel='', ylabel='', dark=False):
    bg = T_DARKBG if dark else 'white'
    tc = 'white' if dark else T_DARK
    gc = '#3A4A5C' if dark else T_GRID
    ax.set_facecolor(bg)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(gc)
    ax.spines['bottom'].set_color(gc)
    ax.tick_params(colors=tc, labelsize=9)
    ax.xaxis.label.set_color(tc)
    ax.yaxis.label.set_color(tc)
    ax.set_title(title, color=tc, fontsize=11, fontweight='bold', pad=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.yaxis.grid(True, color=gc, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)

# ─────────────────────────────────────────────────────────────────────────────
# 4. CHART 1 — Top 15 Districts by Sale Price (Horizontal Bar)
# ─────────────────────────────────────────────────────────────────────────────
top15 = records[:15]
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('white')
style_ax(ax, title='Top 15 Zones by Sale Price — OMI Milano H1 2024\n(Abitazioni Civili, Stato NORMALE)',
         xlabel='Sale Price Midpoint (€/m²)')

names_short = [f"{r['zone']} — {r['name'][:30]}" for r in reversed(top15)]
vals = [r['sale'] for r in reversed(top15)]
colors_bar = [FASCIA_COLORS[r['fascia']] for r in reversed(top15)]

bars = ax.barh(names_short, vals, color=colors_bar, height=0.65, edgecolor='none')

# Value labels
for bar, val in zip(bars, vals):
    ax.text(val + 80, bar.get_y() + bar.get_height()/2,
            f'€{val:,.0f}', va='center', fontsize=8.5, color=T_DARK, fontweight='bold')

ax.set_xlim(0, max(vals) * 1.17)
ax.tick_params(axis='y', labelsize=8.5)

# Legend
legend_patches = [mpatches.Patch(color=FASCIA_COLORS[f], label=f'Fascia {f} — {FASCIA_LABEL[f]}')
                  for f in FASCIA_ORDER if f in FASCIA_COLORS]
ax.legend(handles=legend_patches, loc='lower right', fontsize=8.5,
          framealpha=0.9, edgecolor=T_GRID)

# Source annotation
fig.text(0.12, 0.01, 'Source: OMI — Comune di Milano Open Data (CC BY 4.0) | dati.comune.milano.it | H1 2024',
         fontsize=7.5, color='#888888')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('/home/user/workspace/tbl_chart1.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Chart 1 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. CHART 2 — Sale vs Rent by Zone Category (Grouped Bar)
# ─────────────────────────────────────────────────────────────────────────────
# Aggregate by fascia
fascia_stats = {}
for f in FASCIA_ORDER:
    subset = [r for r in records if r['fascia'] == f]
    if subset:
        fascia_stats[f] = {
            'label': FASCIA_LABEL[f],
            'sale_avg': sum(r['sale'] for r in subset) / len(subset),
            'rent_avg': sum(r['rent'] for r in subset) / len(subset),
            'n': len(subset),
        }

labels = [fascia_stats[f]['label'] for f in FASCIA_ORDER if f in fascia_stats]
sale_avgs = [fascia_stats[f]['sale_avg'] for f in FASCIA_ORDER if f in fascia_stats]
rent_avgs = [fascia_stats[f]['rent_avg'] for f in FASCIA_ORDER if f in fascia_stats]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
fig.patch.set_facecolor('white')
fig.suptitle('Sale Price vs Monthly Rent by Zone Category — OMI Milano H1 2024',
             fontsize=13, fontweight='bold', color=T_DARK, y=1.01)

# Left: Sale prices
style_ax(ax1, title='Average Sale Price (€/m²)', ylabel='€/m²')
x = np.arange(len(labels))
sale_colors = [FASCIA_COLORS[f] for f in FASCIA_ORDER if f in fascia_stats]
bars1 = ax1.bar(x, sale_avgs, color=sale_colors, width=0.55, edgecolor='none')
for bar, val in zip(bars1, sale_avgs):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 60,
             f'€{val:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color=T_DARK)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=9.5)
ax1.set_ylim(0, max(sale_avgs) * 1.18)

# Right: Rent prices
style_ax(ax2, title='Average Monthly Rent (€/m²/month)', ylabel='€/m²/month')
bars2 = ax2.bar(x, rent_avgs, color=sale_colors, width=0.55, edgecolor='none')
for bar, val in zip(bars2, rent_avgs):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
             f'€{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color=T_DARK)
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontsize=9.5)
ax2.set_ylim(0, max(rent_avgs) * 1.22)

# Zone count annotations
for i, f in enumerate([ff for ff in FASCIA_ORDER if ff in fascia_stats]):
    n = fascia_stats[f]['n']
    ax1.text(i, -max(sale_avgs)*0.06, f'n={n}', ha='center', fontsize=8, color='#888888')
    ax2.text(i, -max(rent_avgs)*0.08, f'n={n}', ha='center', fontsize=8, color='#888888')

fig.text(0.12, -0.04, 'Source: OMI — Comune di Milano Open Data (CC BY 4.0) | dati.comune.milano.it | H1 2024',
         fontsize=7.5, color='#888888')

plt.tight_layout()
plt.savefig('/home/user/workspace/tbl_chart2.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Chart 2 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 6. CHART 3 — Sale Price vs Gross Yield Scatter (distance-from-center proxy)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor('white')
style_ax(ax, title='Sale Price vs Gross Rental Yield by Zone — OMI Milano H1 2024',
         xlabel='Sale Price Midpoint (€/m²)', ylabel='Gross Annual Yield (%)')

for r in records:
    color = FASCIA_COLORS[r['fascia']]
    ax.scatter(r['sale'], r['yield'], color=color, s=90, alpha=0.85,
               edgecolors='white', linewidths=0.5, zorder=3)
    # Label top zones by fascia
    if r['zone'] in ['B12', 'B15', 'C14', 'C13', 'D12', 'D36', 'E5']:
        short_name = r['name'].split('/')[0].strip()
        ax.annotate(f"{r['zone']}\n{short_name}", (r['sale'], r['yield']),
                   textcoords='offset points', xytext=(6, 4),
                   fontsize=7.5, color=T_DARK,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))

# Trend line
xs = np.array([r['sale'] for r in records])
ys = np.array([r['yield'] for r in records])
z_fit = np.polyfit(xs, ys, 1)
p_fit = np.poly1d(z_fit)
xs_line = np.linspace(xs.min(), xs.max(), 100)
ax.plot(xs_line, p_fit(xs_line), color=T_RED, linewidth=1.5, linestyle='--', alpha=0.7, label='Trend')

# Pearson correlation
from statistics import mean, stdev
def pearson(x, y):
    n = len(x)
    mx, my = mean(x), mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = math.sqrt(sum((xi - mx)**2 for xi in x) * sum((yi - my)**2 for yi in y))
    return num / den if den != 0 else 0

r_val = pearson(xs.tolist(), ys.tolist())
ax.text(0.97, 0.97, f'Pearson r = {r_val:.2f}', transform=ax.transAxes,
        ha='right', va='top', fontsize=9.5, color=T_DARK,
        bbox=dict(boxstyle='round', facecolor='#FFF9E6', edgecolor=T_ORANGE, alpha=0.9))

# Legend
legend_patches = [mpatches.Patch(color=FASCIA_COLORS[f], label=f'Fascia {f} — {FASCIA_LABEL[f]}')
                  for f in FASCIA_ORDER if f in FASCIA_COLORS]
ax.legend(handles=legend_patches + [
    plt.Line2D([0], [0], color=T_RED, linestyle='--', linewidth=1.5, label='Trend line')
], fontsize=8.5, framealpha=0.9, edgecolor=T_GRID)

fig.text(0.12, 0.01, 'Source: OMI — Comune di Milano Open Data (CC BY 4.0) | dati.comune.milano.it | H1 2024',
         fontsize=7.5, color='#888888')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('/home/user/workspace/tbl_chart3.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print(f"Chart 3 saved. Pearson r (sale vs yield) = {r_val:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. CHART 4 — Treemap-style heatmap by zone
# ─────────────────────────────────────────────────────────────────────────────
# Use a grid layout showing all zones colored by sale price
all_recs = sorted(records, key=lambda r: (FASCIA_ORDER.index(r['fascia']), -r['sale']))

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor(T_DARK)
ax.set_facecolor(T_DARK)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
ax.set_title('Milan Housing Zones — Sale Price Heatmap (€/m²)\nOMI H1 2024 | Abitazioni Civili, Stato NORMALE',
             color='white', fontsize=13, fontweight='bold', pad=14)

# Group by fascia
fascia_groups = {}
for r in all_recs:
    fascia_groups.setdefault(r['fascia'], []).append(r)

# Layout: 4 rows (fascias), columns within each
col_width = 0.115
row_heights = {'B': 0.20, 'C': 0.20, 'D': 0.22, 'E': 0.12}
row_tops = {'B': 0.92, 'C': 0.68, 'D': 0.44, 'E': 0.19}

# Color normalization across all zones
all_sale_vals = [r['sale'] for r in records]
vmin, vmax = min(all_sale_vals), max(all_sale_vals)
cmap = plt.cm.YlOrRd

for fascia in FASCIA_ORDER:
    if fascia not in fascia_groups:
        continue
    grp = fascia_groups[fascia]
    top = row_tops[fascia]
    h = row_heights[fascia]
    n = len(grp)

    # Fascia label on left
    ax.text(0.01, top - h/2, f'Fascia {fascia}\n({FASCIA_LABEL[fascia]})',
            color='white', fontsize=9, fontweight='bold', va='center', ha='left')

    cols_start = 0.10
    for i, r in enumerate(grp):
        norm_val = (r['sale'] - vmin) / (vmax - vmin)
        color = cmap(norm_val)
        # Slightly lighter for high contrast
        text_color = 'black' if norm_val > 0.5 else 'white'

        rect_x = cols_start + i * (col_width + 0.005)
        rect_y = top - h

        rect = plt.Rectangle((rect_x, rect_y), col_width * 0.95, h * 0.88,
                              facecolor=color, edgecolor='#333333', linewidth=0.5)
        ax.add_patch(rect)

        # Zone code
        ax.text(rect_x + col_width*0.475, rect_y + h*0.65,
                r['zone'], ha='center', va='center',
                fontsize=9, fontweight='bold', color=text_color)

        # Short name (2 words max)
        short = r['name'].split('/')[0].strip()[:14]
        ax.text(rect_x + col_width*0.475, rect_y + h*0.42,
                short, ha='center', va='center',
                fontsize=6.5, color=text_color, wrap=True)

        # Price
        ax.text(rect_x + col_width*0.475, rect_y + h*0.20,
                f"€{r['sale']:,.0f}", ha='center', va='center',
                fontsize=7.5, fontweight='bold', color=text_color)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm.set_array([])
cbar_ax = fig.add_axes([0.12, 0.04, 0.76, 0.025])
cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
cbar.set_label('Sale Price Midpoint (€/m²)', color='white', fontsize=9)
cbar.ax.xaxis.set_tick_params(color='white')
plt.setp(cbar.ax.xaxis.get_ticklabels(), color='white', fontsize=8)

fig.text(0.5, 0.0, 'Source: OMI — Comune di Milano Open Data (CC BY 4.0) | dati.comune.milano.it | H1 2024',
         fontsize=7.5, color='#AAAAAA', ha='center')

plt.savefig('/home/user/workspace/tbl_chart4.png', dpi=300, bbox_inches='tight',
            facecolor=T_DARK, edgecolor='none')
plt.close()
print("Chart 4 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 8. PRINT SUMMARY STATS
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== SUMMARY STATISTICS ===")
print(f"Total zones analyzed: {len(records)}")
for f in FASCIA_ORDER:
    subset = [r for r in records if r['fascia'] == f]
    if subset:
        avg_sale = sum(r['sale'] for r in subset) / len(subset)
        avg_rent = sum(r['rent'] for r in subset) / len(subset)
        avg_yield = sum(r['yield'] for r in subset) / len(subset)
        print(f"Fascia {f} ({FASCIA_LABEL[f]}): n={len(subset)}, avg sale=€{avg_sale:,.0f}/m², avg rent=€{avg_rent:.1f}/m²/mo, avg yield={avg_yield:.1f}%")

print(f"\nMost expensive: {records[0]['zone']} — {records[0]['name']} @ €{records[0]['sale']:,}/m²")
print(f"Most affordable: {records[-1]['zone']} — {records[-1]['name']} @ €{records[-1]['sale']:,}/m²")

best_yield_rec = max(records, key=lambda r: r['yield'])
print(f"Best gross yield: {best_yield_rec['zone']} — {best_yield_rec['name']} @ {best_yield_rec['yield']:.1f}%")
print(f"Pearson r (sale vs yield): {r_val:.2f}")
print("\nAll charts saved successfully.")
