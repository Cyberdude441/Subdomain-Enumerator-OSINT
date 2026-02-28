from flask import Flask, render_template, request
import requests
import dns.resolver
import socket
import concurrent.futures

app = Flask(__name__)

COMMON_SUBS = [
    "www","mail","dev","test","staging","api","vpn","portal",
    "admin","beta","internal","secure","prod","uat","backup",
    "shop","blog","m","mobile","cdn","static","support",
    "dashboard","panel","gateway","auth","sso","cloud"
]

# ----------------------------
# CT LOG ENUMERATION
# ----------------------------
def ct_enum(domain):
    found = set()
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        r = requests.get(url, timeout=20)
        data = r.json()

        for entry in data:
            names = entry.get("name_value", "").split("\n")
            for name in names:
                name = name.strip().lower()
                if name.startswith("*."):
                    name = name[2:]
                if domain in name:
                    found.add(name)
    except:
        pass

    return found


# ----------------------------
# DNS BRUTE FORCE
# ----------------------------
def dns_bruteforce(domain):
    found = set()
    resolver = dns.resolver.Resolver()

    def check(sub):
        test_domain = f"{sub}.{domain}"
        try:
            resolver.resolve(test_domain, "A")
            return test_domain
        except:
            return test_domain  # return even if no DNS

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check, COMMON_SUBS)

    for result in results:
        found.add(result)

    return found


# ----------------------------
# CLASSIFICATION
# ----------------------------
def classify_subdomain(sub):
    status = "No DNS"
    ip = "N/A"

    # DNS check
    try:
        ip = socket.gethostbyname(sub)
        status = "DNS Resolved"
    except:
        return {
            "subdomain": sub,
            "ip": ip,
            "status": status
        }

    # HTTP check
    try:
        r = requests.get(f"http://{sub}", timeout=5)
        return {
            "subdomain": sub,
            "ip": ip,
            "status": f"HTTP {r.status_code}"
        }
    except:
        pass

    # HTTPS check
    try:
        r = requests.get(f"https://{sub}", timeout=5)
        return {
            "subdomain": sub,
            "ip": ip,
            "status": f"HTTPS {r.status_code}"
        }
    except:
        pass

    return {
        "subdomain": sub,
        "ip": ip,
        "status": "Down / Blocked"
    }


# ----------------------------
# MAIN ENUMERATION ENGINE
# ----------------------------
def enumerate_domain(domain):
    all_subs = set()

    # CT logs
    all_subs.update(ct_enum(domain))

    # DNS brute force
    all_subs.update(dns_bruteforce(domain))

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        classified = executor.map(classify_subdomain, all_subs)

    for item in classified:
        results.append(item)

    return sorted(results, key=lambda x: x["subdomain"])


# ----------------------------
# FLASK ROUTE
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    domain = ""

    if request.method == "POST":
        domain = request.form.get("domain")

        if domain:
            results = enumerate_domain(domain)

    return render_template("index.html", results=results, domain=domain)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
