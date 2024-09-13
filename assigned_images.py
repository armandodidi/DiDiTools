import json

with open('jsons/VerdeVida.json', encoding="utf8") as f:
    with open('jsons/VerdeVidaImages.json', encoding="utf8") as fi:
        original = json.load(f)
        images = json.load(fi)

        for i in range(0, len(images)):
            for y in range(0, len(images)):
                if images[i]["result"][0] == original["items"][y]["item_name"]:
                    original["items"][y]["head_img"] = f"https://img0.didiglobal.com{images[i]["result"][1]}"

with open('jsons/VerdeVidaImages_.json', 'w', encoding='utf-8') as f:
    json.dump(original, f, ensure_ascii=False, indent=4)