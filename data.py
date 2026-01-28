import kagglehub
import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import os

# Create plots directory if it doesn't exist
if not os.path.exists('plots'):
    os.makedirs('plots')
# Download latest version
path =  r"C:\Users\othma\.cache\kagglehub\datasets\martinkanju\dirty-dataset-to-practice-data-cleaning\versions\1\data.csv"
data = pd.read_csv(path)
y = data['Actual gross']

#cleaning the data
#starting by the column peak
def clean_peak(val):
    return re.sub(r'\[.*?\]', '', str(val))
data['Peak'] = data['Peak'].apply(clean_peak)
data['All Time Peak'] = data['All Time Peak'].apply(clean_peak)

#cleaning the gross columns
def clean_gross(val):
    return re.sub(r'[^\d.]','',str(val))
data['Actual gross'] = data['Actual gross'].apply(clean_gross)
data['Actual gross(in 2022 dollars)'] = data['Actual gross(in 2022 dollars)'].apply(clean_gross)
data['Average gross'] = data['Average gross'].apply(clean_gross)

def clean_shows(val):
    # Retrieve only digits
    val = re.sub(r'[^\d]', '', str(val))
    return int(val) if val else None

data['Shows'] = data['Shows'].apply(clean_shows)

def extract_years(val):
    # Capture patterns like "2018-2019", "2018", etc.
    matches = re.findall(r'(\d{4})', str(val))
    if not matches:
        return None, None
    start = int(matches[0])
    end = int(matches[-1]) if len(matches) > 1 else start
    return start, end

# Create new temporal features
year_data = data['Year(s)'].apply(lambda x: pd.Series(extract_years(x)))
data['Start Year'] = year_data[0]
data['End Year'] = year_data[1]
data['Tour Duration'] = data['End Year'] - data['Start Year']
# Keep the original simplified 'Year(s)' column for compatibility if needed, or just use Start Year
data['Year(s)'] = data['Start Year']


def clean_text(val):
    # Enlever les citations [1]
    val = re.sub(r'\[.*?\]', '', str(val))
    # Enlever les symboles bizarres †, ‡, *
    val = re.sub(r'[†‡*]', '', val)
    return val.strip()

# Ça reste des Strings (objets), c'est parfait !
data['Tour title'] = data['Tour title'].apply(clean_text)
data['Artist'] = data['Artist'].apply(clean_text)

#gerer les valeurs manquantes
# On remplace les vides par NaN pour tout harmoniser
import numpy as np
data = data.replace(r'^\s*$', np.nan, regex=True)
data = data.replace('nan', np.nan)

# Imputation par la Médiane (Groupé par Artiste d'abord, puis Global)
# C'est logique : si on ne connait pas le rang, on prend le rang "moyen" (médian) de cet artiste
cols_a_remplir = ['Peak', 'All Time Peak']

for col in cols_a_remplir:
    # IMPORTANT: Convertir en nombre (float) pour pouvoir calculer la médiane
    data[col] = pd.to_numeric(data[col], errors='coerce')
    
    # 1. Essayer de remplir avec la médiane de l'artiste
    data[col] = data.groupby('Artist')[col].transform(lambda x: x.fillna(x.median()))
    # 2. Si l'artiste n'a aucune donnée, remplir avec la médiane de tout le monde
    data[col] = data[col].fillna(data[col].median())

# --- FEATURE ENGINEERING ---

# 1. Derived Metrics
# Ensure numerical columns are floats
cols_to_float = ['Actual gross', 'Actual gross(in 2022 dollars)', 'Average gross', 'Shows']
for col in cols_to_float:
    data[col] = pd.to_numeric(data[col], errors='coerce')

data['Gross per Show'] = data['Actual gross'] / data['Shows']
data['Inflation Factor'] = data['Actual gross(in 2022 dollars)'] / data['Actual gross']

# 2. Artist Aggregates
# Calculate career stats per artist
artist_stats = data.groupby('Artist').agg({
    'Shows': 'sum',
    'Actual gross': 'sum',
    'Tour title': 'count'
}).rename(columns={
    'Shows': 'Artist Total Shows',
    'Actual gross': 'Artist Career Gross',
    'Tour title': 'Artist Tour Count'
})

# Merge back into main dataframe
data = data.merge(artist_stats, on='Artist', how='left')

print("\nAprès imputation (Valeurs manquantes restantes) :")
print(data.isna().sum())
print(data['Actual gross'])
#summary statistics
# Convertir en nombre pour avoir les stats
cols_numeriques = ['Actual gross', 'Actual gross(in 2022 dollars)', 'Average gross']
for col in cols_numeriques:
    data[col] = pd.to_numeric(data[col])

print(data.describe())
#visualisation
# --- 1. Bar Plot : Rank vs Peak ---
plt.figure(figsize=(12, 6))
data_melted = data.melt(id_vars=['Tour title'], value_vars=['Rank', 'Peak'], var_name='Metric', value_name='Value')
sns.barplot(data=data_melted, x='Tour title', y='Value', hue='Metric')
plt.title('Comparaison : Rang Actuel vs Meilleur Classement (Peak)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plots/rank_vs_peak.png')
plt.show()

# --- 2. Scatter Plot : Revenu vs Nombre de Shows ---
# Est-ce que faire plus de concerts rapporte plus d'argent ?
plt.figure(figsize=(10, 6))
sns.scatterplot(data=data, x='Shows', y='Actual gross', hue='Artist', s=100)
plt.title('Relation entre Revenu (Actual Gross) et Nombre de Shows')
plt.xlabel('Nombre de Shows')
plt.ylabel('Revenu ($)')
plt.grid(True)
plt.savefig('plots/revenue_vs_shows.png')
plt.show()
#histogramme pour actual gross
plt.figure(figsize=(10, 6))
sns.histplot(data=data, x='Actual gross', kde=True)
plt.title('Distribution du Revenu (Actual Gross)')
plt.xlabel('Revenu ($)')
plt.ylabel('Fréquence')
plt.savefig('plots/gross_distribution.png')
plt.show()

# --- 3. Boxplot : Tour Duration Distribution ---
plt.figure(figsize=(10, 6))
sns.boxplot(x=data['Tour Duration'])
plt.title('Distribution de la Durée des Tournées (Années)')
plt.xlabel('Durée (Années)')
plt.savefig('plots/tour_duration_boxplot.png')
plt.show()

# --- 4. Bar Plot : Top 10 Artists by Career Gross ---
plt.figure(figsize=(12, 6))
top_artists = data[['Artist', 'Artist Career Gross']].drop_duplicates().sort_values('Artist Career Gross', ascending=False).head(10)
sns.barplot(data=top_artists, x='Artist', y='Artist Career Gross', palette='viridis')
plt.title('Top 10 Artistes par Revenu de Carrière Total')
plt.xticks(rotation=45)
plt.ylabel('Revenu Total ($)')
plt.tight_layout()
plt.savefig('plots/top_artists_gross.png')
plt.show()

# --- HYPOTHESIS TESTING ---
print("\n" + "="*50)
print("TESTS D'HYPOTHÈSES")
print("="*50)

# Hypothèse 1 : Corrélation entre le nombre de concerts (Shows) et le revenu total (Actual gross)
# H0 : Il n'y a pas de corrélation linéaire significative.
# H1 : Il existe une corrélation linéaire significative.

corr_coef, p_value_corr = stats.pearsonr(data['Shows'], data['Actual gross'])
print(f"\n1. Test de Corrélation (Shows vs Actual Gross) :")
print(f"   Coefficient de Pearson : {corr_coef:.4f}")
print(f"   P-value : {p_value_corr:.4e}")
if p_value_corr < 0.05:
    print("   -> Résultat Significatif : Il y a une corrélation (probablement positive).")
else:
    print("   -> Résultat Non Significatif : Pas de lien linéaire évident.")

# Hypothèse 2 : Les tournées récentes (après 2010) rapportent-elles plus que les anciennes ?
# H0 : Pas de différence significative de revenus moyens.
# H1 : Différence significative.

recent_tours = data[data['Start Year'] > 2010]['Actual gross']
older_tours = data[data['Start Year'] <= 2010]['Actual gross']

t_stat, p_value_ttest = stats.ttest_ind(recent_tours, older_tours, equal_var=False)
print(f"\n2. T-test (Revenus : Après 2010 vs Avant/En 2010) :")
print(f"   Moyenne (Récents)   : ${recent_tours.mean():,.2f}")
print(f"   Moyenne (Anciens)   : ${older_tours.mean():,.2f}")
print(f"   T-statistic : {t_stat:.4f}")
print(f"   P-value : {p_value_ttest:.4e}")

if p_value_ttest < 0.05:
    print("   -> Résultat Significatif : Il y a une différence significative de revenus selon l'époque.")
else:
    print("   -> Résultat Non Significatif : Pas de différence prouvée statistiquement.")
