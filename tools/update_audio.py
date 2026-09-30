"""CHẠY 1 LỆNH để cập nhật giọng đọc tiếng Việt cho trang 1000 câu.

Thứ tự ưu tiên (TJ chọn 2026-09-30):
  1. ElevenLabs "Alice" — dùng LUÂN PHIÊN các tài khoản: key này hết lượt thì tự chuyển key kế tiếp.
  2. Microsoft "HoaiMy" (edge-tts, miễn phí) — lấp các câu còn thiếu.
  3. Gắn danh sách file vào trang (embed_audio.py).
Trên trang: câu nào có Alice thì đọc Alice, chưa có thì đọc HoaiMy.
Tháng sau lượt ElevenLabs hồi lại: chạy lại lệnh này -> Alice làm tiếp các câu còn thiếu.

Lấy API key ElevenLabs (chọn 1 trong 2 cách):
  a) Từ Supabase Vault (đã cất sẵn tên elevenlabs_key_1, elevenlabs_key_2, ...):
       $env:SUPABASE_PAT = "<Personal Access Token tạo ở supabase.com/dashboard/account/tokens>"
     (xong việc nhớ xoá PAT đó trên Supabase)
  b) Gõ thẳng, nhiều key cách nhau bằng dấu phẩy:
       $env:K = "sk_aaa,sk_bbb"
Rồi chạy (PowerShell, trong thư mục L00_ES-CN):
    python tools/update_audio.py
Xong thì: git add -A; git commit -m "..."; git push   (GitHub Pages sẽ đăng file mới)
Cần: pip install edge-tts
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ALICE = "Xb7hH8MSUJpSbSDYk0k2"
SUPABASE_REF = "pqarpszsipbdugrumhfy"   # project Supabase của TJ WordLoop
PARTS = ["p-0", "p-1", "p-2", "p-3", "readings"]
env = dict(os.environ, PYTHONIOENCODING="utf-8")

def keys_from_vault(pat):
    sql = "select name, decrypted_secret from vault.decrypted_secrets where name like 'elevenlabs_key_%' order by name"
    req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{SUPABASE_REF}/database/query",
                                 data=json.dumps({"query": sql}).encode(),
                                 headers={"Authorization": "Bearer " + pat, "Content-Type": "application/json"})
    rows = json.load(urllib.request.urlopen(req, timeout=30))
    print("Lấy từ Supabase Vault:", [r["name"] for r in rows])
    return [r["decrypted_secret"] for r in rows]

def run(args, extra=None):
    print("\n>>", " ".join(os.path.basename(a) for a in args[:1]) + " " + " ".join(args[1:]), flush=True)
    return subprocess.call([sys.executable] + args, cwd=ROOT, env=dict(env, **(extra or {})))

keys = [k.strip() for k in env.get("K", "").split(",") if k.strip()]
if not keys and env.get("SUPABASE_PAT"):
    keys = keys_from_vault(env["SUPABASE_PAT"])

# 1. Alice — luân phiên key: key hết lượt thì chuyển key kế, làm lại đúng Phần đang dở (file đã có được bỏ qua)
ki = 0
if not keys:
    print("Không có key ElevenLabs -> bỏ qua Alice, chỉ chạy HoaiMy.")
for part in PARTS:
    while ki < len(keys):
        if run([os.path.join(HERE, "gen_audio.py"), part, "vi-VN", "vi-alice", ALICE], {"K": keys[ki]}) == 0:
            break
        print(f"== key #{ki + 1} dừng (hết lượt/lỗi) -> thử key kế tiếp ==")
        ki += 1
    if ki >= len(keys):
        break

# 2. HoaiMy cho các câu Alice chưa có
run([os.path.join(HERE, "gen_edge_audio.py"), "vi-VN", "vi-hoaimy", "vi-VN-HoaiMyNeural", "vi-alice"])

# 3. Gắn vào trang
run([os.path.join(HERE, "embed_audio.py")])
print("\nXong. Nhớ: git add -A; git commit -m \"...\"; git push")
