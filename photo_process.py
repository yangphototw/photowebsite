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
    # 簡單的 slug 轉換，移除特殊字元
    return re.sub(r'[^\w\s-]', '', text.strip()).replace(' ', '-')

def process_single_folder(folder_path, output_subpath):
    """處理單一資料夾內的所有圖片，返回 Web 存取路徑列表"""
    print(f"  📸 正在處理: {folder_path.name}")
    output_dir = TARGET_BASE_DIR / output_subpath
    output_dir.mkdir(parents=True, exist_ok=True)
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    project_images = []
    
    img_files = sorted([f for f in folder_path.iterdir() if f.suffix.lower() in valid_extensions])
    
    for img_path in img_files:
        try:
            with Image.open(img_path) as img:
                img = ImageOps.exif_transpose(img)
                width, height = img.size
                max_size = 2048
                if max(width, height) > max_size:
                    ratio = max_size / max(width, height)
                    img = img.resize((int(width * ratio), int(height * ratio)), Image.Resampling.LANCZOS)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                output_filename = f"{img_path.stem}.webp"
                final_output_path = output_dir / output_filename
                img.save(final_output_path, "WEBP", quality=85, method=6)

                # 使用正斜線構建 Web 路徑
                web_path = f"/images/albums/{output_subpath}/{output_filename}"
                project_images.append(web_path)
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
    print(f"🚀 開始掃描資料夾結構...")
    
    if not ALBUMS_DIR.exists():
        print(f"❌ 找不到來源資料夾: {ALBUMS_DIR}")
        return

    albums_data = []
    carousel_data = []
    featured_data = []

    # 遍歷 Albums 下的資料夾
    categories = [d for d in ALBUMS_DIR.iterdir() if d.is_dir()]
    for category_path in categories:
        category_name = category_path.name
        
        # 處理首頁特殊資料夾
        if category_name == "00_Home_Carousel":
            paths = process_single_folder(category_path, "00_Home_Carousel")
            carousel_data = [{"src": p, "alt": "Carousel Image"} for p in paths]
            continue
            
        if category_name == "00_Home_Featured":
            paths = process_single_folder(category_path, "00_Home_Featured")
            featured_data = [{"src": p, "alt": "Featured Image"} for p in paths]
            continue

        # 處理一般作品集類別 (如 Portrait, Wedding)
        category_slug = slugify(category_name) or "category"
        print(f"📂 進入類別: {category_name}")

        projects = [d for d in category_path.iterdir() if d.is_dir()]
        
        # 如果該類別下沒有子資料夾，但有照片，就當作一個名為 "Gallery" 的專案處理
        img_files = [f for f in category_path.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
        if img_files and not projects:
             print(f"  📸 發現散落照片，建立預設專案...")
             # 建立一個隱擬的子資料夾路徑來借用現有邏輯 (實務上是直接處理這個 category_path)
             paths = process_single_folder(category_path, category_name)
             if paths:
                 albums_data.append({
                    "category": category_name,
                    "categorySlug": category_slug,
                    "project": "Gallery",
                    "projectSlug": "gallery",
                    "cover": paths[0],
                    "images": paths
                })
             continue

        # 正常處理子專案
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
                    "cover": paths[0],
                    "images": paths
                })

    # 儲存三個 JSON 檔案
    save_json(albums_data, "albums.json")
    save_json(carousel_data, "carousel.json")
    save_json(featured_data, "featured.json")
    
    print(f"\n✅ 處理完畢！")

if __name__ == "__main__":
    process_albums()
