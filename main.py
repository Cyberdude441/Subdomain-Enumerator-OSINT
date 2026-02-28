import requests
import sys

def get_subdomains(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()

        subdomains = set()

        for entry in data:
            name = entry.get("name_value")
            if name:
                for sub in name.split("\n"):
                    sub = sub.strip()
                    if "*" not in sub and domain in sub:
                        subdomains.add(sub.lower())

        return subdomains

    except Exception as e:
        print("Error:", e)
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"\n[*] Enumerating subdomains for: {domain}\n")

    subdomains = get_subdomains(domain)

    for sub in subdomains:
        print(sub)

    print(f"\n[+] Total found: {len(subdomains)}")

if __name__ == "__main__":
    main()
