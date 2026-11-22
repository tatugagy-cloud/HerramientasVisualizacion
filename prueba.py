import requests
url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno"
r = requests.get(url, headers={"Bmx-Token": "2d05a732795736c9d063eeeb262cc2920a58a03a5d56e2a9833900291b4eefd6"})
print(r.status_code, r.text[:200])