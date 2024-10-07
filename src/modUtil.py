import requests
import difflib
import re

modBase = "https://www.curseforge.com/minecraft/mc-mods/"

def __get_most_similar__(mod: str, items: list):
    best_match = None
    best_ratio = 0
    
    for item in items:
        name = item["name"].lower()
        slug = item["slug"].lower()
        
        name_ratio = difflib.SequenceMatcher(None, mod, name).ratio() * 100
        slug_ratio = difflib.SequenceMatcher(None, mod, slug).ratio() * 100

        boost = 0
        if mod in name:
            boost += 20
        if mod in slug.split('-'):
            boost += 20

        name_penalty = len(name.split()) * 5 if mod in name else 0
        slug_penalty = len(slug.split('-')) * 5 if mod in slug else 0

        total_score = name_ratio + slug_ratio + boost - name_penalty - slug_penalty

        if total_score > best_ratio:
            best_ratio = total_score
            best_match = item

        print(f"Name: {name}, Slug: {slug}, Name Similarity: {name_ratio:.2f}%, Slug Similarity: {slug_ratio:.2f}%, Total Score: {total_score:.2f}")

    item = {
        "id": best_match["id"],
        "name": best_match["name"],
        "img": best_match["thumbnailUrl"],
        "url": modBase + best_match["slug"]
    }

    return item

def parse(fileName: str):
    hasForge = 'forge' in fileName
    fileName = fileName.replace('forge', '') if hasForge else fileName
    fileName = fileName.lower().replace(' ', '-')
    mod = re.sub(r'(-[-.0-9()]+-[a-zA-Z]+|-[-.0-9()]+|)\.jar$', '', fileName)

    replacer = {
        "taczplus": "tacz: plus (timeless and classics feature addon)",
    }
    if mod in replacer:
        mod = replacer[mod]

    print(f"Mod: {mod}\n")

    url = "https://www.curseforge.com/api/v1/mods/search?gameId=432&index=0&classId=6&pageSize=20&sortField=1&filterText=" + mod
    
    try:
        response = requests.get(url, timeout=5)

        json = response.json()
        items = json["data"][:3]

        return __get_most_similar__(mod, items)
    except Exception as e:
        return None