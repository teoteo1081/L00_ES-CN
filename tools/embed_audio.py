"""Chạy lại sau mỗi lần tạo audio: gom audio/<voice>/manifest.json vào biến AUDIO trong trang."""
import io, os, re, json, sys
ROOT = r"C:\Users\User\Desktop\TJ\Project\L00_ES-CN"
P = os.path.join(ROOT, "Operation_0-Chunks_1000_cau_EN_ES_CN_VN_v4.html")
META = {'vi-alice': ('vi-VN', 'alice', 'Alice'), 'en-laura': ('en-US', 'laura', 'Laura'), 'en-brian': ('en-US', 'brian', 'Brian')}
audio = {}
for d, (lang, key, name) in META.items():
    mf = os.path.join(ROOT, 'audio', d, 'manifest.json')
    if not os.path.exists(mf): continue
    files = {t: f for t, f in json.load(open(mf, encoding='utf-8')).items() if os.path.exists(os.path.join(ROOT, 'audio', d, f))}
    if files: audio.setdefault(lang, {})[key] = {'name': name, 'dir': f'audio/{d}/', 'files': files}
s = io.open(P, encoding="utf-8").read()
new = "/*AUDIO>*/ AUDIO = " + json.dumps(audio, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + "; /*<AUDIO*/"
s, n = re.subn(r"/\*AUDIO>\*/.*?/\*<AUDIO\*/", lambda m: new, s, flags=re.S)
if n != 1: sys.exit(f"marker count {n}")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print({l: {k: len(v['files']) for k, v in d.items()} for l, d in audio.items()})
