import os
import json
import re
from pathlib import Path
from PIL import Image, ImageOps

# 設定路徑
ALBUMS_DIR = Path("../Albums")
TARGET_BASE_DIR = Path("public/images/albums")
DATA_DIR = Path("src/data")

def slugify(text):
    return re.sub(r'[^\w\s-]', '', text.strip()).replace(' ', '-')

def process_single_folder(folder_path, output_subpath, is_hero=False):
    """
    處理單一資料夾內的所有圖片
    is_hero: 如果是首頁大圖，使用更高的解析度 (4096px) 與品質 (100)
    回傳：[{ "filename": "name", "src": "/path/to/webp" }, ...]
    """
    if not folder_path.exists():
        return []

    print(f"  📸 正在處理: {folder_path.name} {'(High Quality Mode)' if is_hero else ''}")
    output_dir = TARGET_BASE_DIR / output_subpath
    output_dir.mkdir(parents=True, exist_ok=True)
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    project_images = []
    
    img_files = sorted([f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions])
    
    for img_path in img_files:
        try:
            with Image.open(img_path) as img:
                img = ImageOps.exif_transpose(img)
                width, height = img.size
                
                max_size = 4096 if is_hero else 2048
                if max(width, height) > max_size:
                    ratio = max_size / max(width, height)
                    img = img.resize((int(width * ratio), int(height * ratio)), Image.Resampling.LANCZOS)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                output_filename = f"{img_path.stem}.webp"
                final_output_path = output_dir / output_filename
                
                # 全部品質調至 100%
                img.save(final_output_path, "WEBP", quality=100, method=6)

                web_path = f"/images/albums/{output_subpath}/{output_filename}"
                project_images.append({
                    "filename": img_path.stem.lower(),
                    "src": web_path
                })
        except Exception as e:
            print(f"    ⚠️ 處理 {img_path.name} 時發生錯誤: {e}")
            
    return project_images

def save_json(data, filename):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📂 已更新: {file_path}")

def process_albums():
    print(f"🚀 開始掃描資料夾結構 (100% 品質版)...")
    
    if not ALBUMS_DIR.exists():
        print(f"❌ 找不到來源資料夾: {ALBUMS_DIR}")
        return

    albums_data = []
    carousel_data = []
    featured_data = []
    cards_data = []

    # 1. 優先處理首頁專屬資源 (00_Home)
    home_dir = ALBUMS_DIR / "00_Home"
    if home_dir.exists():
        print(f"📂 進入類別: 00_Home")
        
        # 輪播
        paths = process_single_folder(home_dir / "Carousel", "00_Home/Carousel", is_hero=True)
        carousel_data = [{"src": p["src"], "alt": "Carousel Image"} for p in paths]
        
        # 精華瀑布流
        paths = process_single_folder(home_dir / "Featured", "00_Home/Featured")
        featured_data = [{"src": p["src"], "alt": "Featured Image"} for p in paths]
        
        # 卡片封面 (關鍵修正：讀取檔名作為對應依據)
        paths = process_single_folder(home_dir / "Cards", "00_Home/Cards")
        cards_data = [{"category": p["filename"], "src": p["src"]} for p in paths]

    # 2. 處理一般作品集類別
    categories = [d for d in ALBUMS_DIR.iterdir() if d.is_dir() and not d.name.startswith("00_Home")]
    for category_path in categories:
        category_name = category_path.name
        category_slug = slugify(category_name) or "category"
        print(f"📂 進入類別: {category_name}")

        projects = [d for d in category_path.iterdir() if d.is_dir()]
        
        # 處理散落照片
        img_files = [f for f in category_path.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
        if img_files and not projects:
             print(f"  📸 發現散落照片，建立預設專案...")
             paths = process_single_folder(category_path, category_name)
             if paths:
                 albums_data.append({
                    "category": category_name,
                    "categorySlug": category_slug,
                    "project": "Gallery",
                    "projectSlug": "gallery",
                    "cover": paths[0]["src"],
                    "images": [p["src"] for p in paths]
                })
             continue

        # 處理子專案
        for project_path in projects:
            project_name = project_path.name
            project_slug = slugify(project_name) or "project"
            
            paths = process_single_folder(project_path, f"{category_name}/{project_name}")

            if paths:
                albums_data.append({
                    "category": category_name,
                    "categorySlug": category_slug,
                    "project": project_name,
                    "projectSlug": project_slug,
                    "cover": paths[0]["src"],
                    "images": [p["src"] for p in paths]
                })

    # 儲存 JSON 檔案
    save_json(albums_data, "albums.json")
    save_json(carousel_data, "carousel.json")
    save_json(featured_data, "featured.json")
    save_json(cards_data, "cards.json")
    
    print(f"\n✅ 全部高畫質圖片與卡片資料處理完畢！")

if __name__ == "__main__":
    process_albums()
