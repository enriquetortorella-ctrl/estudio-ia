import streamlit as st
from groq import Groq
from supabase import create_client
import pdfplumber
import docx
import json
import random
from PIL import Image
import io
import os
import base64

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EstudioIA - UNLa",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

MATERIAS = {
    "📚 Primer Año": [
        "01 - Introducción a Economía Empresarial",
        "02 - Historia Económica Contemporánea",
        "03 - Contabilidad",
        "04 - Matemática I",
        "05 - Taller de Comunicación y Producción de Textos",
        "06 - Empresa, Economía y Sociedad",
        "07 - Organización y Gestión",
        "08 - Matemática II",
        "09 - Derecho Comercial",
        "35 - Seminario de Justicia y Derechos Humanos",
    ],
    "📚 Segundo Año": [
        "10 - Microeconomía I",
        "11 - Cálculo Financiero",
        "12 - Comercialización",
        "13 - Costos Empresariales",
        "36 - Seminario de Pensamiento Nacional Latinoamericano",
        "14 - Control de Gestión",
        "15 - Estadística",
        "16 - Microeconomía II",
        "17 - Macroeconomía",
        "18 - Taller de Práctica Preprofesional",
    ],
    "📚 Tercer Año": [
        "19 - Plan de Negocios",
        "20 - Organización de la Producción y la Tecnología",
        "21 - Formulación de Proyectos de Inversión",
        "22 - Economía Bancaria y Financiera",
        "37 - Seminario Optativo 1",
        "23 - Evaluación de Proyectos de Inversión",
        "24 - Relaciones Laborales",
        "25 - Sistemas de Organización",
        "26 - Principios de Tributación",
        "38 - Seminario Optativo 2",
    ],
    "📚 Cuarto Año": [
        "27 - Financiamiento",
        "28 - Tecnología y Ciencia de Datos",
        "29 - Taller de Proyecto Empresarial",
        "30 - Planeamiento Estratégico",
        "39 - Seminario Optativo 3",
        "31 - Política Económica",
        "32 - Inteligencia de Negocio",
        "33 - Comercio Exterior",
        "34 - Inglés I",
        "40 - Seminario Optativo 4",
    ],
}

# ─── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; }
.stApp { background-color: #0f0f13; }
section[data-testid="stSidebar"] { background-color: #16161e; border-right: 1px solid #2a2a3a; }
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1; margin-bottom: 0.3rem;
}
.hero-sub { color: #6b7280; font-size: 0.95rem; margin-bottom: 1.5rem; }
.materia-badge {
    display: inline-block; background: linear-gradient(135deg, #3b1f6e, #1f3b6e);
    border: 1px solid #a78bfa44; border-radius: 10px; padding: 0.4rem 1rem;
    font-size: 0.85rem; color: #c4b5fd; margin-bottom: 1rem;
    font-family: 'Syne', sans-serif; font-weight: 700;
}
.saved-banner {
    background: linear-gradient(135deg, #0f2a1a, #0a1f2e);
    border: 1px solid #34d39966; border-radius: 12px;
    padding: 0.8rem 1.2rem; margin-bottom: 1rem; font-size: 0.85rem; color: #6ee7b7;
}
.card { background: #16161e; border: 1px solid #2a2a3a; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; color: #e8e8f0; }
.flashcard {
    background: linear-gradient(135deg, #1e1e2e, #16213e); border: 1px solid #3b3b5c;
    border-radius: 20px; padding: 2.5rem; text-align: center; min-height: 180px;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin: 1rem 0; color: #e8e8f0;
}
.badge { display: inline-block; background: #1e1e2e; border: 1px solid #3b3b5c; border-radius: 999px; padding: 0.2rem 0.8rem; font-size: 0.75rem; color: #a78bfa; margin: 0.2rem; }
.concept-pill { display: inline-block; background: linear-gradient(135deg, #1e1e2e, #16213e); border: 1px solid #3b3b5c; border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.85rem; color: #60a5fa; margin: 0.3rem; }
.score-box { background: linear-gradient(135deg, #1a2a1a, #0f1f0f); border: 1px solid #34d399; border-radius: 16px; padding: 1.5rem; text-align: center; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5); color: white; border: none; border-radius: 10px; font-family: 'Syne', sans-serif; font-weight: 700; padding: 0.6rem 1.5rem; transition: all 0.2s; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(124,58,237,0.4); }
.stTextArea textarea { background: #16161e !important; border: 1px solid #2a2a3a !important; color: #e8e8f0 !important; border-radius: 10px !important; }
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #60a5fa); }
p, li { color: #e8e8f0; }
hr { border-color: #2a2a3a; }
</style>
""", unsafe_allow_html=True)

# ─── CLIENTES ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_clients():
    groq_key = st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    sb_url = st.secrets.get("SUPABASE_URL", "") or os.environ.get("SUPABASE_URL", "")
    sb_key = st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    groq = Groq(api_key=groq_key) if groq_key else None
    sb = create_client(sb_url, sb_key) if sb_url and sb_key else None
    return groq, sb

# ─── SUPABASE: cargar y guardar ───────────────────────────────────────────────
def cargar_compartido(sb, materia):
    try:
        r = sb.table("material_compartido").select("contenido, subido_por, updated_at").eq("materia", materia).execute()
        if r.data:
            return r.data[0]
    except:
        pass
    return None

def guardar_compartido(sb, materia, contenido, usuario):
    try:
        sb.table("material_compartido").upsert({
            "materia": materia, "contenido": contenido,
            "subido_por": usuario, "updated_at": "now()"
        }, on_conflict="materia").execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar compartido: {e}")
        return False

def cargar_personal(sb, usuario, materia):
    try:
        r = sb.table("historial_personal").select("contenido").eq("usuario", usuario).eq("materia", materia).execute()
        if r.data:
            return r.data[0]["contenido"]
    except:
        pass
    return None

def guardar_personal(sb, usuario, materia, contenido):
    try:
        sb.table("historial_personal").upsert({
            "usuario": usuario, "materia": materia, "contenido": contenido
        }, on_conflict="usuario,materia").execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar personal: {e}")
        return False

def listar_materias_guardadas(sb, usuario):
    compartidas, personales = [], []
    try:
        r = sb.table("material_compartido").select("materia, subido_por, updated_at").execute()
        compartidas = r.data or []
    except: pass
    try:
        r = sb.table("historial_personal").select("materia").eq("usuario", usuario).execute()
        personales = [x["materia"] for x in (r.data or [])]
    except: pass
    return compartidas, personales

# ─── EXTRACCIÓN ───────────────────────────────────────────────────────────────
def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    return text

def extract_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_image(file, groq):
    img = Image.open(file)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    r = groq.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "Transcribí todo el texto de este apunte fielmente."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        ]}], max_tokens=4000
    )
    return r.choices[0].message.content

def process_files(files, groq):
    combined = ""
    for i, f in enumerate(files):
        st.write(f"  📄 `{f.name}`...")
        try:
            if f.name.endswith(".pdf"): text = extract_pdf(f)
            elif f.name.endswith(".docx"): text = extract_docx(f)
            else: text = extract_image(f, groq)
            combined += f"\n\n=== ARCHIVO {i+1}: {f.name} ===\n{text}"
        except Exception as e:
            st.warning(f"No se pudo procesar {f.name}: {e}")
    return combined

# ─── IA ───────────────────────────────────────────────────────────────────────
def generate_content(text, materia, groq):
    # LLAMADA 1: Resumen extenso
    prompt_resumen = f"""Sos un profesor universitario experto en "{materia}".
Escribí un RESUMEN MUY COMPLETO Y DETALLADO del siguiente material de estudio.
Desarrollá TODOS los temas en profundidad con ejemplos concretos.
Para cada tema escribí varios párrafos explicando el concepto, su importancia y aplicación práctica.
El resumen debe ser tan completo que el estudiante no necesite releer el original.
Escribí solo el resumen en texto plano, sin títulos especiales ni formato JSON.

MATERIAL:
{text[:14000]}"""

    r1 = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt_resumen}],
        max_tokens=3000, temperature=0.3
    )
    resumen = r1.choices[0].message.content.strip()

    # LLAMADA 2: Flashcards, quiz y conceptos
    prompt_estudio = f"""Sos un profesor universitario experto en "{materia}".
Analizá el siguiente material y respondé ÚNICAMENTE con JSON válido, sin texto extra:
{{
  "conceptos_clave": ["CONCEPTO: definición clara y completa"],
  "flashcards": [{{"pregunta": "¿Pregunta específica?", "respuesta": "Respuesta completa con ejemplos en 2-3 oraciones."}}],
  "quiz": [{{"pregunta": "¿Pregunta?", "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."], "correcta": "A) ...", "explicacion": "Por qué es correcta y por qué las otras no."}}]
}}

REQUISITOS:
- conceptos_clave: exactamente 8 ítems
- flashcards: exactamente 10 ítems
- quiz: exactamente 6 ítems

MATERIAL DE {materia}:
{text[:10000]}"""

    r2 = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt_estudio}],
        max_tokens=3000, temperature=0.3
    )
    raw = r2.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    estudio = json.loads(raw.strip())
    estudio["resumen"] = resumen
    return estudio

# ─── RENDER CONTENIDO ─────────────────────────────────────────────────────────
def render_content(c, tab1, tab2, tab3, tab4):
    with tab1:
        st.markdown("### 📋 Resumen")
        st.markdown(f'<div class="card">{c["resumen"]}</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🃏 Flashcards")
        cards = c["flashcards"]
        total = len(cards)
        idx = st.session_state.get("flash_idx", 0)
        show = st.session_state.get("flash_show_answer", False)
        st.progress((idx + 1) / total)
        st.markdown(f'<p style="color:#6b7280;text-align:center;">{idx+1} / {total}</p>', unsafe_allow_html=True)
        content_html = cards[idx]["pregunta"] if not show else cards[idx]["respuesta"]
        label = "PREGUNTA" if not show else "RESPUESTA"
        st.markdown(f'<div class="flashcard"><div><span class="badge">{label}</span><br><br>{content_html}</div></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                st.session_state["flash_idx"] = max(0, idx - 1)
                st.session_state["flash_show_answer"] = False
                st.rerun()
        with col2:
            if st.button("👁️ Ver resp." if not show else "🙈 Ocultar", use_container_width=True):
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

    with tab3:
        st.markdown("### 🧪 Quiz")
        quiz = c["quiz"]
        total_q = len(quiz)
        q_idx = st.session_state.get("quiz_idx", 0)
        answered = st.session_state.get("quiz_answered", [])
        if q_idx < total_q:
            q = quiz[q_idx]
            st.progress(q_idx / total_q)
            st.markdown(f'<p style="color:#6b7280;">Pregunta {q_idx+1} de {total_q} · Puntaje: {st.session_state.get("quiz_score",0)}/{q_idx}</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="card"><b>{q["pregunta"]}</b></div>', unsafe_allow_html=True)
            if q_idx not in [a["idx"] for a in answered]:
                selected = st.radio("Elegí tu respuesta:", q["opciones"], key=f"quiz_{q_idx}")
                if st.button("✅ Confirmar", use_container_width=True):
                    correct = selected == q["correcta"]
                    if correct:
                        st.session_state["quiz_score"] = st.session_state.get("quiz_score", 0) + 1
                        st.success("🎉 ¡Correcto!")
                    else:
                        st.error(f"❌ Era: **{q['correcta']}**")
                    st.info(f"💡 {q['explicacion']}")
                    st.session_state["quiz_answered"].append({"idx": q_idx, "correct": correct})
                    st.session_state["quiz_idx"] += 1
                    st.rerun()
            else:
                if st.button("➡️ Siguiente", use_container_width=True):
                    st.session_state["quiz_idx"] += 1
                    st.rerun()
        else:
            score = st.session_state.get("quiz_score", 0)
            pct = int(score / total_q * 100)
            emoji = "🏆" if pct >= 80 else "📚" if pct >= 50 else "💪"
            st.markdown(f'<div class="score-box"><p style="font-size:3rem;">{emoji}</p><p style="font-family:Syne;font-size:2rem;font-weight:800;color:#34d399;">{pct}%</p><p style="color:#6b7280;">{score} de {total_q} correctas</p></div>', unsafe_allow_html=True)
            if st.button("🔄 Reiniciar quiz", use_container_width=True):
                st.session_state.update({"quiz_idx": 0, "quiz_score": 0, "quiz_answered": []})
                st.rerun()

    with tab4:
        st.markdown("### 💡 Conceptos clave")
        pills = "".join([f'<span class="concept-pill">✦ {con}</span>' for con in c["conceptos_clave"]])
        st.markdown(f'<div class="card">{pills}</div>', unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:Syne;font-size:1.4rem;font-weight:800;color:#a78bfa;">🧠 EstudioIA</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b7280;font-size:0.75rem;">UNLa · Economía Empresarial</p>', unsafe_allow_html=True)
    st.divider()

    usuario = st.text_input("👤 Tu nombre:", placeholder="ej: Enrique", help="Para guardar tu historial personal")

    st.divider()
    st.markdown("**🎓 Seleccioná tu materia**")
    anio = st.selectbox("Año:", list(MATERIAS.keys()))
    materia = st.selectbox("Materia:", MATERIAS[anio])

    st.divider()
    st.markdown("**📂 Nuevo material**")
    input_method = st.radio("Tipo:", ["📄 PDF / Word / Imagen", "✏️ Texto directo"])
    uploaded_files = []
    pasted_text = ""
    if input_method == "📄 PDF / Word / Imagen":
        uploaded_files = st.file_uploader("Subí tus archivos", type=["pdf","docx","png","jpg","jpeg","webp"], accept_multiple_files=True)
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} archivo(s)")
    else:
        pasted_text = st.text_area("Pegá tu texto:", height=150)

    st.divider()
    analizar = st.button("🚀 Analizar y guardar", use_container_width=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">EstudioIA</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">UNLa · Economía Empresarial · Material guardado en la nube</div>', unsafe_allow_html=True)

groq, sb = get_clients()
if not groq:
    st.error("Falta GROQ_API_KEY en los secrets.")
    st.stop()
if not sb:
    st.error("Faltan SUPABASE_URL y SUPABASE_KEY en los secrets.")
    st.stop()

if not usuario:
    st.info("👈 Ingresá tu nombre en el panel izquierdo para empezar.")
    st.stop()

st.markdown(f'<div class="materia-badge">🎓 {materia}</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Resumen", "🃏 Flashcards", "🧪 Quiz", "💡 Conceptos"])

# ─── BUSCAR MATERIAL GUARDADO ─────────────────────────────────────────────────
compartido = cargar_compartido(sb, materia)
personal = cargar_personal(sb, usuario, materia)

# Opciones de carga si hay guardado
if not analizar and not st.session_state.get("content"):
    if compartido or personal:
        st.markdown("### 💾 Material guardado encontrado")
        opciones = []
        if personal:
            opciones.append("📁 Mi material personal")
        if compartido:
            opciones.append(f"🌐 Material compartido (subido por {compartido['subido_por']})")
        opciones.append("📤 Subir nuevo material")

        eleccion = st.radio("¿Qué querés usar?", opciones, horizontal=True)

        if st.button("▶️ Usar este material", use_container_width=False):
            if "personal" in eleccion:
                st.session_state["content"] = personal
            elif "compartido" in eleccion:
                st.session_state["content"] = compartido["contenido"]
            st.session_state.update({"quiz_idx": 0, "quiz_score": 0, "quiz_answered": [], "flash_idx": 0, "flash_show_answer": False})
            st.rerun()
    else:
        with tab1:
            st.markdown('<div class="card" style="text-align:center;padding:3rem;"><p style="font-size:3rem;">📂</p><p style="font-family:Syne;font-size:1.2rem;color:#a78bfa;">No hay material guardado para esta materia</p><p style="color:#6b7280;">Subí archivos o pegá texto en el panel izquierdo.</p></div>', unsafe_allow_html=True)

# ─── PROCESAR NUEVO MATERIAL ──────────────────────────────────────────────────
if analizar:
    text = ""
    with st.spinner("Extrayendo texto..."):
        try:
            if uploaded_files:
                text = process_files(uploaded_files, groq)
            elif pasted_text:
                text = pasted_text
            if not text.strip():
                st.error("No se encontró texto.")
                st.stop()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    with st.spinner(f"🤖 Analizando {materia}..."):
        try:
            content = generate_content(text, materia, groq)

            # Guardar en ambos lados
            guardar_personal(sb, usuario, materia, content)
            guardar_compartido(sb, materia, content, usuario)

            st.session_state["content"] = content
            st.session_state.update({"quiz_idx": 0, "quiz_score": 0, "quiz_answered": [], "flash_idx": 0, "flash_show_answer": False})
            st.success(f"✅ ¡Listo! Material guardado para vos y para todos.")
        except Exception as e:
            st.error(f"Error al generar: {e}")
            st.stop()

# ─── MOSTRAR CONTENIDO ────────────────────────────────────────────────────────
if "content" in st.session_state:
    render_content(st.session_state["content"], tab1, tab2, tab3, tab4)
