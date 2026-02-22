# 🧠 EstudioIA

App de estudio con IA que analiza tu material de facultad y genera automáticamente:
- 📋 Resumen ejecutivo
- 🃏 Flashcards interactivas
- 🧪 Quiz con corrección automática
- 💡 Conceptos clave

## Cómo usar

1. Subí un PDF, Word, imagen de apunte o pegá texto
2. Hacé clic en "Analizar material"
3. ¡Estudiá con las herramientas generadas!

## Deploy en Streamlit Cloud

1. Subí este repo a GitHub
2. Entrá a [share.streamlit.io](https://share.streamlit.io)
3. Conectá tu repo
4. En **Secrets**, agregá:
```toml
GEMINI_API_KEY = "tu_api_key_aqui"
```

## Desarrollo local

```bash
pip install -r requirements.txt
# Crear archivo .streamlit/secrets.toml con tu API key
streamlit run app.py
```
