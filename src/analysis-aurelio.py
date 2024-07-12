import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.proportion import proportions_ztest

# Carregar o dataset
df = pd.read_csv('dataset/dados_judiciais.csv', delimiter=',')

# Renomear colunas
df.columns = ['id', 'gratuidade_justica', 'resultado_processo']

# Converter valores da coluna 'gratuidade_justica' para booleano
df['gratuidade_justica'] = df['gratuidade_justica'].astype(bool)

# Substituir valores de 'resultado_processo' não relevantes por NaN
relevant_categories = ['Procedente', 'Improcedente', 'Parcialmente Procedente', 'Extinto', 'Acordo']
df['resultado_processo'] = df['resultado_processo'].apply(lambda x: x if x in relevant_categories else None)

# Remover linhas com NaN em 'resultado_processo'
df = df.dropna(subset=['resultado_processo'])

# Análise Exploratória
print(df['gratuidade_justica'].value_counts())
print(df['resultado_processo'].value_counts())

# Tabela de Contingência
contingency_table = pd.crosstab(df['resultado_processo'], df['gratuidade_justica'])
print(contingency_table)

# Teste Qui-Quadrado
chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
print(f"Qui-Quadrado: {chi2}")
print(f"P-valor: {p}")

# Proporções
proportions = contingency_table.div(contingency_table.sum(axis=1), axis=0)
print(proportions)

# Testes de Proporções
for result in contingency_table.index:
    count = contingency_table.loc[result]
    nobs = df['gratuidade_justica'].value_counts()
    z_stat, p_val = proportions_ztest(count, nobs)
    print(f"Resultado: {result}")
    print(f"Z-statistic: {z_stat}")
    print(f"P-valor: {p_val}\n")

# Gráficos

# Gráfico de Barras Empilhadas com Proporções
proportions.plot(kind='bar', stacked=True)
plt.xlabel('Resultado do Processo')
plt.ylabel('Proporção')
plt.title('Proporção dos Resultados do Processo por Gratuidade da Justiça')
plt.legend(title='Gratuidade da Justiça')
plt.show()

# Gráfico de Setores
df[df['gratuidade_justica'] == True]['resultado_processo'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title('Distribuição dos Resultados (Com Gratuidade)')
plt.ylabel('')
plt.show()

df[df['gratuidade_justica'] == False]['resultado_processo'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title('Distribuição dos Resultados (Sem Gratuidade)')
plt.ylabel('')
plt.show()

# Heatmap de Contingência
sns.heatmap(contingency_table, annot=True, fmt="d", cmap="YlGnBu")
plt.xlabel('Gratuidade da Justiça')
plt.ylabel('Resultado do Processo')
plt.title('Heatmap de Contingência')
plt.show()

# Gráfico de Barras Separadas
sns.catplot(data=df, x='resultado_processo', hue='gratuidade_justica', kind='count', height=6, aspect=2)
plt.xlabel('Resultado do Processo')
plt.ylabel('Contagem')
plt.title('Distribuição dos Resultados do Processo por Gratuidade da Justiça')
plt.show()