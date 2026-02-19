"""
╔══════════════════════════════════════════════════════════════╗
║         Mobile Calculator Web App — Android/iPhone Style     ║
║         Built with Python + Streamlit                        ║
║         Version : 1.0.0                                      ║
╚══════════════════════════════════════════════════════════════╝

Run locally:
  pip install -r requirements.txt
  streamlit run app.py
"""

import streamlit as st

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the first Streamlit call)
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Calculator",
    page_icon="🔢",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# SESSION STATE — initialise once per session
# ══════════════════════════════════════════════════════════════
def init_state() -> None:
    defaults = {
        "expression":     "",
        "display":        "0",
        "history":        [],
        "dark_mode":      True,
        "just_evaluated": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ══════════════════════════════════════════════════════════════
# THEME PALETTES
# ══════════════════════════════════════════════════════════════
DARK = {
    "bg":           "#1a1a2e",
    "calc_bg":      "#16213e",
    "display_bg":   "#0f3460",
    "display_text": "#e0e0e0",
    "num_bg":       "#2a2a3e",
    "num_hover":    "#3a3a5e",
    "op_bg":        "#e07b39",
    "op_hover":     "#f09050",
    "eq_bg":        "#27ae60",
    "eq_hover":     "#2ecc71",
    "ac_bg":        "#c0392b",
    "ac_hover":     "#e74c3c",
    "text":         "#ffffff",
    "history_bg":   "#0d1b2a",
    "shadow":       "rgba(0,0,0,0.6)",
}

LIGHT = {
    "bg":           "#f0f4f8",
    "calc_bg":      "#ffffff",
    "display_bg":   "#e8edf2",
    "display_text": "#1a1a2e",
    "num_bg":       "#dde3ea",
    "num_hover":    "#c8d0da",
    "op_bg":        "#e07b39",
    "op_hover":     "#f09050",
    "eq_bg":        "#27ae60",
    "eq_hover":     "#2ecc71",
    "ac_bg":        "#c0392b",
    "ac_hover":     "#e74c3c",
    "text":         "#1a1a2e",
    "history_bg":   "#e8edf2",
    "shadow":       "rgba(0,0,0,0.15)",
}

C = DARK if st.session_state.dark_mode else LIGHT

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');

  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {C['bg']} !important;
  }}
  [data-testid="stSidebar"] {{
      background-color: {C['history_bg']} !important;
  }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding: 1rem 1rem 0 1rem !important; }}

  .calc-body {{
      background: {C['calc_bg']};
      border-radius: 28px;
      padding: 22px 18px 28px 18px;
      width: 340px;
      box-shadow: 0 20px 60px {C['shadow']}, 0 0 0 1px rgba(255,255,255,0.05);
  }}
  .calc-display {{
      background: {C['display_bg']};
      border-radius: 16px;
      padding: 14px 20px 10px 20px;
      margin-bottom: 18px;
      min-height: 90px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      align-items: flex-end;
      box-shadow: inset 0 4px 12px rgba(0,0,0,0.3);
  }}
  .expr-text {{
      font-family: 'Share Tech Mono', monospace;
      font-size: 13px;
      color: {C['display_text']};
      opacity: 0.55;
      min-height: 18px;
      word-break: break-all;
      text-align: right;
  }}
  .display-number {{
      font-family: 'Orbitron', monospace;
      font-size: 38px;
      font-weight: 700;
      color: {C['display_text']};
      letter-spacing: -1px;
      text-align: right;
      word-break: break-all;
      line-height: 1.1;
  }}
  div[data-testid="column"] > div > div > div > button {{
      width: 100% !important;
      border-radius: 14px !important;
      height: 68px !important;
      font-family: 'Share Tech Mono', monospace !important;
      font-size: 20px !important;
      font-weight: 600 !important;
      border: none !important;
      box-shadow: 0 4px 10px rgba(0,0,0,0.25) !important;
      transition: transform 0.08s ease, filter 0.1s ease !important;
      letter-spacing: 0.5px !important;
  }}
  div[data-testid="column"] > div > div > div > button:active {{
      transform: scale(0.91) !important;
      filter: brightness(1.3) !important;
      box-shadow: 0 1px 4px rgba(0,0,0,0.2) !important;
  }}
  .hist-title {{
      font-family: 'Orbitron', monospace;
      font-size: 15px;
      color: {C['display_text']};
      margin-bottom: 12px;
      letter-spacing: 1px;
      opacity: 0.8;
  }}
  .hist-item {{
      font-family: 'Share Tech Mono', monospace;
      font-size: 13px;
      color: {C['display_text']};
      opacity: 0.7;
      padding: 8px 10px;
      border-radius: 8px;
      margin-bottom: 6px;
      background: rgba(255,255,255,0.05);
      border-left: 3px solid {C['op_bg']};
      word-break: break-all;
  }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CALCULATOR LOGIC
# ══════════════════════════════════════════════════════════════

def safe_eval(expr: str) -> str:
    """Safely evaluate a calculator expression string."""
    try:
        sanitised = (
            expr
            .replace("×", "*")
            .replace("÷", "/")
            .replace("%", "/100")
        )
        result = eval(sanitised, {"__builtins__": {}})
        if isinstance(result, float):
            if result == int(result):
                return str(int(result))
            return f"{result:.10g}"
        return str(result)
    except ZeroDivisionError:
        return "Error: ÷ 0"
    except Exception:
        return "Error"


def handle_button(label: str) -> None:
    """Handle a calculator button press and update session state."""
    expr      = st.session_state.expression
    disp      = st.session_state.display
    just_eq   = st.session_state.just_evaluated
    OPERATORS = {"+", "-", "×", "÷"}

    # All-Clear
    if label == "AC":
        st.session_state.expression     = ""
        st.session_state.display        = "0"
        st.session_state.just_evaluated = False
        return

    # Backspace
    if label == "⌫":
        if just_eq:
            st.session_state.expression     = ""
            st.session_state.display        = "0"
            st.session_state.just_evaluated = False
        else:
            expr = expr[:-1]
            st.session_state.expression = expr
            st.session_state.display    = expr if expr else "0"
        return

    # Evaluate
    if label == "=":
        if not expr:
            return
        result = safe_eval(expr)
        if not result.startswith("Error"):
            st.session_state.history.insert(0, f"{expr} = {result}")
            if len(st.session_state.history) > 20:
                st.session_state.history.pop()
        st.session_state.display        = result
        st.session_state.expression     = result if not result.startswith("Error") else ""
        st.session_state.just_evaluated = True
        return

    # Percentage
    if label == "%":
        if expr:
            result = safe_eval(expr + "/100")
            st.session_state.expression     = result
            st.session_state.display        = result
            st.session_state.just_evaluated = True
        return

    # Toggle sign
    if label == "±":
        if disp not in ("0", "Error: ÷ 0", "Error"):
            if disp.startswith("-"):
                st.session_state.display    = disp[1:]
                st.session_state.expression = expr[1:]
            else:
                st.session_state.display    = "-" + disp
                st.session_state.expression = "-" + expr
        return

    # Operator right after evaluation → continue from result
    if just_eq and label in OPERATORS:
        st.session_state.expression     = st.session_state.display + label
        st.session_state.display        = st.session_state.display + label
        st.session_state.just_evaluated = False
        return

    # New number right after evaluation → start fresh
    if just_eq and label not in OPERATORS:
        expr = ""
        st.session_state.just_evaluated = False

    # Guard: no two operators in a row
    if label in OPERATORS and expr and expr[-1] in OPERATORS:
        expr = expr[:-1]

    # Guard: no two decimals in same number segment
    if label == ".":
        current_segment = ""
        for ch in expr:
            if ch in "+-×÷":
                current_segment = ""
            else:
                current_segment += ch
        if "." in current_segment:
            return

    expr += label
    st.session_state.expression = expr
    st.session_state.display    = expr


# ══════════════════════════════════════════════════════════════
# SIDEBAR — History & Theme Toggle
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="hist-title">⏱ HISTORY</div>', unsafe_allow_html=True)

    theme_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.button(theme_label, key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.divider()

    if st.session_state.history:
        if st.button("🗑 Clear History", key="clear_hist"):
            st.session_state.history = []
            st.rerun()
        for item in st.session_state.history:
            st.markdown(f'<div class="hist-item">{item}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="hist-item" style="opacity:0.4;">No history yet.</div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════
# MAIN UI — Display Screen
# ══════════════════════════════════════════════════════════════
expr_preview = st.session_state.expression if not st.session_state.just_evaluated else ""

st.markdown(f"""
<div style="display:flex; justify-content:center; padding:10px 0 0 0;">
  <div class="calc-body">
    <div class="calc-display">
      <div class="expr-text">{expr_preview}</div>
      <div class="display-number">{st.session_state.display}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN UI — Button Grid
#
#  ┌────┬────┬────┬────┐
#  │ AC │ ±  │ %  │ ÷  │
#  ├────┼────┼────┼────┤
#  │  7 │  8 │  9 │ ×  │
#  ├────┼────┼────┼────┤
#  │  4 │  5 │  6 │ −  │
#  ├────┼────┼────┼────┤
#  │  1 │  2 │  3 │ +  │
#  ├────┼────┼────┼────┤
#  │ ⌫  │  0 │  . │ =  │
#  └────┴────┴────┴────┘
# ══════════════════════════════════════════════════════════════

BUTTON_ROWS = [
    [("AC", "ac"), ("±",  "num"), ("%", "num"), ("÷", "op")],
    [("7",  "num"), ("8",  "num"), ("9", "num"), ("×", "op")],
    [("4",  "num"), ("5",  "num"), ("6", "num"), ("−", "op")],
    [("1",  "num"), ("2",  "num"), ("3", "num"), ("+", "op")],
    [("⌫",  "ac"), ("0",  "num"), (".", "num"), ("=", "eq")],
]

BTN_COLORS = {
    "num": (C["num_bg"], C["num_hover"]),
    "op":  (C["op_bg"],  C["op_hover"]),
    "eq":  (C["eq_bg"],  C["eq_hover"]),
    "ac":  (C["ac_bg"],  C["ac_hover"]),
}

for row in BUTTON_ROWS:
    cols = st.columns(4, gap="small")
    for col, (label, btn_type) in zip(cols, row):
        bg, hover = BTN_COLORS[btn_type]
        key = f"btn_{label}"
        with col:
            st.markdown(f"""
            <style>
            button[data-testid="baseButton-secondary"][aria-label="{label}"] {{
                background: {bg} !important;
                color: #ffffff !important;
                border: none !important;
            }}
            button[data-testid="baseButton-secondary"][aria-label="{label}"]:hover {{
                background: {hover} !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            if st.button(label, key=key, use_container_width=True):
                handle_button(label.replace("−", "-"))
                st.rerun()

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;
            font-family:'Share Tech Mono',monospace;
            font-size:11px;
            color:{C['display_text']};
            opacity:0.3;
            margin-top:18px;">
  CALC v1.0.0 · Python + Streamlit · MIT License
</div>
""", unsafe_allow_html=True)
