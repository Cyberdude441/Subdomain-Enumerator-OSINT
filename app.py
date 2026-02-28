from flask import Flask, request, render_template
import requests

app = Flask(__name__)

def clean_domain(domain):
    domain = domain.strip().lower()
    domain = domain.replace("http://", "").replace("https://", "")
    domain = domain.split("/")[0]
    return domain

def get_subdomains(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print("Bad response:", response.status_code)
            return []

        data = response.json()

        subdomains = set()

        for entry in data:
            name_value = entry.get("name_value", "")

            for sub in name_value.split("\n"):
                sub = sub.strip().lower()

                if not sub:
                    continue

                if "*" in sub:
                    continue

                subdomains.add(sub)

        print("FLASK COUNT:", len(subdomains))  # Debug

        return sorted(subdomains)

    except Exception as e:
        print("ERROR:", e)
        return []

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    count = 0

    if request.method == "POST":
        domain = request.form.get("domain")
        if domain:
            domain = clean_domain(domain)
            results = get_subdomains(domain)
            count = len(results)

    return render_template("index.html", results=results, count=count)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
