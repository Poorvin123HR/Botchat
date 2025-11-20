import streamlit as st
import streamlit.components.v1 as components

# Read the HTML file
with open("1.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Wrap HTML in a full‑screen container
full_html = f"""
<html>
  <head>
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
      }}
      iframe {{
        border: none;
        width: 100%;
        height: 100%;
      }}
    </style>
  </head>
  <body>
    {html_content}
  </body>
</html>
"""

# Render with a large height so it fills the page
components.html(full_html, height=800, scrolling=True)
