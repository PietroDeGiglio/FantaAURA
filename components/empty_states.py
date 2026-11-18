import streamlit as st

def render_empty_leagues():
    st.markdown("""
        <div style="text-align: center; padding: 50px 20px; background-color: #0D0D0D; border: 1px dashed #1A1A1A; border-radius: 12px; margin-top: 20px;">
            <h3 style="color: #888;">Nessuna lega ancora.</h3>
            <p style="color: #666; margin-bottom: 0;">La tua AURA inizia con la tua prima lega.</p>
        </div>
    """, unsafe_allow_html=True)

def render_empty_roster():
    st.markdown("""
        <div style="text-align: center; padding: 40px; background-color: #0D0D0D; border-radius: 12px; border: 1px solid #1A1A1A;">
            <p style="color: #A0A0A0; font-size: 1.1rem; margin: 0;">La tua rosa verrà costruita durante l'asta.</p>
        </div>
    """, unsafe_allow_html=True)