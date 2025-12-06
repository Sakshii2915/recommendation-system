@echo off
echo ========================================
echo Testing Recommendation API
echo ========================================
echo.
cd /d "%~dp0"

echo 1. Testing Health Check...
powershell -Command "Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing | Select-Object -ExpandProperty Content"
echo.

echo 2. Tracking an event...
powershell -Command "Invoke-WebRequest -Uri http://localhost:8000/events -Method POST -ContentType 'application/json' -Body '{\"user_id\":\"test_user\",\"item_id\":\"item1\",\"event_type\":\"view\"}' | Select-Object -ExpandProperty Content"
echo.

echo 3. Getting recommendations...
powershell -Command "Invoke-WebRequest -Uri http://localhost:8000/recommendations -Method POST -ContentType 'application/json' -Body '{\"user_id\":\"test_user\",\"limit\":5}' | Select-Object -ExpandProperty Content"
echo.

echo Done! Check the results above.
echo.
echo Or open in browser: http://localhost:8000/docs
echo.
pause

