import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import seaborn as sns

file_path = r'G:\github\Data\Table\Amery_resultstatistics.xlsx'
df = pd.read_excel(file_path)
df['Date'] = df['FileName'].apply(lambda x: datetime.strptime(x.split('_')[0], '%Y%m%d'))
df_filtered = df[df['Date'].dt.month.isin([1, 2, 11, 12])]
df_filtered['Year'] = df_filtered['Date'].dt.strftime('%Y')

# Calculate standard deviations per year
along_abs_std = df_filtered.groupby('Year')['Along_Abs Mean'].std()
cross_abs_std = df_filtered.groupby('Year')['Cross_Abs Mean'].std()

# Count data points per year
yearly_counts = df_filtered.groupby('Year').size()

# Generate x-axis positions
x_positions = []
x_labels = []
xticks_positions = []  # Store xticks positions

current_position = 1
for year, count in yearly_counts.items():
    for i in range(count):
        x_positions.append(current_position)
        current_position += 1
    x_labels.append(year)
    xticks_positions.append(current_position - count)

# Create figure
plt.rcParams["font.family"] = "Arial"
fig = plt.figure(figsize=(16, 8), dpi=600)

# Custom grid layout: left plot 3/4 width, right plot 1/4 width
gs = plt.GridSpec(1, 2, width_ratios=[3, 1], wspace=0)
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])

# Left plot: Scatter plot
point_size = 80
along_color = '#1f77b4'  # Blue
cross_color = '#d62728'  # Red

# Plot scatter points
ax1.scatter(x_positions, df_filtered['Along_Abs Mean'],
            label='Along-track', color=along_color,
            s=point_size, marker='s', edgecolors='black',
            linewidth=0.8, alpha=0.9)

ax1.scatter(x_positions, df_filtered['Cross_Abs Mean'],
            label='Cross-track', color=cross_color,
            s=point_size, marker='o', edgecolors='black',
            linewidth=0.8, alpha=0.9)

# Add error bars
for i, pos in enumerate(x_positions):
    year = df_filtered.iloc[i]['Year']
    along_std = along_abs_std[year]
    cross_std = cross_abs_std[year]

    ax1.errorbar(pos, df_filtered['Along_Abs Mean'].iloc[i],
                 yerr=along_std,
                 fmt='none', ecolor=along_color, elinewidth=2, capsize=5, capthick=2, alpha=0.7)
    ax1.errorbar(pos, df_filtered['Cross_Abs Mean'].iloc[i],
                 yerr=cross_std,
                 fmt='none', ecolor=cross_color, elinewidth=2, capsize=5, capthick=2, alpha=0.7)

# Configure left plot
ax1.set_xlabel('Year', fontsize=28)
ax1.set_ylabel('Absolute Geometric Shift (m)', fontsize=28)
ax1.set_ylim(0, 175)  # Adjusted y-axis upper limit
ax1.set_yticks(np.arange(0, 176, 25))
ax1.set_xticks(xticks_positions)
ax1.set_xticklabels(x_labels, rotation=0, fontsize=24)
ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.3, color='gray')
ax1.legend(fontsize=32, loc='upper left')
ax1.tick_params(axis='y', labelsize=24)

# Add reference lines and labels
ax1.axhline(y=125, color='#FF4500', linestyle='--', linewidth=4, alpha=0.9)  # Orange-red
ax1.text(x=2.5, y=110, s='1/2 IFOV (125 m)', color='#FF4500',
         fontsize=32, ha='left', va='bottom', weight='bold',
         bbox=dict(facecolor='none', alpha=0.8, edgecolor='none'))

ax1.axhline(y=83.3, color='#32CD32', linestyle='--', linewidth=4, alpha=0.9)  # Lime green
ax1.text(x=0.5, y=88, s='1/3 IFOV (83.3 m)', color='#32CD32',
         fontsize=32, ha='left', va='bottom', weight='bold',
         bbox=dict(facecolor='none', alpha=0.8, edgecolor='none'))

# Right plot: Violin plot
along_abs = df["Along_Abs Mean"].dropna()
cross_abs = df["Cross_Abs Mean"].dropna()

violin_data = pd.DataFrame({
    "Bias Value": np.concatenate([along_abs, cross_abs]),
    "Type": ["Along_Abs Mean"] * len(along_abs) + ["Cross_Abs Mean"] * len(cross_abs)
})

# Create split violin plot
sns.violinplot(
    x=["Bias"] * len(violin_data),
    y="Bias Value",
    hue="Type",
    data=violin_data,
    split=True,
    inner="quartile",
    palette=[along_color, cross_color],
    ax=ax2,
    width=0.6
)

# Configure right plot
ax2.set_ylim(0, 175)  # Match left plot's y-axis
ax2.set_yticks(np.arange(0, 176, 25))
ax2.set_yticklabels([])  # Hide y-tick labels
ax2.set_xlabel("Distribution", fontsize=28)
ax2.set_ylabel("")
ax2.set_xticklabels([""])  # Hide x-tick labels
ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.3, color='gray')

# Add reference lines to right plot
ax2.axhline(y=125, color='#FF4500', linestyle='--', linewidth=4, alpha=0.5)
ax2.axhline(y=83.3, color='#32CD32', linestyle='--', linewidth=4, alpha=0.5)

# Create manual legend
handles = [
    plt.Line2D([0], [0], color=along_color, marker='s', markersize=10, linestyle='none', label='Along-track'),
    plt.Line2D([0], [0], color=cross_color, marker='o', markersize=10, linestyle='none', label='Cross-track')
]
ax2.get_legend().remove()

# Final layout adjustments
plt.tight_layout()
plt.subplots_adjust(wspace=0)
plt.show()