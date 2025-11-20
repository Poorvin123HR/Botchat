# import streamlit as st
#import streamlit.components.v1 as components
# Load your HTML file that contains JS
#with open("1.html", "r", encoding="utf-8") as f:
    html_code = f.read()
# Render it inside Streamlit
components.html(html_code, height=600, scrolling=True)

import streamlit as st
import streamlit.components.v1 as components

# Path to your HTML file
file_path = r"1.html"

with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Render inside Streamlit
components.html(html_content, height=600, scrolling=True)
