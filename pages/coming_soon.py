import streamlit as st

def show():
    st.markdown("""
        <div style="text-align: center; padding: 100px 20px;">
            <h1 style="color: #D4AF37; font-size: 3rem; margin-bottom: 10px;">COMING SOON</h1>
            <p style="color: #888; font-size: 1.2rem;">Questo modulo è in fase di sviluppo.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Torna alla Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()