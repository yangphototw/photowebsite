import os
import json
import base64
import shutil
import time
from pathlib import Path
from PIL import Image, ImageOps
import requests
import sys

# 解決 Windows 主機 print unicode/emoji 時的 CP950 編碼錯誤
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


# 1. 設定路徑與參數
SRC_DIR = Path("F:/0.PIC/1.After/260315_詩語_香水/3.LR顆粒")
TMP_DIR = Path("D:/Gemini_CLI/Photography/portfolio/tmp")
RESIZE_DIR = Path("D:/Gemini_CLI/Photography/portfolio/tmp_resized")
API_KEY = os.environ.get("GEMINI_API_KEY")

GROUP_SIZE = 12
STAGE1_KEEP_COUNT = 3
FINAL_KEEP_COUNT = 12
RESIZE_MAX_EDGE = 600

def get_gemini_response(prompt, images):
    """
    發送 API 請求給 Gemini 1.5 Flash。
    images: 字典，格式為 {"filename.jpg": base64_str}
    """
    if not API_KEY:
        print("❌ 錯誤: 找不到環境變數 GEMINI_API_KEY！")
        return None

    # 使用標準的 Gemini 1.5 Flash API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    parts = []
    # 加入 Prompt 說明
    parts.append({"text": prompt})
    
    # 加入相片與檔名關聯說明，並附上圖片二進位資料
    for filename, img_b64 in images.items():
        parts.append({"text": f"相片檔名: {filename}"})
        parts.append({
            "inlineData": {
                "mimeType": "image/jpeg",
                "data": img_b64
            }
        })
        
    payload = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            res_data = response.json()
            text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return text_response
        else:
            print(f"⚠️ API 錯誤 (HTTP {response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ API 連線異常: {e}")
        return None

def resize_images():
    """
    將所有原圖縮小成低解析度 JPEG 存在臨時目錄中，以加快 API 上傳並節省 Token。
    """
    print(f"📦 步驟 1: 正在將原始大圖縮小至最大邊 {RESIZE_MAX_EDGE}px...")
    RESIZE_DIR.mkdir(parents=True, exist_ok=True)
    
    valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    files = sorted([f for f in SRC_DIR.iterdir() if f.is_file() and f.suffix in valid_extensions])
    
    resized_files = []
    for f in files:
        dest_path = RESIZE_DIR / f.name
        # 如果已經存在，跳過
        if dest_path.exists():
            resized_files.append(dest_path)
            continue
            
        try:
            with Image.open(f) as img:
                img = ImageOps.exif_transpose(img)
                w, h = img.size
                if max(w, h) > RESIZE_MAX_EDGE:
                    ratio = RESIZE_MAX_EDGE / max(w, h)
                    img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
                
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                img.save(dest_path, "JPEG", quality=85)
                resized_files.append(dest_path)
        except Exception as e:
            print(f"  ⚠️ 無法處理相片 {f.name}: {e}")
            
    print(f"✅ 縮圖處理完成，共 {len(resized_files)} 張相片。")
    return sorted(resized_files)

def to_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def parse_json_list(text):
    """解析 Gemini 回傳的 JSON 列表"""
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception as e:
        # 手動正則提取
        import re
        matches = re.findall(r'DSC\d+\.jpg', text, re.IGNORECASE)
        if matches:
            return list(set(matches))
    return []

def run_curation():
    print("🚀 開始 AI 自動挑片流程 (兩階段淘汰賽)...")
    
    # 建立目標目錄
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. 產生縮圖
    resized_files = resize_images()
    if not resized_files:
        print("❌ 沒有找到可處理 hometown 相片。")
        return

    # 2. 第一階段: 分組初賽
    print(f"\n🏆 步驟 2: 開始第一階段分組初賽 (每組最多 {GROUP_SIZE} 張，取前 {STAGE1_KEEP_COUNT} 名)...")
    candidates = []
    
    groups = [resized_files[i:i + GROUP_SIZE] for i in range(0, len(resized_files), GROUP_SIZE)]
    
    for idx, group in enumerate(groups):
        print(f" 🎬 正在評估第 {idx + 1}/{len(groups)} 組，包含 {len(group)} 張相片...")
        
        # 讀取並轉換圖片為 base64
        images = {}
        for f in group:
            images[f.name] = to_base64(f)
            
        prompt = (
            f"你是一位專業的攝影編輯。這裡有 {len(group)} 張商業人像與香水主題的相片。\n"
            f"請幫我挑選出其中構圖、光影與故事性最優秀的 {STAGE1_KEEP_COUNT} 張，並排除手震、模糊或眨眼的照片。\n"
            "請務必根據每張相片提供的檔名進行挑選，並嚴格只回傳一個包含挑選檔名的 JSON array 格式，不需任何其他說明文字。\n"
            "範例格式:\n"
            '["DSC01163.jpg", "DSC01174.jpg"]'
        )
        
        res_text = get_gemini_response(prompt, images)
        if res_text:
            selected = parse_json_list(res_text)
            # 過濾確保回傳的檔名確實在該組中
            group_names = [f.name for f in group]
            valid_selected = [name for name in selected if name in group_names]
            print(f"   ✨ 第 {idx + 1} 組初賽挑中: {valid_selected}")
            candidates.extend([RESIZE_DIR / name for name in valid_selected])
        else:
            print(f"   ⚠️ 第 {idx + 1} 組 API 回呼失敗，預設保留前 2 張作為備份。")
            candidates.extend(group[:2])
            
        time.sleep(1) # 避開 API 頻率限制
        
    print(f"🚩 第一階段結束。共有 {len(candidates)} 張相片晉級決賽。")

    # 3. 第二階段: 總決賽
    print(f"\n👑 步驟 3: 開始第二階段總決賽 (從 {len(candidates)} 張中篩選出最終 {FINAL_KEEP_COUNT} 張)...")
    
    images = {}
    for f in candidates:
        if f.exists():
            images[f.name] = to_base64(f)
            
    prompt = (
        f"你是一位專業的視覺總監與攝影編輯。這裡有 {len(images)} 張在第一階段初選中晉級的作品，主題是『詩語_香水』。\n"
        f"請從中挑選出最精美的 {FINAL_KEEP_COUNT} 張相片，作為最終要放在作品集網站上的展示成果。\n"
        "【重要篩選標準】:\n"
        "1. 必須注重作品集的「多樣性」，需要包含: 模特兒的大特寫 (Close-up)、半身照 (Medium shot)、全身照 (Full shot)，以及單純香水瓶商品的靜物特寫。\n"
        "2. 避免挑選到動作、表情或構圖高度重複的照片（例如同一個姿勢的連拍）。\n"
        "3. 請依據提供的相片檔名進行挑選。\n"
        "請嚴格只回傳一個包含挑選檔名的 JSON array 格式，不需任何其他說明文字。\n"
        "範例格式:\n"
        '["DSC01163.jpg", "DSC01174.jpg"]'
    )
    
    res_text = get_gemini_response(prompt, images)
    final_selection = []
    if res_text:
        final_selection = parse_json_list(res_text)
        # 過濾確保檔名在決賽名單中
        candidate_names = [f.name for f in candidates]
        final_selection = [name for name in final_selection if name in candidate_names]
        
    # 如果決賽失敗，或是選出的數量不對，我們用備份方案
    if not final_selection:
        print("⚠️ 決賽 API 回呼失敗或格式不符，改用預設初賽前幾名相片。")
        final_selection = [f.name for f in candidates[:FINAL_KEEP_COUNT]]
        
    # 限制最大數量
    final_selection = final_selection[:FINAL_KEEP_COUNT]
    print(f"🎉 決賽最終挑選的名單為 ({len(final_selection)} 張): {final_selection}")

    # 4. 複製原圖到 tmp 資料夾
    print(f"\n📂 步驟 4: 正在將挑選的原始高解析度照片複製到 {TMP_DIR} ...")
    
    # 清空 tmp 目錄
    for item in TMP_DIR.iterdir():
        if item.is_file():
            item.unlink()
            
    for name in final_selection:
        src_path = SRC_DIR / name
        dest_path = TMP_DIR / name
        if src_path.exists():
            shutil.copy2(src_path, dest_path)
            print(f"  ➡️ 複製: {name} ({src_path.stat().st_size / (1024*1024):.2f} MB)")
            
    # 5. 清理縮圖暫存目錄
    if RESIZE_DIR.exists():
        shutil.rmtree(RESIZE_DIR)
    print("\n✨ AI 挑片與原圖複製全部完成！")

if __name__ == "__main__":
    run_curation()
