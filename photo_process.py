import os
import json
import re
from pathlib import Path
from PIL import Image, ImageOps

# 設定路徑
ALBUMS_DIR = Path("../Albums")
TARGET_BASE_DIR = Path("public/images/albums")
DATA_FILE = Path("src/data/albums.json")

def slugify(text):
    # 簡單的 slug 轉換，移除特殊字元
    return re.sub(r'[^\w\s-]', '', text.strip()).replace(' ', '-')

def process_albums():
    print(f"🚀 開始掃描多層級相簿...")
    
    if not ALBUMS_DIR.exists():
        print(f"❌ 找不到來源資料夾: {ALBUMS_DIR}")
        return

    albums_data = []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')

    # 遍歷類別資料夾
    categories = [d for d in ALBUMS_DIR.iterdir() if d.is_dir()]
    for category_path in categories:
        category_name = category_path.name
        category_slug = slugify(category_name) or "category"
        print(f"📂 進入類別: {category_name}")

        # 遍歷專案資料夾
        projects = [d for d in category_path.iterdir() if d.is_dir()]
        for project_path in projects:
            project_name = project_path.name
            project_slug = slugify(project_name) or "project"
            
            print(f"  📸 正在處理專案: {project_name}")
            
            output_dir = TARGET_BASE_DIR / category_name / project_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            project_images = []
            img_files = sorted([f for f in project_path.iterdir() if f.suffix.lower() in valid_extensions])
            
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
                        web_path = f"/images/albums/{category_name}/{project_name}/{output_filename}"
                        project_images.append(web_path)
                except Exception as e:
                    print(f"    ⚠️ 處理 {img_path.name} 時發生錯誤: {e}")

            if project_images:
                albums_data.append({
                    "category": category_name,
                    "categorySlug": category_slug,
                    "project": project_name,
                    "projectSlug": project_slug,
                    "cover": project_images[0],
                    "images": project_images
                })

    # 寫入 JSON 資料
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(albums_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 處理完畢！已建立 {len(albums_data)} 個專案藝廊。")
    print(f"📂 資料索引已更新至: {DATA_FILE}")

if __name__ == "__main__":
    process_albums()
