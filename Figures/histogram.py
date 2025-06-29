import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

folders = {
    'Amery': 'your path\Data\Table\Amery_resultstatistics.xlsx',
    'AP': 'your path\Data\Table\AntarcticPeninsula_resultstatistic.xlsx',
    'hengguan': 'your path\Data\Table\RossIsland_resultstatistics.xlsx',
    'maud': 'your path\Data\Table\QueenMaudLand_resultstatistics.xlsx'
}

data = {'Along_bias': [], 'Cross_Bias': [], 'Region': []}

for region, file_path in folders.items():
    df = pd.read_excel(file_path)

    if 'Along_Bias' in df.columns and 'Cross_Bias' in df.columns:
        data['Along_bias'].extend(df['Along_Bias'].dropna())
        data['Cross_Bias'].extend(df['Cross_Bias'].dropna())
        data['Region'].extend([region] * len(df))

df_combined = pd.DataFrame(data)

for region in folders.keys():
    plt.figure(figsize=(12, 10))

    df_region = df_combined[df_combined['Region'] == region]


    sns.histplot(df_region['Along_bias'], kde=True, color='blue', label='Along-track', stat='density', linewidth=2, line_kws={'linewidth': 5})


    sns.histplot(df_region['Cross_Bias'], kde=True, color='green', label='Cross-track', stat='density', linewidth=2, line_kws={'linewidth': 5})


    plt.xlabel('Geometric Shift (m)', fontsize=36, fontname='Arial')
    plt.ylabel('Probability Density', fontsize=36, fontname='Arial')


    plt.legend(fontsize=32, loc='upper left', frameon=False, prop={'family': 'Arial', 'size': 32})


    plt.xticks(fontsize=32, fontname='Arial')
    plt.yticks(fontsize=32, fontname='Arial')
    plt.tight_layout()


    plt.savefig(f'{region}_Geometric_Shift_Distribution第二版.png', dpi=300)
    plt.close()


plt.figure(figsize=(12, 10))


sns.histplot(df_combined['Along_bias'], kde=True, color='blue', label='Along-track', stat='density', linewidth=2, line_kws={'linewidth': 5})


sns.histplot(df_combined['Cross_Bias'], kde=True, color='green', label='Cross-track', stat='density', linewidth=2, line_kws={'linewidth': 5})


plt.xlabel('Geometric Shift (m)', fontsize=36, fontname='Arial')
plt.ylabel('Probability Density', fontsize=36, fontname='Arial')

plt.legend(fontsize=32, loc='upper left', frameon=False, prop={'family': 'Arial', 'size': 32})

plt.xticks(fontsize=32, fontname='Arial')
plt.yticks(fontsize=32, fontname='Arial')
plt.tight_layout()
plt.show()
