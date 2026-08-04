
# 🔋 LiionDB

### **→ Browse the database live at [liiondb.com](https://liiondb.com) ←**

[![Open app](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://liiondb.com)

LiionDB is an open database of DFN-type (Doyle–Fuller–Newman) lithium-ion battery model parameters, curated from literature, that accompanies the review manuscript: [Review of parameterisation and a novel database (LiionDB) for continuum Li-ion battery models.](https://iopscience.iop.org/article/10.1088/2516-1083/ac692c/meta)

If you use LiionDB in your work, please cite our paper at: [https://doi.org/10.1088/2516-1083/ac692c](https://doi.org/10.1088/2516-1083/ac692c)

> **📢 2026 update:** the original Azure PostgreSQL server has been retired. The full database now ships **inside this repository** as a single SQLite file — [`database/dfndb.sqlite`](database/dfndb.sqlite) (~0.5 MB, 915 datasets, 83 papers). Cloning the repo gives you the complete dataset with no server, no credentials, and no internet connection required.

There are three ways to use LiionDB:

---
### 1. 🌐 Web app (no install)

The interactive Parameter Dashboard (browse, plot, and download parameters) runs on Streamlit Community Cloud:

**→ [liiondb.com](https://liiondb.com)** (mirrored at [liiondb.streamlit.app](https://liiondb.streamlit.app))

---
### 2. 🐍 Python / SQL (for your own analysis)

Clone the repo and query the bundled database directly — `fn_db.liiondb()` returns a SQLAlchemy engine connected to the local SQLite file, and all documented SQL (including `lower()`/`upper()` range queries) works unchanged:

```python
import pandas as pd
import liiondb.functions.fn_db as fn_db

dfndb, db_connection = fn_db.liiondb()
df = pd.read_sql('SELECT * FROM parameter', dfndb)
```

Guided examples via Google Colab notebooks:

1. [Example LiionDB queries](https://colab.research.google.com/github/ndrewwang/liiondb/blob/main/python%20notebooks/1_Example_Queries.ipynb)
2. [Plotting parameter comparisons](https://colab.research.google.com/github/ndrewwang/liiondb/blob/main/python%20notebooks/2_Parameter_Plotter.ipynb)

Prefer raw SQL? The file at `database/dfndb.sqlite` opens with any SQLite client (`sqlite3`, DBeaver, Datasette, ...). The schema diagram is in [`docs`](streamlit_gui/media/liiondb_erd.png).

---
### 3. 💻 Run the GUI locally

```bash
git clone https://github.com/ndrewwang/liiondb.git
cd liiondb
pip install -r requirements.txt
streamlit run liiondb.py
```

A Dockerfile is also provided: `docker build -t liiondb . && docker run -p 8501:8501 liiondb`

#### Hosting your own copy
The public app is deployed on [Streamlit Community Cloud](https://share.streamlit.io) (free): sign in with GitHub → New app → pick this repo, branch `main`, main file `liiondb.py`. The GitHub Pages site in [`docs/`](docs/) wraps the app for the `liiondb.com` domain.

---
### 🤝 Contributing

- Found an issue or want to add parameter data? Open a [GitHub issue](https://github.com/ndrewwang/liiondb/issues).
- The `#param-database` channel on the [PyBaMM Slack](https://pybamm.slack.com) ([how to join](https://www.pybamm.org/contact)).

---
### Acknowledgements

 - Supported by the [Multi-Scale Modelling](https://www.faraday.ac.uk/research/lithium-ion/battery-system-modelling/) project within [The Faraday Institution](https://www.faraday.ac.uk/)

[![DOI](https://zenodo.org/badge/394467534.svg)](https://zenodo.org/badge/latestdoi/394467534)
