@echo off
echo Starting Minimum AI CAD Development Environment...
echo.

echo [1/2] Starting Frontend Development Server...
cd frontend
start "Frontend" npm start
echo Frontend will open at http://localhost:3000
echo.

echo [2/2] Backend services can be started with:
echo   - API Gateway: cd backend/services/api_gateway ^&^& python main.py
echo   - File Processor: cd backend/services/file_processor ^&^& python main.py  
echo   - CAD Engine: cd backend/services/cad_engine ^&^& python main.py
echo.

echo Development environment setup complete!
echo Press any key to continue...
pause > nul