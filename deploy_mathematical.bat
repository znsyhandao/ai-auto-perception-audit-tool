@echo off
echo Deploying Mathematical Audit Service...
docker build -f Dockerfile.mathematical -t mathematical-audit:latest .
docker run -p 8010:8010 mathematical-audit:latest
