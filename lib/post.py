"""Agenda um vídeo (URL pública) nos 3 canais do Buffer (TikTok, Instagram Reels, YouTube Shorts).
Uso: post.py meta.json   (meta: url, title, desc, tags_social, tags_yt, due_at ISO-UTC)"""
import json, os, sys, urllib.request

API = "https://api.buffer.com"


def gql(query, variables=None):
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 headers=dict({"Content-Type": "application/json"},
                                              **({"Authorization": "Bearer " + os.environ["BUFFER_KEY"]}
                                                 if os.environ.get("BUFFER_KEY") else {})))
    return json.load(urllib.request.urlopen(req, timeout=120))


def channels():
    org = gql("query { account { organizations { id } } }")["data"]["account"]["organizations"][0]["id"]
    q = 'query($o: OrganizationId!) { channels(input:{organizationId:$o}) { id service name } }'
    r = gql(q, {"o": org})
    if "errors" in r:  # alguns esquemas usam String
        r = gql(q.replace("OrganizationId!", "String!"), {"o": org})
    return {c["service"]: c["id"] for c in r["data"]["channels"]}


MUT = """mutation($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt status } }
    ... on MutationError { message }
  }
}"""


def schedule(meta, dry=False):
    ch = channels()
    social = f"{meta['desc']}\n\n{' '.join(meta['tags_social'])}"
    yt_desc = f"{meta['desc']}\n\n{' '.join(meta['tags_yt'])}"
    video = {"url": meta["url"], "metadata": {"thumbnailOffset": int(meta.get("thumb_ms", 0))}}
    base = {"schedulingType": "automatic", "mode": "customScheduled", "dueAt": meta["due_at"],
            "assets": [{"video": video}], "needsApproval": False}
    posts = {
        "tiktok": dict(base, channelId=ch["tiktok"], text=social,
                       metadata={"tiktok": {"title": meta["title"][:90], "isAiGenerated": True}}),
        "instagram": dict(base, channelId=ch["instagram"], text=social,
                          metadata={"instagram": {"type": "reel", "shouldShareToFeed": True, "isAiGenerated": True}}),
        "youtube": dict(base, channelId=ch["youtube"], text=yt_desc,
                        metadata={"youtube": {"title": (meta["title"] + " #shorts")[:100], "privacy": "public",
                                              "categoryId": "25", "madeForKids": False, "isAiGenerated": True,
                                              "notifySubscribers": True, "type": "short"}}),
    }
    out = {}
    for svc, inp in posts.items():
        if dry:
            out[svc] = inp
            continue
        r = gql(MUT, {"input": inp})
        out[svc] = r.get("data", {}).get("createPost") if r.get("data") else r
        print(svc, json.dumps(out[svc], ensure_ascii=False))
    return out


if __name__ == "__main__":
    meta = json.load(open(sys.argv[1]))
    schedule(meta, dry="--dry" in sys.argv)
