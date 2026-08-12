import os
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

# 解決 Windows 主機 print Unicode 的 CP950 編碼問題
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

SRC_DIR = Path("F:/0.PIC/1.After/260315_詩語_香水/3.LR顆粒")
OUTPUT_DIR = Path("D:/Gemini_CLI/Photography/portfolio/contact_sheets")

CELL_SIZE = 600
GRID_COLS = 3
GRID_ROWS = 4
SHEET_WIDTH = GRID_COLS * CELL_SIZE
SHEET_HEIGHT = GRID_ROWS * CELL_SIZE

def create_sheets():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    files = sorted([f for f in SRC_DIR.iterdir() if f.is_file() and f.suffix in valid_extensions])
    
    if not files:
        print("❌ 找不到相片檔案！")
        return
        
    print(f"📦 找到 {len(files)} 張相片，開始建立拼貼聯絡簿...")
    
    # 每 12 張一組
    chunk_size = GRID_COLS * GRID_ROWS
    chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]
    
    # 嘗試載入 Windows 系統字型，若無則使用預設字型
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    for sheet_idx, chunk in enumerate(chunks):
        sheet = Image.new("RGB", (SHEET_WIDTH, SHEET_HEIGHT), (20, 20, 20)) # 暗色背景
        draw = ImageDraw.Draw(sheet)
        
        print(f" 🎬 正在製作第 {sheet_idx + 1}/{len(chunks)} 張拼貼圖...")
        
        for idx, img_path in enumerate(chunk):
            col = idx % GRID_COLS
            row = idx // GRID_COLS
            
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            
            try:
                with Image.open(img_path) as img:
                    img = ImageOps.exif_transpose(img)
                    # 縮放相片
                    img.thumbnail((CELL_SIZE - 20, CELL_SIZE - 20), Image.Resampling.LANCZOS)
                    
                    # 置中放入單元格
                    img_w, img_h = img.size
                    offset_x = x + (CELL_SIZE - img_w) // 2
                    offset_y = y + (CELL_SIZE - img_h) // 2
                    
                    sheet.paste(img, (offset_x, offset_y))
                    
                    # 畫上單元格邊框，方便區分
                    draw.rectangle([x, y, x + CELL_SIZE, y + CELL_SIZE], outline=(50, 50, 50), width=1)
                    
                    # 在左上角畫上文字背景與標籤
                    label = f"[{idx + 1}] {img_path.stem}"
                    # 畫一個半透明黑色背景條
                    draw.rectangle([x + 10, y + 10, x + 350, y + 55], fill=(0, 0, 0))
                    draw.text((x + 15, y + 15), label, fill=(235, 94, 40), font=font) # 橘色文字
                    
            except Exception as e:
                print(f"  ⚠️ 讀取相片 {img_path.name} 失敗: {e}")
                
        # 存檔
        output_file = OUTPUT_DIR / f"contact_sheet_{sheet_idx + 1}.jpg"
        sheet.save(output_file, "JPEG", quality=90)
        print(f"  ➡️ 已存檔: {output_file.name}")
        
    print("✨ 所有拼貼聯絡簿製作完成！")

if __name__ == "__main__":
    create_sheets()
