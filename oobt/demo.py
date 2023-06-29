# Out Of Box testing
#
#  Run simple serparpi search
#
import serpapi
import sys, os, pprint

print("initialize serpapi client")
client = serpapi.Client({"api_key": os.getenv("API_KEY", "demo")})
print("execute search")
result = client.search(
    {
        "q": "coffee",
        "location": "Austin,Texas",
    }
)
print("display result:")
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(result)
print("------")
if len(result) > 0:
    print("OK: Out of box tests passed")
    sys.exit(0)

print("FAIL: Out of box tests failed: no result")
sys.exit(1)
