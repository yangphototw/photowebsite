import os
import json
from pathlib import Path
from PIL import Image, ImageOps

# 設定路徑
SOURCE_DIR = Path("../Portrait")
TARGET_DIR = Path("src/assets/images")
DATA_FILE = Path("src/data/images.json")

def process_images():
    print(f"🚀 開始處理照片...")
    
    # 確保輸出目錄存在
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    images_data = []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')

    if not SOURCE_DIR.exists():
        print(f"❌ 找不到來源資料夾: {SOURCE_DIR}")
        return

    # 讀取檔案
    for img_path in SOURCE_DIR.iterdir():
        if img_path.suffix.lower() in valid_extensions:
            print(f"📸 正在處理: {img_path.name}")
            try:
                with Image.open(img_path) as img:
                    # 修正 EXIF 轉向
                    img = ImageOps.exif_transpose(img)
                    
                    # 縮放邏輯：長邊縮放至 2048px
                    width, height = img.size
                    max_size = 2048
                    if max(width, height) > max_size:
                        if width > height:
                            new_size = (max_size, int(height * (max_size / width)))
                        else:
                            new_size = (int(width * (max_size / height)), max_size)
                        img = img.resize(new_size, Image.Resampling.LANCZOS)

                    # 轉為 sRGB 並另存為 WebP
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    output_filename = f"{img_path.stem}.webp"
                    output_path = TARGET_DIR / output_filename
                    img.save(output_path, "WEBP", quality=85, method=6)

                    images_data.append({
                        "src": f"/src/assets/images/{output_filename}",
                        "alt": "Portrait Work"
                    })
            except Exception as e:
                print(f"⚠️ 處理 {img_path.name} 時發生錯誤: {e}")

    # 寫入 JSON 資料
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(images_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 處理完畢！共處理 {len(images_data)} 張照片。")
    print(f"📂 資料索引已更新至: {DATA_FILE}")

if __name__ == "__main__":
    process_images()
