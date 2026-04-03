@echo off
echo Starting API Gateway on port 8000...
cd microservices\api-gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload