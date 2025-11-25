# 🧠 Synapse — Organizador Semântico de Anotações de Estudo

Sistema inteligente para organizar e recuperar conhecimento usando **Busca Semântica** e **Modelagem em Grafo**, demonstrando o conceito de **Persistência Poliglota**.

---

## 📌 Sobre o Projeto

O **Synapse** é uma aplicação voltada para estudantes universitários que precisam organizar suas anotações e revisitar conteúdos de forma rápida e intuitiva.

Combinamos:

- **Embeddings** para representar o significado das anotações  
- **Banco Vetorial (ChromaDB)** para busca semântica  
- **Banco em Grafo (Neo4j)** para estruturar relações entre matérias, temas e notas  
- **Backend em Python** para integrar as tecnologias

O resultado é um sistema capaz de encontrar anotações não pelas palavras exatas, mas **pelo significado**.

---

## 🧩 Arquitetura Poliglota

A aplicação usa diferentes tecnologias, cada uma na sua especialidade:

### **🔹 ChromaDB — Banco Vetorial**
- Armazena embeddings  
- Realiza busca por similaridade (kNN)  

### **🔹 Neo4j — Banco em Grafo**
- Armazena nós das anotações  
- Modela relações entre temas, matérias e outras notas  

### **🔹 Python — Backend**
- Gera embeddings  
- Faz consultas nos bancos  
- Monta o resultado final para o usuário  

---

## 🖼 Estrutura do Projeto

projeto-synapse/
│
├── src/
│   ├── embeddings.py
│   ├── synapse_core.py
│   ├── chroma_service.py
│   ├── neo4j_service.py
│   └── __init__.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── app.py
├── requirements.txt
├── docker-compose.yml
├── README.md

---

## 🚀 Como Rodar o Projeto

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Suba os serviços com Docker
```bash
docker-compose up -d
```

### 3. Execute o backend
```bash
python app.py
```

### 4. Acesse no navegador
```
http://localhost:5000
```

---

## ✨ Funcionalidades

- Cadastro de anotações  
- Geração automática de embeddings  
- Busca semântica por similaridade  
- Visualização do contexto por grafo  
- Interface simples e objetiva  

---

## 👥 Integrantes

- Gabriel Lopes — Backend  
- Jean Carlos — Banco de Dados  
- Pedro Garcia — Documentação e Estrutura Visual  
- Yasmin Melo — Frontend  

---

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos no curso de Engenharia de Software da **Universidade de Rio Verde (UniRV)** — 8º Período.
