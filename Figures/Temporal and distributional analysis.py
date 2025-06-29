import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import seaborn as sns

# ====================== Reading data table result statistics ======================
file_path = r'your path\Data\Table\Amery_resultstatistics.xlsx'
df = pd.read_excel(file_path)

# Extract dates and filter data
df['Date'] = df['FileName'].apply(lambda x: datetime.strptime(x.split('_')[0], '%Y%m%d'))
df_filtered = df[df['Date'].dt.month.isin([1, 2, 11, 12])]
df_filtered['Year'] = df_filtered['Date'].dt.strftime('%Y')

# Count data volume per year
yearly_counts = df_filtered.groupby('Year').size()

# Generate x-axis positions
x_positions = []
x_labels = []
xticks_positions = []  # Store positions for xticks

current_position = 1
for year, count in yearly_counts.items():
    for i in range(count):
        x_positions.append(current_position)
        current_position += 1
    x_labels.append(year)
    xticks_positions.append(current_position - count)

# ====================== Part 2: Create canvas ======================
plt.rcParams["font.family"] = "Arial"  # Unified font
fig = plt.figure(figsize=(16, 8), dpi=600)  # 16x8 canvas, 600dpi

# Create custom layout with GridSpec: left plot 3/4 width, right plot 1/4 width
gs = plt.GridSpec(1, 2, width_ratios=[3, 1], wspace=0)  # wspace=0 reduces spacing between plots
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])

# ====================== Left plot: Scatter plot ======================
point_size = 80
along_color = '#1f77b4'  # Blue
cross_color = '#d62728'  # Red

offset = 0.3
x_positions_cross = [pos + offset for pos in x_positions]

# Plot along-track data
ax1.scatter(x_positions, df_filtered['Along_Bias'],
            label='Along-track', color=along_color,
            s=point_size, marker='s', edgecolors='black',
            linewidth=0.8, alpha=0.9)

# Plot cross-track data
ax1.scatter(x_positions_cross, df_filtered['Cross_Bias'],
            label='Cross-track', color=cross_color,
            s=point_size, marker='o', edgecolors='black',
            linewidth=0.8, alpha=0.9)

# Add error bars
for i, pos in enumerate(x_positions):
    ax1.errorbar(pos, df_filtered['Along_Bias'].iloc[i],
                 yerr=df_filtered['Along_Std Dev'].iloc[i],
                 fmt='none', ecolor=along_color, elinewidth=2, capsize=5, capthick=2, alpha=0.7)

    ax1.errorbar(pos + offset, df_filtered['Cross_Bias'].iloc[i],
                 yerr=df_filtered['Cross_Std Dev'].iloc[i],
                 fmt='none', ecolor=cross_color, elinewidth=2, capsize=5, capthick=2, alpha=0.7)

# Configure left plot
ax1.set_xlabel('Year', fontsize=28)
ax1.set_ylabel('Geometric Shift (m)', fontsize=28)
ax1.set_ylim(-250, 250)
ax1.set_yticks(np.arange(-250, 251, 50))
ax1.set_xticks(xticks_positions)
ax1.set_xticklabels(x_labels, rotation=0, fontsize=24)
ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.3, color='gray')
ax1.legend(fontsize=32, loc='upper left')
ax1.tick_params(axis='y', labelsize=24)

# ====================== Right plot: Violin plot (maintain split violin style) ======================
# Extract data
along_bias = df["Along_Bias"].dropna()
cross_bias = df["Cross_Bias"].dropna()

violin_data = pd.DataFrame({
    "Bias Value": np.concatenate([along_bias, cross_bias]),
    "Type": ["Along_Bias"] * len(along_bias) + ["Cross_Bias"] * len(cross_bias)
})

# Plot split violin plot (maintain style with reduced width)
sns.violinplot(
    x=["Bias"] * len(violin_data),  # Use single x-value to overlay violins
    y="Bias Value",
    hue="Type",
    data=violin_data,
    split=True,  # Maintain split style
    inner="quartile",
    palette=[along_color, cross_color],
    ax=ax2,
    width=0.6  # Reduce overall width
)

# Configure right plot
ax2.set_ylim(-250, 250)  # Match y-axis with left plot
ax2.set_yticks(np.arange(-250, 251, 50))
ax2.set_yticklabels([])  # Hide y-axis tick labels (avoid duplication)
ax2.set_xlabel("Distribution", fontsize=28)
ax2.set_ylabel("")
ax2.set_xticklabels([""])  # Hide x-axis label
ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.3, color='gray')

# Manually add legend (split violin auto-generates legend)
handles = [
    plt.Line2D([0], [0], color=along_color, marker='s', markersize=10, linestyle='none', label='Along-track'),
    plt.Line2D([0], [0], color=cross_color, marker='o', markersize=10, linestyle='none', label='Cross-track')
]
ax2.get_legend().remove()

# ====================== Adjust overall layout ======================
plt.tight_layout()
plt.subplots_adjust(wspace=0)

# Save image
# output_path = r'your path\**.png'
# plt.savefig(output_path, dpi=600, bbox_inches='tight')

plt.show()