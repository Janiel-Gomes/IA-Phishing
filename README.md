# 🛡️ IA-Phishing: Detector de Sites Maliciosos

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

IA-Phishing é uma aplicação web moderna que utiliza Inteligência Artificial para identificar URLs suspeitas de phishing. Com uma interface minimalista e intuitiva, o sistema analisa padrões digitais para ajudar usuários a navegar com mais segurança.

![Dashboard Preview](https://via.placeholder.com/800x450/0f172a/6366f1?text=IA-Phishing+Dashboard+Preview)

## ✨ Funcionalidades

- **🔍 Análise em Tempo Real**: Verificação instantânea de URLs suspeitas.
- **🧠 Inteligência Artificial**: Modelo treinado com milhares de exemplos de sites legítimos e maliciosos.
- **📊 Histórico Local**: Acompanhe suas verificações recentes salvas no navegador.
- **🎨 Design Premium**: Interface moderna com glassmorphism, modo noturno e responsiva.
- **📈 Confiança da IA**: Exibição da probabilidade de acerto da predição (quando disponível).

## 🚀 Tecnologias

- **Backend**: Python 3, Flask, Scikit-Learn, Pandas.
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism), JavaScript (ES6+), Bootstrap 5.
- **Modelo**: Pipeline de processamento de linguagem natural (NLP) com CountVectorizer e Classificador Random Forest (ou similar).

## 🛠️ Configuração e Instalação

### Pré-requisitos
- Python 3.8 ou superior instalado.

### Passo a Passo

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/IA-Phishing.git
   cd IA-Phishing
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install flask flask-cors transformers torch
   ```

4. **Inicie a aplicação**:
   Ao rodar pela primeira vez, o sistema baixará automaticamente o modelo BERT (~500MB).
   ```bash
   python app.py
   ```

5. **Acesse no navegador**:
   Abra `http://localhost:5001`

## 📁 Estrutura do Projeto

```text
IA-Phishing/
├── app.py              # Servidor Flask e Lógica da API
├── models/             # Modelos de IA treinados (.pkl)
├── static/             # Recursos estáticos (CSS, JS, Imagens)
├── templates/          # Templates HTML (Jinja2)
└── requirements.txt    # Lista de dependências
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---
Desenvolvido para fins educacionais e de segurança digital.
