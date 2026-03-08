@echo off
cd /d "%~dp0"

echo Starting Paper Manager...
echo Checking Conda environment...

call conda run -n paper-manager streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo =========================================
    echo [ERROR] Paper Manager の起動に失敗しました。
    echo.
    echo - Conda環境 'paper-manager' は作成されていますか？
    echo   (conda env create -f environment.yml を実行してください)
    echo - Streamlit が正しくインストールされていますか？
    echo =========================================
    pause
)
