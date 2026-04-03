@echo off
echo ========================================
echo AI自动感知进化框架启动
echo ========================================
echo.
echo 使用方法:
echo   start_ai_auto_perception.bat scan        - 扫描记忆文件
echo   start_ai_auto_perception.bat audit <路径> - AI审核技能
echo   start_ai_auto_perception.bat report      - 生成AI报告
echo.
echo 示例:
echo   start_ai_auto_perception.bat audit "D:\openclaw\releases\professional-sleep-analyzer"
echo.

if "%1"=="" (
    python AI_AUTO_PERCEPTION_EVOLUTION.py
) else (
    python AI_AUTO_PERCEPTION_EVOLUTION.py %*
)

pause