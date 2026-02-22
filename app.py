import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx
import json
import random
from PIL import Image
import io
import os

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EstudioIA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif;
}

.main { background-color: #0f0f13; color: #e8e8f0; }

.stApp { background-color: #0f0f13; }

section[data-testid="stSidebar"] {
    background-color: #16161e;
    border-right: 1px solid #2a2a3a;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}

.hero-sub {
    color: #6b7280;
    font-size: 1rem;
    font-weight: 300;
    margin-bottom: 2rem;
}

.card {
    background: #16161e;
    border: 1px solid #2a2a3a;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}

.card:hover { border-color: #a78bfa; }

.flashcard {
    background: linear-gradient(135deg, #1e1e2e, #16213e);
    border: 1px solid #3b3b5c;
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    min-height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.3s;
    margin: 1rem 0;
}

.flashcard:hover {
    border-color: #a78bfa;
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(167,139,250,0.15);
}

.badge {
    display: inline-block;
    background: #1e1e2e;
    border: 1px solid #3b3b5c;
    border-radius: 999px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    color: #a78bfa;
    margin: 0.2rem;
}

.concept-pill {
    display: inline-block;
    background: linear-gradient(135deg, #1e1e2e, #16213e);
    border: 1px solid #3b3b5c;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    color: #60a5fa;
    margin: 0.3rem;
}

.score-box {
    background: linear-gradient(135deg, #1a2a1a, #0f1f0f);
    border: 1px solid #34d399;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    padding: 0.6rem 1.5rem;
    transition: all 0.2s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
}

.stTextArea textarea, .stTextInput input {
    background: #16161e !important;
    border: 1px solid #2a2a3a !important;
    color: #e8e8f0 !important;
    border-radius: 10px !important;
}

.stSelectbox > div > div {
    background: #16161e !important;
    border: 1px solid #2a2a3a !important;
    color: #e8e8f0 !important;
}

div[data-testid="stExpander"] {
    background: #16161e;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #60a5fa);
}

hr { border-color: #2a2a3a; }
</style>
""", unsafe_allow_html=True)

# ─── API SETUP ────────────────────────────────────────────────────────────────
def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.sidebar.error("⚠️ No se encontró la API key. Configurala en Streamlit Secrets.")
        return False
    genai.configure(api_key=api_key)
    return True

# ─── EXTRACCIÓN DE TEXTO ──────────────────────────────────────────────────────
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text_from_image(file):
    model = genai.GenerativeModel("gemini-1.5-flash")
    img = Image.open(file)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    response = model.generate_content([
        "Transcribí todo el texto que aparece en esta imagen de apunte o material de estudio. "
        "Mantené la estructura original lo mejor posible.",
        {"mime_type": "image/png", "data": buf.getvalue()}
    ])
    return response.text

# ─── GENERACIÓN CON IA ────────────────────────────────────────────────────────
def generate_study_content(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""Analizá el siguiente material de estudio y generá contenido de estudio en formato JSON.

Respondé ÚNICAMENTE con un JSON válido con esta estructura exacta:
{{
  "resumen": "Resumen ejecutivo del tema en 3-5 párrafos",
  "conceptos_clave": ["concepto1", "concepto2", "concepto3"],
  "flashcards": [
    {{"pregunta": "¿...?", "respuesta": "..."}},
    {{"pregunta": "¿...?", "respuesta": "..."}}
  ],
  "quiz": [
    {{
      "pregunta": "¿...?",
      "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correcta": "A) ...",
      "explicacion": "Porque..."
    }}
  ]
}}

Generá al menos:
- 8 flashcards
- 5 preguntas de quiz con 4 opciones cada una
- 6 conceptos clave

MATERIAL DE ESTUDIO:
{text[:12000]}
"""
    response = model.generate_content(prompt)
    raw = response.text.strip()
    # Limpiar markdown si viene con backticks
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family: Syne; font-size:1.4rem; font-weight:800; color:#a78bfa;">🧠 EstudioIA</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b7280; font-size:0.8rem;">Tu asistente de estudio con IA</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**📂 Cargá tu material**")
    input_method = st.radio("Método de entrada:", ["📄 PDF", "📝 Word (.docx)", "📸 Imagen/Foto", "✏️ Texto directo"])

    uploaded_file = None
    pasted_text = ""

    if input_method == "📄 PDF":
        uploaded_file = st.file_uploader("Subí tu PDF", type=["pdf"])
    elif input_method == "📝 Word (.docx)":
        uploaded_file = st.file_uploader("Subí tu Word", type=["docx"])
    elif input_method == "📸 Imagen/Foto":
        uploaded_file = st.file_uploader("Subí tu foto de apunte", type=["png", "jpg", "jpeg", "webp"])
    else:
        pasted_text = st.text_area("Pegá tu texto acá:", height=200, placeholder="Copiá y pegá el texto del material...")

    st.divider()
    analizar = st.button("🚀 Analizar material", use_container_width=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">EstudioIA</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Subí tu material de facultad y la IA genera todo lo que necesitás para estudiar</div>', unsafe_allow_html=True)

if not init_gemini():
    st.info("👈 Configurá tu API key de Gemini en los secrets de Streamlit para comenzar.")
    st.stop()

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📋 Resumen", "🃏 Flashcards", "🧪 Quiz", "💡 Conceptos"])

# ─── PROCESAMIENTO ────────────────────────────────────────────────────────────
if analizar:
    text = ""
    with st.spinner("Extrayendo texto del material..."):
        try:
            if uploaded_file:
                if input_method == "📄 PDF":
                    text = extract_text_from_pdf(uploaded_file)
                elif input_method == "📝 Word (.docx)":
                    text = extract_text_from_docx(uploaded_file)
                elif input_method == "📸 Imagen/Foto":
                    text = extract_text_from_image(uploaded_file)
            elif pasted_text:
                text = pasted_text

            if not text.strip():
                st.error("No se pudo extraer texto. Verificá el archivo.")
                st.stop()

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            st.stop()

    with st.spinner("🤖 La IA está analizando tu material..."):
        try:
            content = generate_study_content(text)
            st.session_state["content"] = content
            st.session_state["quiz_idx"] = 0
            st.session_state["quiz_score"] = 0
            st.session_state["quiz_answered"] = []
            st.session_state["flash_idx"] = 0
            st.session_state["flash_show_answer"] = False
            st.success("✅ ¡Material analizado! Explorá las pestañas.")
        except Exception as e:
            st.error(f"Error al generar contenido con IA: {e}")
            st.stop()

# ─── CONTENIDO ────────────────────────────────────────────────────────────────
if "content" in st.session_state:
    c = st.session_state["content"]

    # TAB 1: RESUMEN
    with tab1:
        st.markdown("### 📋 Resumen del tema")
        st.markdown(f'<div class="card">{c["resumen"]}</div>', unsafe_allow_html=True)

    # TAB 2: FLASHCARDS
    with tab2:
        st.markdown("### 🃏 Flashcards")
        cards = c["flashcards"]
        total = len(cards)

        if "flash_idx" not in st.session_state:
            st.session_state["flash_idx"] = 0
            st.session_state["flash_show_answer"] = False

        idx = st.session_state["flash_idx"]
        show = st.session_state["flash_show_answer"]

        st.progress((idx + 1) / total)
        st.markdown(f'<p style="color:#6b7280; text-align:center;">{idx + 1} / {total}</p>', unsafe_allow_html=True)

        card = cards[idx]
        if not show:
            st.markdown(f'<div class="flashcard"><div><span class="badge">PREGUNTA</span><br><br>{card["pregunta"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="flashcard"><div><span class="badge">RESPUESTA</span><br><br>{card["respuesta"]}</div></div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                st.session_state["flash_idx"] = max(0, idx - 1)
                st.session_state["flash_show_answer"] = False
                st.rerun()
        with col2:
            label = "👁️ Ver respuesta" if not show else "🙈 Ocultar"
            if st.button(label, use_container_width=True):
                st.session_state["flash_show_answer"] = not show
                st.rerun()
        with col3:
            if st.button("➡️ Siguiente", use_container_width=True):
                st.session_state["flash_idx"] = min(total - 1, idx + 1)
                st.session_state["flash_show_answer"] = False
                st.rerun()

        if st.button("🔀 Aleatorio", use_container_width=True):
            st.session_state["flash_idx"] = random.randint(0, total - 1)
            st.session_state["flash_show_answer"] = False
            st.rerun()

    # TAB 3: QUIZ
    with tab3:
        st.markdown("### 🧪 Quiz de práctica")
        quiz = c["quiz"]
        total_q = len(quiz)

        if "quiz_answered" not in st.session_state:
            st.session_state["quiz_answered"] = []
            st.session_state["quiz_score"] = 0
            st.session_state["quiz_idx"] = 0

        q_idx = st.session_state["quiz_idx"]
        answered = st.session_state["quiz_answered"]

        if q_idx < total_q:
            q = quiz[q_idx]
            st.progress((q_idx) / total_q)
            st.markdown(f'<p style="color:#6b7280;">Pregunta {q_idx + 1} de {total_q} · Puntaje: {st.session_state["quiz_score"]}/{q_idx}</p>', unsafe_allow_html=True)

            st.markdown(f'<div class="card"><b>{q["pregunta"]}</b></div>', unsafe_allow_html=True)

            if q_idx not in [a["idx"] for a in answered]:
                selected = st.radio("Elegí tu respuesta:", q["opciones"], key=f"quiz_{q_idx}")
                if st.button("✅ Confirmar respuesta", use_container_width=True):
                    correct = selected == q["correcta"]
                    if correct:
                        st.session_state["quiz_score"] += 1
                        st.success("🎉 ¡Correcto!")
                    else:
                        st.error(f"❌ Incorrecto. La respuesta era: **{q['correcta']}**")
                    st.info(f"💡 {q['explicacion']}")
                    st.session_state["quiz_answered"].append({"idx": q_idx, "correct": correct})
                    st.session_state["quiz_idx"] += 1
                    st.rerun()
            else:
                if st.button("➡️ Siguiente pregunta", use_container_width=True):
                    st.session_state["quiz_idx"] += 1
                    st.rerun()
        else:
            score = st.session_state["quiz_score"]
            pct = int(score / total_q * 100)
            emoji = "🏆" if pct >= 80 else "📚" if pct >= 50 else "💪"
            st.markdown(f"""
            <div class="score-box">
                <p style="font-size:3rem;">{emoji}</p>
                <p style="font-family:Syne; font-size:2rem; font-weight:800; color:#34d399;">{pct}%</p>
                <p style="color:#6b7280;">{score} de {total_q} correctas</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Reiniciar quiz", use_container_width=True):
                st.session_state["quiz_idx"] = 0
                st.session_state["quiz_score"] = 0
                st.session_state["quiz_answered"] = []
                st.rerun()

    # TAB 4: CONCEPTOS
    with tab4:
        st.markdown("### 💡 Conceptos clave")
        conceptos = c["conceptos_clave"]
        pills_html = "".join([f'<span class="concept-pill">✦ {c}</span>' for c in conceptos])
        st.markdown(f'<div class="card">{pills_html}</div>', unsafe_allow_html=True)

else:
    # Estado vacío
    with tab1:
        st.markdown("""
        <div class="card" style="text-align:center; padding:3rem;">
            <p style="font-size:3rem;">📂</p>
            <p style="font-family:Syne; font-size:1.2rem; color:#a78bfa;">Cargá tu material para comenzar</p>
            <p style="color:#6b7280;">Subí un PDF, Word, foto de apunte o pegá texto en el panel izquierdo y hacé clic en "Analizar material"</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        st.info("Primero analizá un material para ver las flashcards.")
    with tab3:
        st.info("Primero analizá un material para hacer el quiz.")
    with tab4:
        st.info("Primero analizá un material para ver los conceptos.")
