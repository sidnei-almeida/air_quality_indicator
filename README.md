# 🌬️ Indicador de Qualidade do Ar

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit Version](https://img.shields.io/badge/streamlit-1.31.1-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production-brightgreen)

*Um sistema avançado de monitoramento e previsão da qualidade do ar usando Machine Learning*

[Funcionalidades](#-funcionalidades) •
[Instalação](#-instalação) •
[Uso](#-como-usar) •
[Documentação](#-documentação) •
[Contribuição](#-contribuindo)

</div>

## 🎯 Visão Geral

O Indicador de Qualidade do Ar é uma aplicação web moderna desenvolvida para monitorar, analisar e prever índices de qualidade do ar. Utilizando técnicas avançadas de Machine Learning, o sistema processa dados de diversos poluentes atmosféricos para fornecer previsões precisas e insights valiosos sobre a qualidade do ar.

### 🌟 Destaques
- Interface web moderna e responsiva
- Sistema robusto de autenticação
- Processamento em tempo real
- Visualizações interativas
- Suporte a análises em lote
- Exportação de dados em múltiplos formatos

## ✨ Funcionalidades

### 🔐 Sistema de Autenticação
- Sistema seguro de login e registro
- Proteção de rotas sensíveis
- Gerenciamento de sessões
- Recuperação de senha
- Níveis de acesso personalizáveis

### 🎯 Previsão Individual
- Interface intuitiva para entrada de dados
- Validação em tempo real
- Feedback visual imediato
- Histórico de previsões
- Gráficos comparativos detalhados
- Recomendações personalizadas

### 📊 Previsões em Lote
- Suporte a upload de arquivos CSV
- Validação robusta de dados
- Processamento otimizado em lote
- Visualizações interativas:
  - Distribuição do AQI
  - Análise temporal
  - Correlações
  - Contribuição dos poluentes
  - Insights automáticos
- Exportação em múltiplos formatos

### 📈 Análise de Dados
- Análise temporal avançada
- Correlação entre poluentes
- Distribuições estatísticas
- Métricas resumidas
- Detecção de anomalias
- Tendências sazonais

## 🛠️ Tecnologias

### Core
- Python 3.8+
- Streamlit 1.31.1
- Pandas 2.2.0
- NumPy 1.26.3

### Machine Learning
- Scikit-learn 1.4.0
- Joblib 1.3.2

### Visualização
- Plotly 5.18.0

### Segurança
- PyYAML 6.0.1
- Streamlit-Authenticator 0.3.1

## 📦 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Passos de Instalação

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/air_quality_indicator.git
cd air_quality_indicator
```

2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### Iniciando o Aplicativo
```bash
streamlit run app.py
```

### Configuração Inicial

1. Configure o arquivo de autenticação:
```yaml
# config.yaml
credentials:
  usernames:
    admin:
      email: admin@exemplo.com
      name: Administrador
      password: # senha hasheada
cookie:
  expiry_days: 30
  key: chave_segura
  name: cookie_auth
```

2. Configure as variáveis de ambiente (opcional):
```bash
export AQI_ENV=production
export AQI_DEBUG=false
```

## 📊 Formato dos Dados

### Estrutura do CSV
O sistema aceita arquivos CSV com as seguintes colunas:

| Coluna | Descrição | Unidade | Faixa Válida |
|--------|-----------|---------|--------------|
| date   | Data da medição | YYYY-MM-DD | - |
| co     | Monóxido de Carbono | μg/m³ | 0-1000 |
| no2    | Dióxido de Nitrogênio | μg/m³ | 0-500 |
| so2    | Dióxido de Enxofre | μg/m³ | 0-500 |
| o3     | Ozônio | μg/m³ | 0-400 |
| pm2.5  | Material Particulado < 2.5μm | μg/m³ | 0-250 |
| pm10   | Material Particulado < 10μm | μg/m³ | 0-430 |

### Exemplo de Dados
```csv
date,co,no2,so2,o3,pm2.5,pm10
2024-01-01,1.2,23.4,5.6,48.2,12.3,25.7
```

## 📈 Interpretação do AQI

| Faixa AQI | Classificação | Recomendações |
|-----------|---------------|---------------|
| 0-50 | Bom | Condições ideais para atividades ao ar livre |
| 51-100 | Moderado | Pessoas sensíveis devem reduzir exposição prolongada |
| 101-150 | Insalubre para Grupos Sensíveis | Reduzir atividades ao ar livre |
| 151-200 | Insalubre | Evitar atividades ao ar livre |
| 201-300 | Muito Insalubre | Permanecer em ambientes fechados |
| 301+ | Perigoso | Evitar qualquer exposição externa |

## 🔍 Recursos Avançados

### API REST
O sistema oferece endpoints REST para integração:
```python
GET /api/v1/predict
POST /api/v1/batch-predict
GET /api/v1/statistics
```

### Customização
- Temas personalizáveis
- Dashboards configuráveis
- Alertas customizáveis
- Relatórios automatizados

## 🤝 Contribuindo

Adoramos receber contribuições! Para contribuir:

1. Fork o projeto
2. Crie sua Feature Branch
```bash
git checkout -b feature/RecursoIncrivel
```
3. Commit suas mudanças
```bash
git commit -m 'Adiciona novo recurso incrível'
```
4. Push para a Branch
```bash
git push origin feature/RecursoIncrivel
```
5. Abra um Pull Request

### Diretrizes de Contribuição
- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Mantenha o histórico de commits limpo

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores e Mantenedores

- **Seu Nome** - *Desenvolvedor Principal* - [GitHub](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Streamlit pela excelente framework
- Comunidade Python pelos pacotes incríveis
- Contribuidores do projeto
- Usuários que fornecem feedback valioso

## 📞 Suporte

- Abra uma issue para bugs
- Discussões no GitHub para dúvidas
- Email para contato profissional

## 🚀 Deploy no Streamlit Share

Para fazer o deploy do aplicativo no Streamlit Share:

1. Faça fork do repositório para sua conta do GitHub

2. Acesse [share.streamlit.io](https://share.streamlit.io)

3. Faça login com sua conta do GitHub

4. Clique em "New app" e selecione o repositório

5. Configure as seguintes variáveis de ambiente:
   - `GITHUB_RAW_URL`: URL base do seu repositório (ex: "https://raw.githubusercontent.com/seu-usuario/air_quality_indicator/main")

6. Clique em "Deploy!"

O aplicativo irá automaticamente:
- Baixar o modelo treinado do GitHub
- Carregar os dados de referência
- Configurar a autenticação

### Observações Importantes
- Certifique-se de que todos os arquivos necessários (modelo, dados, config) estão no repositório
- O arquivo `config.yaml` deve estar atualizado com as credenciais corretas
- O modelo `rf_model.joblib` deve estar presente no repositório
- O arquivo `airquality.csv` deve estar disponível para normalização dos dados

---

<div align="center">

Desenvolvido com ❤️ pela comunidade para um ar mais limpo 🌍

[⬆ Voltar ao topo](#-indicador-de-qualidade-do-ar)

</div>
