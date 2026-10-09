import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #0b1020;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 1.6rem 1.8rem;
            border: 1px solid #293653;
            border-radius: 18px;
            background: linear-gradient(135deg, #121a2e 0%, #0f172a 100%);
            margin-bottom: 1.2rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 2.25rem;
            color: #f8fafc;
        }

        .hero p {
            margin: .5rem 0 0;
            color: #aebbd1;
            font-size: 1rem;
        }

        .phase-card {
            border: 1px solid #293653;
            border-radius: 14px;
            padding: 1rem;
            text-align: center;
            background: #111827;
            min-height: 110px;
        }

        .phase-number {
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: .08em;
            color: #7dd3fc;
            font-weight: 700;
        }

        .phase-title {
            color: #f8fafc;
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: .35rem;
        }

        .phase-desc {
            color: #94a3b8;
            font-size: .82rem;
            margin-top: .25rem;
        }

        .status-ok {
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #285c45;
            background: #10251d;
            color: #a7f3d0;
            font-weight: 700;
        }

        .status-bad {
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #713b43;
            background: #28151a;
            color: #fecaca;
            font-weight: 700;
        }

        .metric-card {
            border: 1px solid #293653;
            border-radius: 12px;
            padding: .85rem;
            background: #111827;
        }

        .metric-value {
            color: #f8fafc;
            font-size: 1.35rem;
            font-weight: 800;
        }

        .metric-label {
            color: #94a3b8;
            font-size: .78rem;
        }

        div[data-testid="stCodeBlock"] {
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
