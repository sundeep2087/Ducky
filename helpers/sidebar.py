import streamlit as st


def show() -> None:
    with st.sidebar:
        st.markdown("""
            <style>
                .sidebar-header {
                    margin-botton: 30px;  /* Adjust margin as needed */
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="sidebar-header">
			<a href="/" style="color:black;text-decoration: none">
				<div style="display:table;margin-top:-23rem;margin-left:0%;">
					<img src="/app/static/logo.jpeg" width="45">
					<span style="font-size: 1.0em; color: orange; padding-left: 20px">Ducky</span>
					<span style="font-size: 0.8em; color: grey">&nbsp;&nbsp;v0.1.3</span>
				</div>
			</a>
			</div>
			<br>
			""", unsafe_allow_html=True
        )

        reload_button = st.button("↪︎ Reload Page")
        if reload_button:
            st.session_state.clear()
            st.rerun()
