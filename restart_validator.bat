@echo off
echo Restarting Validator Service with AST Analyzer integration...
echo.

REM Kill existing validator service
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Validator*" 2>nul
timeout /t 2 /nobreak >nul

REM Start validator service with AST analyzer
cd microservices\validator-service
start "Validator Service with AST" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
cd ..

echo.
echo Waiting for service to start (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo Testing service...
python -c "import requests; r=requests.get('http://localhost:8001/health', timeout=5); print('Status:', r.json()['status'] if r.status_code==200 else 'Failed')"

echo.
echo Validator Service restarted with AST Analyzer integration!
echo Test AST analysis: python test_ast_validation.py
pause