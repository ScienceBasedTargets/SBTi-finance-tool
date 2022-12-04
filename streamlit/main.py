from streamlit.web import bootstrap
import os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "app.py")

bootstrap.run(filename, "", [], {})