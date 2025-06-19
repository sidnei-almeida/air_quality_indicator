import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Definir semente para reprodutibilidade
np.random.seed(42)

# Criar datas para um ano de dados (medições diárias)
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
n_samples = len(dates)

# Função para gerar dados com variação sazonal
def generate_seasonal_data(base, amplitude, noise_level):
    # Criar componente sazonal
    seasonal = amplitude * np.sin(2 * np.pi * np.arange(n_samples) / 365)
    # Adicionar ruído
    noise = np.random.normal(0, noise_level, n_samples)
    # Combinar e garantir valores não negativos
    return np.maximum(0, base + seasonal + noise)

# Gerar dados para cada poluente
data = {
    'date': dates,
    'co': generate_seasonal_data(290, 50, 20),      # CO tem variação maior no inverno
    'no2': generate_seasonal_data(25, 10, 5),       # NO2 varia com tráfego
    'so2': generate_seasonal_data(1, 0.5, 0.2),     # SO2 relativamente estável
    'o3': generate_seasonal_data(25, 15, 5),        # O3 maior no verão
    'pm2.5': generate_seasonal_data(10, 5, 2),      # PM2.5 maior no inverno
    'pm10': generate_seasonal_data(15, 7, 3)        # PM10 varia com clima seco
}

# Criar DataFrame
df = pd.DataFrame(data)

# Adicionar alguns eventos extremos (ex: queimadas, inversão térmica)
extreme_days = np.random.choice(n_samples, 10, replace=False)
for day in extreme_days:
    df.iloc[day, 1:] *= np.random.uniform(1.5, 2.5)

# Garantir que todos os valores estejam dentro dos limites realistas
df['co'] = df['co'].clip(0, 1000)
df['no2'] = df['no2'].clip(0, 100)
df['so2'] = df['so2'].clip(0, 50)
df['o3'] = df['o3'].clip(0, 100)
df['pm2.5'] = df['pm2.5'].clip(0, 100)
df['pm10'] = df['pm10'].clip(0, 150)

# Salvar o arquivo
df.to_csv('test_data.csv', index=False)
print('Arquivo test_data.csv criado com sucesso!') 