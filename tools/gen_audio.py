"""Tạo mp3 tiếng Việt (ElevenLabs, giọng Alice) cho các câu VN của 1 Phần. Chạy lại được: bỏ qua file đã có."""
import os, re, io, sys, json, html, hashlib, time, urllib.request, urllib.error

K = os.environ['K']
# dùng: gen_vi_audio.py <part id> <lang vi-VN|en-US> <voice key> <voice id>
PART, LANG, VKEY, VOICE = sys.argv[1:5]
ROOT = r"C:\Users\User\Desktop\TJ\Project\L00_ES-CN"
PAGE = os.path.join(ROOT, "Operation_0-Chunks_1000_cau_EN_ES_CN_VN_v4.html")
OUT = os.path.join(ROOT, "audio", VKEY)
os.makedirs(OUT, exist_ok=True)

s = io.open(PAGE, encoding="utf-8").read()
i = s.index(f'<section class="part" id="{PART}"')
j = s.find('<section class="part"', i + 10)
sec = s[i:j if j > 0 else len(s)]
texts = list(dict.fromkeys(html.unescape(x) for x in re.findall(r'<button class="say-btn" data-say="([^"]*)" data-lang="%s"' % LANG, sec)))
print(PART, LANG, VKEY, 'unique sentences:', len(texts), 'chars:', sum(map(len, texts)), flush=True)

mf = os.path.join(OUT, "manifest.json")
manifest = json.load(open(mf, encoding="utf-8")) if os.path.exists(mf) else {}
used = 0
for n, t in enumerate(texts, 1):
    name = hashlib.sha1(t.encode('utf-8')).hexdigest()[:12] + '.mp3'
    path = os.path.join(OUT, name)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        manifest[t] = name; continue
    body = json.dumps({"text": t, "model_id": "eleven_flash_v2_5", "language_code": LANG[:2]}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_64", data=body,
                                 headers={"xi-api-key": K, "Content-Type": "application/json; charset=utf-8"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                open(path, 'wb').write(r.read())
                used += int(r.headers.get('x-character-count') or 0)
            manifest[t] = name
            break
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode('utf-8', 'replace')
            if e.code == 429 and attempt < 3:
                time.sleep(3 * (attempt + 1)); continue
            json.dump(manifest, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            sys.exit(f"STOP at {n}/{len(texts)} HTTP {e.code}: {msg}")
    if n % 25 == 0:
        print(f'{n}/{len(texts)} credits so far: {used}', flush=True)
        json.dump(manifest, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

json.dump(manifest, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('done. files in manifest:', len(manifest), 'credits used this run:', used)
