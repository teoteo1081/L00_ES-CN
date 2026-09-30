"""Tạo mp3 bằng giọng Microsoft Edge (edge-tts, miễn phí) cho các câu CHƯA có giọng thu sẵn khác.
Chạy lại được: bỏ qua file đã có. Dùng: python tools/gen_edge_audio.py <lang vi-VN|en-US> <voice-key, vd vi-hoaimy> <edge voice, vd vi-VN-HoaiMyNeural> [thư mục giọng ưu tiên cần bỏ qua ...]
vd: python tools/gen_edge_audio.py vi-VN vi-hoaimy vi-VN-HoaiMyNeural vi-alice
Lưu ý: edge-tts không phải API chính thức của Microsoft — có thể lỗi/bị chặn; file đã tạo thì vẫn dùng bình thường."""
import os, re, io, sys, json, html, hashlib, asyncio
import edge_tts

LANG, VKEY, EDGE_VOICE = sys.argv[1:4]
SKIP = sys.argv[4:]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "Operation_0-Chunks_1000_cau_EN_ES_CN_VN_v4.html")
OUT = os.path.join(ROOT, "audio", VKEY)
os.makedirs(OUT, exist_ok=True)

s = io.open(PAGE, encoding="utf-8").read()
texts = list(dict.fromkeys(html.unescape(x) for x in re.findall(r'<button class="say-btn" data-say="([^"]*)" data-lang="%s"' % LANG, s)))
skip = set()
for d in SKIP:
    mf = os.path.join(ROOT, "audio", d, "manifest.json")
    if os.path.exists(mf): skip |= set(json.load(open(mf, encoding="utf-8")))
todo = [t for t in texts if t not in skip]
print(LANG, VKEY, "tổng:", len(texts), "| đã có giọng khác:", len(texts) - len(todo), "| cần tạo:", len(todo), flush=True)

mf = os.path.join(OUT, "manifest.json")
manifest = json.load(open(mf, encoding="utf-8")) if os.path.exists(mf) else {}

async def one(t, path):
    last = None
    for k in range(6):
        try:
            await edge_tts.Communicate(t, EDGE_VOICE).save(path)
            if os.path.getsize(path) > 500: return True
        except Exception as e:
            last = e
        await asyncio.sleep(2 + 3 * k)
    print("  FAIL:", t[:50], type(last).__name__ if last else "empty", flush=True)
    if os.path.exists(path): os.remove(path)
    return False

async def main():
    fails = 0
    for n, t in enumerate(todo, 1):
        name = hashlib.sha1(t.encode("utf-8")).hexdigest()[:12] + ".mp3"
        path = os.path.join(OUT, name)
        if os.path.exists(path) and os.path.getsize(path) > 500:
            manifest[t] = name; continue
        if await one(t, path): manifest[t] = name
        else: fails += 1
        await asyncio.sleep(0.3)
        if n % 50 == 0:
            print(f"{n}/{len(todo)} (lỗi {fails})", flush=True)
            json.dump(manifest, open(mf, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(manifest, open(mf, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("xong:", len(manifest), "file | lỗi:", fails)

asyncio.run(main())
