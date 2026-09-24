@echo off
title Interconti - Generator Comenzi Dictare
cd /d "C:\Users\Lucru\Desktop\interconti"
echo =======================================================
echo    PORNIRE APLICATIE INTERCONTI (CU ACCES TELEFON)
echo =======================================================
echo.
echo Pornire server local...
start /b .venv\Scripts\python.exe app.py
timeout /t 2 >nul
echo.
echo Se genereaza linkul securizat HTTPS pentru telefon...
echo (Linkul va aparea mai jos si merge direct de pe telefon)
echo.
cloudflared.exe tunnel --url http://localhost:5000
pause
