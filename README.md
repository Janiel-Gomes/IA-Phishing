# 🛡️ IA-Phishing — Detector Multimodal de Phishing com IA

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

> **Avaliação Intermediária — IA Generativa (30% da nota final)**  
> Desenvolvido integralmente com auxílio de agente de codificação IA.

---

## 📋 Índice

- [Descrição do Problema e Solução](#-descrição-do-problema-e-solução)
- [Como a IA Será Integrada no Futuro](#-como-a-ia-será-integrada-no-futuro)
- [Funcionalidades Implementadas](#-funcionalidades-implementadas)
- [Arquitetura e Escolhas de Design](#-arquitetura-e-escolhas-de-design)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Configuração e Instalação](#-configuração-e-instalação)
- [O que Funcionou Bem](#-o-que-funcionou-bem)
- [O que Não Funcionou](#-o-que-não-funcionou)
- [Uso do Agente de Codificação](#-uso-do-agente-de-codificação)

---

## 🎯 Descrição do Problema e Solução

### O Problema

O phishing é uma das ameaças cibernéticas mais comuns e perigosas. Milhões de pessoas são vítimas todos os anos de sites falsos que imitam bancos, redes sociais e serviços governamentais para roubar dados pessoais. As ferramentas de detecção existentes geralmente analisam apenas a URL, ignorando outros sinais importantes como o conteúdo textual do e-mail, a estrutura HTML da página e até imagens/capturas de tela.

### A Solução

O **IA-Phishing** é uma plataforma web de **análise multimodal** que combina **4 agentes especializados** para detectar phishing de forma mais completa:

| Agente | O que analisa | Exemplos de detecção |
|--------|--------------|---------------------|
| 🔗 **URL Lexical** | Estrutura da URL | Domínios suspeitos, excesso de subdomínios, IPs no lugar de domínios |
| 📝 **NLP Text** | Conteúdo textual | Palavras de urgência ("sua conta será bloqueada"), erros gramaticais |
| 💻 **HTML Structural** | Código-fonte HTML | Formulários apontando para domínios diferentes, campos de senha em HTTP |
| 🖼️ **Vision** | Imagens/screenshots | Logos de marca, texto em imagens para burlar filtros |

Cada agente gera um **score de risco independente**, e um **orquestrador** consolida tudo com pesos ponderados para gerar o veredito final: **Legítima**, **Suspeita** ou **Phishing**.

---

## 🔮 Como a IA Será Integrada no Futuro

Atualmente, os agentes utilizam **heurísticas e análises baseadas em regras** (mock/placeholder). Na próxima etapa do projeto, cada agente será aprimorado com modelos de IA:

| Agente | Integração Futura |
|--------|-------------------|
| URL Lexical | Modelo BERT fine-tuned (`ealvaradob/bert-finetuned-phishing`) para classificação binária |
| NLP Text | LLM (GPT/Claude) via API para análise semântica de e-mails suspeitos |
| HTML Structural | Modelo treinado em features extraídas de HTML para detecção de páginas clonadas |
| Vision | OCR (Tesseract/PaddleOCR) + CLIP para detectar logos falsificados e texto em imagens |

A arquitetura multi-agente já está preparada para receber esses modelos sem alterar a interface.

---

## ✨ Funcionalidades Implementadas

### 🔍 Analisador Multimodal (Tela Principal)
- **Barra de entrada unificada** estilo chat com botão "+" para selecionar o tipo de análise
- **4 modos de entrada:** URL, Texto/E-mail, Código HTML e Upload de Imagem
- **Preview de imagem** antes do envio
- **Resultado detalhado** com score de confiança, badge colorido (Legítima/Phishing/Suspeito)
- **Insights por agente** — cada agente mostra seus findings individuais

### 📊 Página de Estatísticas
- **4 KPIs em cards:** Total de Análises, Phishing Detectado, Conteúdo Seguro, Taxa de Detecção
- **Barras de distribuição** animadas mostrando a proporção de cada resultado
- **Timeline** das últimas análises com ícones e cores por tipo

### 🕐 Histórico de Buscas
- **Últimas 10 análises** salvas em SQLite
- **Paginação inteligente:** mostra apenas as 2 mais recentes com botão "Ver Mais"
- **Expansão de detalhes:** clique na seta (▼) de qualquer item para expandir e ver o score de confiança e a análise completa da IA, com animação suave de abertura
- **Estilos premium** para a caixa de detalhe: gradiente sutil, labels em maiúsculo com ícone azul, separador elegante e glassmorphism na caixa de texto

### 🗂️ Sidebar de Navegação
- Menu lateral com glassmorphism
- Alternância entre "Analisador" e "Estatísticas"
- Botão de fechar (✕) dentro do menu + overlay clicável
- Design responsivo — colapsa em telas menores

---

## 🏗️ Arquitetura e Escolhas de Design

### Por que Flask (e não FastAPI/Gradio)?

Flask foi escolhido por:
1. **Flexibilidade total** no design da UI — sem limitações de componentes pré-prontos (como Gradio/Streamlit)
2. **Servir templates HTML** nativamente com Jinja2
3. **Simplicidade** — um único `app.py` serve backend, API e frontend
4. **Compatibilidade** com uploads de arquivos e FormData multipart

### Por que arquitetura Multi-Agente?

Em vez de um único modelo monolítico, optei por agentes especializados porque:
1. **Modularidade** — cada agente pode ser desenvolvido, testado e substituído independentemente
2. **Explicabilidade** — o usuário vê exatamente quais sinais cada agente detectou
3. **Escalabilidade** — novos agentes (ex: para análise de DNS, certificados SSL) podem ser adicionados sem mudar a interface
4. **Pesos configuráveis** — o orquestrador combina os scores com pesos ajustáveis

```
URL Lexical (25%) ──┐
NLP Text (35%)   ───┤──▶ Orquestrador ──▶ Veredito Final
HTML Struct (25%) ──┤
Vision (15%)     ───┘
```

### Por que SQLite?

- Não exige instalação de servidor de banco de dados
- Um único arquivo `.db` — portátil e simples
- Python já tem suporte nativo
- Suficiente para o escopo do protótipo

### Escolhas de UI/UX

- **Glassmorphism** — estilo visual moderno com transparências e blur, dando um ar premium à aplicação
- **Design escuro** — Adequado para uma ferramenta de segurança, reduz fadiga visual
- **Input unificado estilo "chat"** — inspirado em interfaces modernas de IA (ChatGPT, Claude), mais intuitivo do que formulários tradicionais
- **Responsivo** — sidebar colapsável, layout adaptável para mobile

---

## 📁 Estrutura do Projeto

```
IA-Phishing/
├── app.py                    # Servidor Flask, rotas API e banco de dados
├── requirements.txt          # Dependências Python
├── phishing_history.db       # Banco SQLite (gerado automaticamente)
│
├── agents/                   # Módulo de agentes de análise
│   ├── __init__.py
│   ├── orchestrator.py       # Orquestrador — combina resultados dos agentes
│   ├── url_agent.py          # Agente de análise lexical de URLs
│   ├── text_agent.py         # Agente de análise NLP de texto
│   ├── html_agent.py         # Agente de análise estrutural de HTML
│   └── vision_agent.py       # Agente de análise de imagens
│
├── templates/
│   └── index.html            # Template principal (Analisador + Estatísticas)
│
├── static/
│   ├── style.css             # Estilos customizados (630+ linhas)
│   └── script.js             # Lógica frontend (450+ linhas)
│
└── models/                   # Diretório para modelos de IA (futuro)
```

---

## 🚀 Tecnologias Utilizadas

| Camada | Tecnologia | Propósito |
|--------|-----------|-----------|
| **Backend** | Python 3.10, Flask | Servidor web, API REST |
| **Banco de Dados** | SQLite + Flask-SQLAlchemy | Persistência do histórico |
| **Frontend** | HTML5, CSS3, JavaScript ES6+ | Interface do usuário |
| **UI Framework** | Bootstrap 5 | Grid system, utilitários |
| **Ícones** | Font Awesome 6 | Iconografia |
| **Análise** | BeautifulSoup4, Requests | Parsing HTML, requisições HTTP |
| **IA (futuro)** | Transformers, Torch | Modelos BERT para classificação |

---

## 🛠️ Configuração e Instalação

### Pré-requisitos
- Python 3.8 ou superior

### Passo a Passo

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/IA-Phishing.git
cd IA-Phishing

# 2. Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Iniciar a aplicação
python app.py
```

A aplicação estará disponível em `http://localhost:5001`

### Publicar Endpoint (ngrok)

```bash
ngrok http 5001
```

---

## ✅ O que Funcionou Bem

### 1. Geração da Arquitetura Multi-Agente
O agente de codificação entendeu perfeitamente o conceito de múltiplos agentes especializados com um orquestrador central. Em um único prompt, ele gerou a estrutura completa dos 4 agentes (`url_agent.py`, `text_agent.py`, `html_agent.py`, `vision_agent.py`) e o `orchestrator.py` com o sistema de pesos ponderados. A separação de responsabilidades ficou limpa desde a primeira iteração.

**Exemplo de prompt efetivo:**
> "Evolua meu projeto para um sistema multi-agente com agentes especializados em URL, NLP, HTML e Visão, orquestrados por um agente central que consolida os resultados com pesos ponderados."

### 2. Interface Glassmorphism Completa
O agente gerou todo o CSS (550+ linhas) com o tema escuro + glassmorphism sem intervenção manual. Os efeitos de blur, transparência, bordas luminosas e animações de hover ficaram profissionais desde a primeira versão. A barra de input unificada com o menu "+" foi especialmente bem implementada.

### 3. Página de Estatísticas
Ao pedir "gere a página de estatísticas", o agente criou de uma só vez:
- O endpoint `/stats` no backend com queries SQL agregadas
- Os 4 cards KPI com ícones e cores
- As barras de distribuição animadas
- A timeline com ícones por tipo de resultado
- A navegação entre páginas (Analisador ↔ Estatísticas)

### 4. Persistência com SQLite
A integração Flask-SQLAlchemy foi gerada corretamente, incluindo o modelo `ScannedURL`, a criação automática do banco e o endpoint `/history` com paginação — tudo funcional sem nenhum ajuste.

### 5. Iteração Incremental
A estratégia de construir incrementalmente (estrutura → agentes → UI → refinamentos) funcionou muito bem com o agente. Cada iteração adicionava funcionalidade sem quebrar o que já existia.

---

## ❌ O que Não Funcionou

### 1. Bug de Referência JavaScript (`navAnalyzer`)
Após uma refatoração do frontend, o botão "Analisador" na sidebar parou de funcionar. O agente havia renomeado o ID no HTML mas não atualizou todas as referências no JavaScript, gerando um `ReferenceError: navAnalyzer is not defined`. 

**Como foi resolvido:** O agente identificou o problema ao analisar o console do navegador e adicionou o guard `if (navAnalyzer)` para proteger contra referências nulas.

**Aprendizado:** Ao fazer refatorações que envolvem múltiplos arquivos (HTML + JS), é importante verificar todas as referências cruzadas.

### 2. Sidebar que Não Fechava
Ao implementar o botão de toggle da sidebar na página de Estatísticas, o agente criou o botão mas ele ficava **atrás da sidebar** quando ela abria, tornando impossível fechá-la. O overlay de fundo (que deveria fechar ao clique) existia no código mas o usuário não percebia que podia clicar ali.

**Como foi resolvido:** Adicionamos um botão de fechar (✕) **dentro** da sidebar, ao lado do logo, para que o usuário sempre tenha uma forma visível de fechar o menu.

**Aprendizado:** Interações de toggle precisam de múltiplos caminhos de saída para boa UX.

### 3. Desalinhamento de Larguras (Input vs. Histórico)
A barra de input e a seção de histórico tinham `max-width` diferentes (700px vs. 800px), causando um desalinhamento visual. Isso aconteceu porque o agente modificou os componentes em momentos diferentes sem manter consistência entre eles.

**Como foi resolvido:** Unificamos ambos para `max-width: 800px`.

### 4. Dificuldade com Edições no HTML
O agente teve repetidas falhas ao tentar inserir blocos de HTML grandes no arquivo `index.html`. O tool de edição de código não encontrava o conteúdo-alvo quando havia caracteres especiais (CRLF, acentos) ou quando o trecho aparecia mais de uma vez no arquivo. Foram necessárias várias tentativas com abordagens diferentes até conseguir inserir o bloco da página de estatísticas.

**Aprendizado:** Edição de arquivos HTML grandes com muitos blocos similares (`</div></section>`) é um desafio para ferramentas automatizadas.

### 5. VisionAgent Básico
O agente de visão (`vision_agent.py`) é atualmente o mais limitado — ele verifica apenas metadados básicos da imagem (tamanho, tipo) e retorna um score fixo baixo. Não há OCR, detecção de logos ou análise visual real ainda.

**Razão:** Manter o protótipo leve e funcional. A integração com modelos de visão computacional está planejada para a próxima fase.

### 6. Função de Toggle do Histórico Não Definida
O HTML dinâmico dos cards do histórico chamava `toggleHistoryDetail(index)` via atributo `onclick`, mas essa função nunca havia sido declarada no `script.js`. Como resultado, clicar na seta (▼) de qualquer item do histórico não produzia nenhum efeito visível para o usuário.

**Como foi resolvido:** O agente identificou a função ausente ao inspecionar o `script.js` e adicionou a implementação completa com toggle de `display` e rotação do chevron via `style.transform`.

**Aprendizado:** Funções chamadas via `onclick` em HTML gerado dinamicamente devem ser sempre declaradas no escopo global (`window.toggleHistoryDetail = ...`) para serem acessíveis fora do escopo de módulos.

---

## 🤖 Uso do Agente de Codificação

### Ferramenta Utilizada
**Gemini (Antigravity)** — agente de codificação integrado ao VS Code, com acesso direto ao filesystem, terminal e navegador.

### Processo de Desenvolvimento

O desenvolvimento seguiu uma abordagem **iterativa e incremental**, utilizando o agente em todas as etapas:

| Fase | O que foi pedido ao agente | Resultado |
|------|--------------------------|-----------|
| **1. Setup** | "Analise o projeto e me diga como rodar" | Identificou a estrutura Flask, dependências e porta |
| **2. Multi-Agente** | "Evolua para sistema multi-agente com URL, NLP, HTML e Vision agents" | Gerou 5 arquivos Python completos |
| **3. Histórico** | "Implemente busca recente com SQLite" | Criou modelo, endpoint e rendering no frontend |
| **4. UI Unificada** | "Crie interface unificada estilo chat com menu +" | Refatorou completamente o frontend (HTML + CSS + JS) |
| **5. Bug Fix** | "O botão analisador não funciona" (screenshot) | Diagnosticou ReferenceError e corrigiu |
| **6. Refinamento** | "Alinhe a largura do input com o histórico" | Ajustou max-width de 700px→800px |
| **7. Paginação** | "Mostre apenas 2 itens com botão Ver Mais" | Implementou paginação com toggle |
| **8. Estatísticas** | "Gere a página de estatísticas" (screenshot de referência) | Criou endpoint + HTML + CSS + JS completos |
| **9. Sidebar** | "Adicione botão para abrir/fechar menu lateral" | Adicionou toggle + close button |
| **10. Bug Fix Histórico** | "Clico na seta mas não aparece o texto" | Diagnosticou função `toggleHistoryDetail` ausente e a implementou |
| **11. Estilo Histórico** | "Deixe essas caixas de textos mais bonitas" | Adicionou 70+ linhas de CSS premium para as caixas de detalhes |

### Extensão do Uso

- **~95% do código foi gerado pelo agente**, incluindo todo o CSS, JavaScript, HTML e a maior parte do Python
- **Intervenção manual** limitou-se a aprovações de comandos e feedback visual (screenshots)
- O agente fez **planning → implementation → verification** em ciclos estruturados
- Quando encontrou bugs, o agente usou screenshots do navegador para diagnosticar

### Exemplos de Prompts Efetivos

```
✅ "Evolua meu projeto para um sistema multi-agente com agentes 
especializados em URL, NLP, HTML e Visão"
→ Resultado: Gerou toda a arquitetura em uma iteração

✅ "Gere a página de estatísticas agora" + screenshot de referência
→ Resultado: Criou backend + frontend de uma vez, seguindo o design de referência

✅ "Deixe a caixa de inserir do mesmo tamanho de buscas recentes"
→ Resultado: Identificou e corrigiu o desalinhamento CSS
```

### Exemplos de Prompts que Precisaram de Iteração

```
⚠️ "Adicione botão para abrir/fechar menu lateral"
→ Problema: Primeira versão não permitia fechar a sidebar
→ Solução: Após feedback visual, adicionou botão ✕ dentro da sidebar

⚠️ "Mostre apenas 2 últimas buscas com botão Ver Mais"  
→ Problema: Botão não foi inserido no HTML na primeira tentativa
→ Solução: Necessitou múltiplas tentativas de edição até encontrar o ponto correto
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido por Janiel Gomes** — Avaliação Intermediária, Disciplina de IA Generativa, 2026.
