"""Đổi phiên âm dòng tiếng Anh trong trang 1000 câu sang IPA giọng Mỹ (TJ yêu cầu 2026-09-30).
Trước: "♪ hơ-LÔU, mai NÊIM iz LEN."  ->  Sau: "♪ /həˈloʊ, maɪ neɪm ɪz læn./"

Nguồn: thư viện eng_to_ipa (từ điển phát âm Mỹ CMU, miễn phí) + vài quy tắc sửa tay bên dưới.
Chạy lại được bao nhiêu lần cũng được (luôn tính lại từ câu tiếng Anh gốc trong nút 🔊).
Cần: pip install eng_to_ipa
Dùng: python tools/en_ipa.py            (sửa trang)
      python tools/en_ipa.py --dry      (chỉ in thử 10 câu, không sửa)
"""
import io, os, re, sys, html
import eng_to_ipa as ipa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "Operation_0-Chunks_1000_cau_EN_ES_CN_VN_v4.html")

# Từ có nhiều cách đọc: chọn cách tự nhiên trong câu nói (dạng lướt cho từ chức năng)
PREFER = {
    "nice": "naɪs", "hello": "həˈloʊ", "to": "tə", "the": "ðə", "a": "ə", "for": "fər", "can": "kən",
    "and": "ənd", "of": "əv", "from": "frəm", "at": "æt", "an": "ən", "or": "ɔr", "are": "ɑr",
    "was": "wəz", "were": "wər", "your": "jʊr", "you're": "jʊr", "here": "hɪr", "there": "ðɛr",
    "their": "ðɛr", "they're": "ðɛr", "where": "wɛr", "our": "aʊər", "hour": "aʊər", "data": "ˈdeɪtə",
    "either": "ˈiðər", "neither": "ˈniðər", "schedule": "ˈskɛdʒul", "via": "ˈvaɪə", "route": "raʊt",
}
# Từ không có trong từ điển (từ mới, viết tắt)
MANUAL = {
    "hashtag": "ˈhæʃˌtæɡ", "hashtags": "ˈhæʃˌtæɡz", "infographic": "ˌɪnfoʊˈɡræfɪk", "infographics": "ˌɪnfoʊˈɡræfɪks",
    "homepage": "ˈhoʊmˌpeɪdʒ", "backlink": "ˈbækˌlɪŋk", "backlinks": "ˈbækˌlɪŋks", "retarget": "riˈtɑrɡɪt",
    "retargeting": "riˈtɑrɡɪtɪŋ", "rebrand": "riˈbrænd", "rebranding": "riˈbrændɪŋ", "influencer": "ˈɪnfluənsər",
    "influencers": "ˈɪnfluənsərz", "creatives": "kriˈeɪtɪvz", "ssn": "ˌɛs ɛs ˈɛn", "itin": "ˈaɪtɪn",
    "chi": "tʃi", "minh": "mɪn", "cpa": "ˌsi pi ˈeɪ", "llc": "ˌɛl ɛl ˈsi", "int": "ɪnt", "irs": "ˌaɪ ɑr ˈɛs", "kpi": "ˌkeɪ pi ˈaɪ",
    "kpis": "ˌkeɪ pi ˈaɪz", "seo": "ˌɛs i ˈoʊ", "ceo": "ˌsi i ˈoʊ", "roi": "ˌɑr oʊ ˈaɪ", "ok": "oʊˈkeɪ",
}
SYM = str.maketrans({"ʤ": "dʒ", "ʧ": "tʃ"})   # ký hiệu IPA chuẩn thay chữ ghép

def word_ipa(w):
    lw = w.lower().strip("'")
    if lw in MANUAL: return MANUAL[lw]
    if lw in PREFER: return PREFER[lw]
    if "-" in lw: return "-".join(word_ipa(p) for p in lw.split("-") if p)
    if lw.isdigit(): return w                      # số giữ nguyên (1099, 2025...)
    alts = ipa.ipa_list(lw)
    out = alts[0][0] if alts and alts[0] else ipa.convert(lw)
    out = out.replace("*", "").translate(SYM).replace("g", "ɡ")
    if out.startswith("hw"): out = out[1:]                       # what /wʌt/ (người Mỹ ít bật h)
    # từ điển CMU ghi cả âm nhấn lẫn âm lướt là ə -> âm NHẤN đổi thành ʌ (touch /tʌtʃ/, company /ˈkʌmpəni/)
    out = re.sub(r"([ˈˌ][^aeiouæɑɔəɛɪʊʌ]*)ə(?!r)", r"\1ʌ", out)
    if "ˈ" not in out and re.fullmatch(r"[^aeiouæɑɔɛɪʊʌ]*ə(?!r)[^aeiouæɑɔɛɪʊʌə]*", out):
        out = out.replace("ə", "ʌ")                              # từ 1 âm tiết: but /bʌt/, much /mʌtʃ/
    return out

def sent_ipa(text):
    # giữ nguyên dấu câu, chỉ đổi từng từ
    return re.sub(r"[A-Za-z0-9][A-Za-z0-9'\-]*", lambda m: word_ipa(m.group(0)), text)

s = io.open(PAGE, encoding="utf-8").read()
row_re = re.compile(r'(<div class="lrow" data-lang="en-US"><span class="flag">[^<]*</span><button class="say-btn" data-say="([^"]*)"(?:(?!</div>).)*?<span class="phon">)♪ [^<]*(</span>)', re.S)
if "--dry" in sys.argv:
    for m in list(row_re.finditer(s))[:10]:
        t = html.unescape(m.group(2)); print(t, "->", "/" + sent_ipa(t) + "/")
    sys.exit()
s, n = row_re.subn(lambda m: m.group(1) + "♪ /" + html.escape(sent_ipa(html.unescape(m.group(2))), quote=False) + "/" + m.group(3), s)
io.open(PAGE, "w", encoding="utf-8", newline="").write(s)
print("đã đổi", n, "dòng phiên âm tiếng Anh sang IPA giọng Mỹ")
