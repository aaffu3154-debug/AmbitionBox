from flask import Flask, render_template, request
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
DATA_DIR = "data"


def load_all_data():
    frames = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(DATA_DIR, file))

            if "city" not in df.columns:
                df["city"] = file.replace(".csv", "").title()

            frames.append(df)

    return pd.concat(frames, ignore_index=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():
    city = request.args.get("city", "All")
    field = request.args.get("field", "All")
    rating = request.args.get("rating")
    salary = request.args.get("salary")
    output = request.args.get("output", "table")

    df = load_all_data()

    # numeric safety
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

    # flexible filtering
    if city != "All":
        df = df[df["city"].str.contains(city, case=False, na=False)]

    if field != "All":
        df = df[df["field"].str.contains(field, case=False, na=False)]

    if rating:
        df = df[df["rating"] >= float(rating)]

    if salary:
        df = df[df["salary"] >= float(salary)]

    if output == "visual":
        return visualize()

    return render_template(
        "data.html",
        companies=df.to_dict(orient="records")
    )


@app.route("/visualize")
def visualize():
    df = load_all_data()

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

    # extract company age
    df["company_age"] = (
        df["founded_in"]
        .astype(str)
        .str.extract(r'(\d+)\s*yrs')
        .astype(float)
    )

    fig1 = px.histogram(df, x="rating", title="Distribution of Ratings")
    fig2 = px.scatter(df, x="salary", y="rating", title="Salary vs Rating")
    fig3 = px.histogram(df, x="company_age", title="Company Age Distribution")
    fig4 = px.scatter(df, x="company_age", y="rating",
                      title="Company Age vs Rating")

    return render_template(
        "visualize.html",
        fig1=pio.to_html(fig1, full_html=False),
        fig2=pio.to_html(fig2, full_html=False),
        fig3=pio.to_html(fig3, full_html=False),
        fig4=pio.to_html(fig4, full_html=False),
    )


if __name__ == "__main__":
    app.run(debug=True)
