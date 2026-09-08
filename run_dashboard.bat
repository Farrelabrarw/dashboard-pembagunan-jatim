@echo off
echo ========================================
echo   Dashboard Pembangunan Wilayah Jatim
echo ========================================
echo.

echo [1/3] Mengecek Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan. Silakan install Python 3.12 atau 3.13 terlebih dahulu.
    pause
    exit /b
)

echo [2/3] Memasang library yang dibutuhkan...
pip install -r requirements.txt

echo [3/3] Menjalankan dashboard...
echo.
echo Dashboard akan terbuka di browser: http://localhost:8501
echo Jangan tutup jendela ini selama dashboard digunakan.
echo.

streamlit run app.py

pause