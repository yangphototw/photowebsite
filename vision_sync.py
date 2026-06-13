import os
import time
import hashlib
from pathlib import Path
from PIL import Image, ImageGrab

# 設定目標目錄
TARGET_DIR = Path("D:/Gemini_CLI/Photography/portfolio/temp_vision")
TARGET_FILE = TARGET_DIR / "latest_vison.png"

def get_image_hash(img):
    """計算圖片內容的 hash，用來判斷是否為同一張圖"""
    return hashlib.md5(img.tobytes()).hexdigest()

def watch_clipboard():
    print("🚀 全自動視覺助手已啟動！")
    print(f"操作方式：按下 Win + Shift + S 截圖後，圖片將自動同步到我這裡。")
    print("-" * 50)
    
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    last_hash = None

    try:
        while True:
            # 從剪貼簿抓取圖片
            img = ImageGrab.grabclipboard()
            
            if isinstance(img, Image.Image):
                current_hash = get_image_hash(img)
                
                # 如果這張圖跟上次的不一樣，就存檔
                if current_hash != last_hash:
                    # 轉為 RGB 以確保能存成高品質 PNG
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img.save(TARGET_FILE, "PNG")
                    last_hash = current_hash
                    print(f"✨ [自動同步] 已捕捉到新截圖並存檔！時間: {time.strftime('%H:%M:%S')}")
            
            time.sleep(0.5) # 每 0.5 秒檢查一次剪貼簿
    except KeyboardInterrupt:
        print("\n👋 視覺助手已停止。")
    except Exception as e:
        print(f"⚠️ 發生錯誤: {e}")

if __name__ == "__main__":
    watch_clipboard()
