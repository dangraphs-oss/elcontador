import html

import streamlit as st
from supabase import create_client

PUNTOS = {"2+1": 3, "3+1": 4, "tiro_libre": 1}
ETIQUETAS = {"2+1": "🏀 2+1", "3+1": "🔥 3+1", "tiro_libre": "🎯 Tiro libre"}

st.set_page_config(page_title="Contador", page_icon="🏀", layout="centered")

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 600px;}

.banner {
    background: linear-gradient(135deg, #FF7A1A, #FF4D00);
    border-radius: 20px;
    padding: 18px 22px;
    margin-bottom: 18px;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: 1px;
    color: white;
}
.banner span {display: block; font-size: 0.85rem; font-weight: 500; opacity: 0.85; letter-spacing: 0;}

div.stButton > button {
    height: 3.6rem;
    border-radius: 16px;
    font-weight: 700;
    font-size: 1.05rem;
    border: 2px solid #FF7A1A;
    background: #1B1F2A;
    color: white;
    transition: all 0.15s ease;
}
div.stButton > button:hover {background: #FF7A1A; border-color: #FF7A1A; color: white;}
div.stButton > button:active {transform: scale(0.97);}

.titulo-seccion {font-size: 1.15rem; font-weight: 700; margin: 22px 0 10px 0; color: #FFB347;}

.fila {
    display: flex; align-items: center; gap: 12px;
    background: #1B1F2A; border-radius: 16px;
    padding: 12px 16px; margin-bottom: 10px;
    border: 2px solid transparent;
}
.fila.yo {border-color: #FF7A1A;}
.puesto {font-size: 1.5rem; width: 2.2rem; text-align: center;}
.centro {flex: 1;}
.nombre {font-weight: 700; font-size: 1.05rem;}
.pts {font-weight: 800; font-size: 1.4rem; color: #FF7A1A;}
.pts small {font-size: 0.75rem; color: #9AA0AE; font-weight: 500;}
.barra {height: 6px; border-radius: 3px; background: #2A3040; margin-top: 6px;}
.barra > div {height: 100%; border-radius: 3px; background: linear-gradient(90deg, #FF7A1A, #FFB347);}

.historial {
    display: flex; justify-content: space-between;
    background: #1B1F2A; border-radius: 12px;
    padding: 9px 14px; margin-bottom: 6px; font-size: 0.92rem;
}
.historial .fecha {color: #9AA0AE;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def conectar():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


supabase = conectar()


def cargar_jugadores():
    datos = supabase.table("jugadores").select("nombre").execute().data
    return [d["nombre"] for d in datos]


def cargar_anotaciones():
    return (
        supabase.table("anotaciones")
        .select("id, jugador, tipo, creado_en")
        .order("creado_en", desc=True)
        .execute()
        .data
    )


def anotar(jugador, tipo):
    supabase.table("anotaciones").insert({"jugador": jugador, "tipo": tipo}).execute()


def deshacer(jugador):
    ultima = (
        supabase.table("anotaciones")
        .select("id")
        .eq("jugador", jugador)
        .order("creado_en", desc=True)
        .limit(1)
        .execute()
        .data
    )
    if ultima:
        supabase.table("anotaciones").delete().eq("id", ultima[0]["id"]).execute()
        return True
    return False


# Cabecera
st.markdown(
    '<div class="banner">🏀 CONTADOR<span>El marcador oficial</span></div>',
    unsafe_allow_html=True,
)
with st.expander("📜 Normas y reglas"):
    st.markdown(
        """
**Qué significa cada marcador**

🏀 **2+1 (+3 puntos):** un "check". Un lío con una chica y nada más.

🔥 **3+1 (+4 puntos):** cuando pasa más que un simple lío.

🎯 **Tiro libre (+1 punto):** la jugada en solitario.

**Normas**

1. Cada uno solo apunta lo suyo, con su nombre y su contraseña.
2. **Prohibido hacer trampa.** Solo se apunta lo que ha pasado de verdad.
3. **Todo 2+1 y 3+1 tiene que notificarse al grupo.** Si no se cuenta, no cuenta.
4. El botón de deshacer es solo para corregir errores, no para borrar puntos incómodos.
5. Esto **no es una competición**, es una broma entre amigos... pero a final de año habrá premios. 🏆
"""
    )

jugadores = cargar_jugadores()

# Pantalla de acceso
if "yo" not in st.session_state:
    nombre = st.selectbox("¿Quién eres?", jugadores)
    pin = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        if pin == dict(st.secrets["pins"]).get(nombre):
            st.session_state["yo"] = nombre
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

yo = st.session_state["yo"]
st.write(f"Sesión de **{yo}**")

# Botones (se procesan antes de calcular la clasificación)
col1, col2, col3 = st.columns(3)
if col1.button("2+1  ·  +3", use_container_width=True):
    anotar(yo, "2+1")
    st.toast("¡Anotado!", icon="🏀")
if col2.button("3+1  ·  +4", use_container_width=True):
    anotar(yo, "3+1")
    st.toast("¡Anotado!", icon="🔥")
if col3.button("Tiro libre  ·  +1", use_container_width=True):
    anotar(yo, "tiro_libre")
    st.toast("¡Anotado!", icon="🎯")

if st.button("↩️ Deshacer mi última anotación", use_container_width=True):
    if deshacer(yo):
        st.toast("Anotación borrada", icon="↩️")
    else:
        st.toast("No tienes anotaciones que borrar")

# Clasificación
anotaciones = cargar_anotaciones()
totales = {j: 0 for j in jugadores}
for a in anotaciones:
    totales[a["jugador"]] += PUNTOS[a["tipo"]]

ranking = sorted(totales.items(), key=lambda x: x[1], reverse=True)
maximo = max([p for _, p in ranking] + [1])
medallas = ["🥇", "🥈", "🥉"]

st.markdown('<div class="titulo-seccion">CLASIFICACIÓN</div>', unsafe_allow_html=True)
filas = ""
for i, (nombre_j, puntos) in enumerate(ranking):
    puesto = medallas[i] if i < 3 else f"{i + 1}º"
    clase = "fila yo" if nombre_j == yo else "fila"
    ancho = int(puntos / maximo * 100)
    filas += (
        f'<div class="{clase}">'
        f'<div class="puesto">{puesto}</div>'
        f'<div class="centro"><div class="nombre">{html.escape(nombre_j)}</div>'
        f'<div class="barra"><div style="width:{ancho}%"></div></div></div>'
        f'<div class="pts">{puntos} <small>pts</small></div>'
        f"</div>"
    )
st.markdown(filas, unsafe_allow_html=True)

# Historial
st.markdown('<div class="titulo-seccion">ÚLTIMAS ANOTACIONES</div>', unsafe_allow_html=True)
if not anotaciones:
    st.write("Todavía no hay anotaciones.")
historial = ""
for a in anotaciones[:10]:
    c = a["creado_en"]
    fecha = f"{c[8:10]}/{c[5:7]}"
    historial += (
        f'<div class="historial"><span>{html.escape(a["jugador"])} · {ETIQUETAS[a["tipo"]]}</span>'
        f'<span class="fecha">{fecha}</span></div>'
    )
st.markdown(historial, unsafe_allow_html=True)

# Salir
if st.button("Cerrar sesión", use_container_width=True):
    del st.session_state["yo"]
    st.rerun()