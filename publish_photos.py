import os
import sys
import shutil
import subprocess
from pathlib import Path

# 解決 Windows CP950 控制台編碼問題
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

SRC_DIR = Path("F:/0.PIC/1.After/260315_詩語_香水/4.想PO")
DEST_DIR = Path("D:/Gemini_CLI/Photography/Albums/Product/260315_詩語_香水")
PORTFOLIO_DIR = Path("D:/Gemini_CLI/Photography/portfolio")

def run_publish():
    print(f"🚀 開始發布「260315_詩語_香水」專案照片...")
    
    # 1. 建立目標資料夾
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. 清空原本的目標資料夾（若有）
    for item in DEST_DIR.iterdir():
        if item.is_file():
            item.unlink()
            
    # 3. 複製 4.想PO 下的所有圖片
    valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    src_files = [f for f in SRC_DIR.iterdir() if f.is_file() and f.suffix in valid_extensions]
    
    print(f"📦 正在從 {SRC_DIR} 複製 {len(src_files)} 張照片到 {DEST_DIR}...")
    for f in src_files:
        shutil.copy2(f, DEST_DIR / f.name)
        print(f"  ➡️ 複製: {f.name}")
        
    print("✅ 照片複製完成！")
    
    # 4. 執行相片優化處理腳本 (photo_process.py)
    process_script = PORTFOLIO_DIR / "photo_process.py"
    if process_script.exists():
        print(f"⚙️ 正在執行 {process_script.name} 來優化相片並更新 JSON 資料...")
        try:
            # 執行 python photo_process.py 並且繼承 stdout
            result = subprocess.run(
                [sys.executable, str(process_script)],
                cwd=str(PORTFOLIO_DIR),
                capture_output=True
            )
            
            try:
                stdout_str = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                stdout_str = result.stdout.decode('cp950', errors='replace')
                
            try:
                stderr_str = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                stderr_str = result.stderr.decode('cp950', errors='replace')

            print(stdout_str)
            if result.returncode == 0:
                print("🎉 相片處理與網站資料同步成功！專案已成功發布。")
            else:
                print(f"❌ photo_process.py 執行失敗，錯誤訊息:\n{stderr_str}")
        except Exception as e:
            print(f"❌ 執行 photo_process.py 時發生異常: {e}")
    else:
        print(f"⚠️ 找不到相片處理腳本: {process_script}")

if __name__ == "__main__":
    run_publish()
