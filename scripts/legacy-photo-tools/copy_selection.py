import shutil
import sys
from pathlib import Path

# 解決 Windows CP950 編碼問題
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


SRC_DIR = Path("F:/0.PIC/1.After/260315_詩語_香水/3.LR顆黎")
# 為了避免打錯字，我們看一下先前 list_dir 的結果是 "3.LR顆粒"。
# 修正為 "3.LR顆粒"
SRC_DIR = Path("F:/0.PIC/1.After/260315_詩語_香水/3.LR顆粒")
TMP_DIR = Path("D:/Gemini_CLI/Photography/portfolio/tmp")

FINAL_SELECTION = [
    "DSC01604.jpg",
    "DSC01262.jpg",
    "DSC01284.jpg",
    "DSC01762.jpg",
    "DSC01192.jpg",
    "DSC01381.jpg",
    "DSC01519.jpg",
    "DSC01301.jpg",
    "DSC01666.jpg",
    "DSC01805.jpg",
    "DSC01642.jpg",
    "DSC01829.jpg"
]

def copy_files():
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 清空 tmp 目錄
    for item in TMP_DIR.iterdir():
        if item.is_file():
            item.unlink()
            
    print(f"🚀 開始複製 AI 視覺挑選的 12 張原圖至 {TMP_DIR}...")
    
    success_count = 0
    for name in FINAL_SELECTION:
        src = SRC_DIR / name
        dest = TMP_DIR / name
        if src.exists():
            shutil.copy2(src, dest)
            print(f"  ➡️ 複製成功: {name} ({src.stat().st_size / (1024*1024):.2f} MB)")
            success_count += 1
        else:
            print(f"  ❌ 找不到檔案: {name}")
            
    print(f"✨ 複製完成！成功複製 {success_count}/{len(FINAL_SELECTION)} 張大圖。")

if __name__ == "__main__":
    copy_files()
