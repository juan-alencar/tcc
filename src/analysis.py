import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

# Carregando o arquivo CSV
df = pd.read_csv('dataset/dados_judiciais.csv')


print(df.head())
################################################################


print("Frequência de processos por gratuidade:")
print(df['gratuidade'].value_counts())

print()
print()

################################################################

print("Frequência de processos por sentenca:")
print(df['sentenca'].value_counts())

print()
print()

################################################################

freq_rel = df.groupby('gratuidade')['sentenca'].value_counts(normalize=True)
print("Frequência relativa de sentencas por gratuidade:")
print(freq_rel)

print()
print()

################################################################

# Criando uma tabela de contingência
contingency_table = pd.crosstab(df['gratuidade'], df['sentenca'])

# Teste Qui-Quadrado
chi2, p, dof, expected = chi2_contingency(contingency_table)
print(f"Valor de Chi2: {chi2}, P-valor: {p}")


print()
print()

################################################################

# le = LabelEncoder()
# df['sentenca'] = le.fit_transform(df['sentenca'])

# # Dividindo os dados em conjuntos de treino e teste
# X_train, X_test, y_train, y_test = train_test_split(df[['gratuidade']], df['sentenca'], test_size=0.3, random_state=42)

# # Criando e treinando o modelo de regressão logística
# model = LogisticRegression()
# model.fit(X_train, y_train)

# # Avaliando o modelo
# print("Acurácia do modelo com todas as categorias:", model.score(X_test, y_test))


# Filtrando o DataFrame para manter apenas "Procedente" e "Improcedente"
df_filtered = df[df['sentenca'].isin(['Procedente', 'Improcedente'])]

# Codificando as categorias "Procedente" e "Improcedente"

le = LabelEncoder()
# Criando uma cópia independente do DataFrame filtrado
df_filtered = df[df['sentenca'].isin(['Procedente', 'Improcedente'])].copy()

# Modificando a coluna 'sentenca' na cópia
df_filtered['sentenca'] = le.fit_transform(df_filtered['sentenca'])

X_train, X_test, y_train, y_test = train_test_split(df_filtered[['gratuidade']], df_filtered['sentenca'], test_size=0.3, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

# Avaliando o modelo
print("Acurácia do modelo com categorias Procedente e Improcedente:", model.score(X_test, y_test))

print()
print()


