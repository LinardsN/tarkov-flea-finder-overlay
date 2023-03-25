import requests
import json

def run_query(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

def fetch_item(item_name):
    query = f"""
    {{
        items(name: "{item_name}") {{
            id
            name
            shortName
            basePrice
            avg24hPrice
            gridImageLink
        }}
    }}
    """
    result = run_query(query)
    data = result.get("data", {}).get("items", [])
    if data:
        return {
            "name": data[0]["name"],
            "shortName": data[0]["shortName"],
            "id": data[0]["id"],
            "basePrice": data[0]["basePrice"],
            "avg24hPrice": data[0]["avg24hPrice"],
            "gridImageLink": data[0]["gridImageLink"],
        }
    return None

def fetch_item_list():
    query = """
    {
        items {
            id
            name
            shortName
            basePrice
            avg24hPrice
        }
    }
    """
    result = run_query(query)
    data = result.get("data", {}).get("items", [])
    return [{"name": item["name"], "shortName": item["shortName"], "id": item["id"], "basePrice": item["basePrice"], "avg24hPrice": item["avg24hPrice"]} for item in data]

