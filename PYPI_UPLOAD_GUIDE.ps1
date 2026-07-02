# ====================================
# PyPI 发布完整指南
# ====================================

Write-Host "🎯 ReadmeMagic PyPI 发布指南" -ForegroundColor Cyan
Write-Host ""
Write-Host "步骤 1: 获取 PyPI API Token" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
Write-Host "1. 访问 https://pypi.org/account/register/ (如果还没有账号)"
Write-Host "2. 登录后访问 https://pypi.org/manage/account/token/"
Write-Host "3. 点击 'Add a new token'"
Write-Host "4. 设置 Token 名称: readme-magic-publish"
Write-Host "5. 权限选择: Entire account (所有项目)"
Write-Host "6. 点击 'Generate token'"
Write-Host "7. 复制生成的 token (格式: pypi-xxxxxxxxxx)"
Write-Host ""
Write-Host "步骤 2: 配置 Token" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
Write-Host "在 PowerShell 中运行:"
Write-Host ""
Write-Host '`$env:TWINE_USERNAME = "__token__"' -ForegroundColor Green
Write-Host '`$env:TWINE_PASSWORD = "pypi-你的token"' -ForegroundColor Green
Write-Host ""
Write-Host "或者永久保存 (推荐):"
Write-Host ""
Write-Host "notepad $PROFILE" -ForegroundColor Green
Write-Host ""
Write-Host "添加以下内容:"
Write-Host 'Export TWINE_USERNAME="__token__"' -ForegroundColor Gray
Write-Host 'Export TWINE_PASSWORD="pypi-你的token"' -ForegroundColor Gray
Write-Host ""
Write-Host "步骤 3: 上传到 TestPyPI (先测试)" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
Write-Host ""
Write-Host "python -m twine upload --repository testpypi dist/*" -ForegroundColor Green
Write-Host ""
Write-Host "步骤 4: 验证测试安装" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
Write-Host ""
Write-Host "pip install --index-url https://test.pypi.org/simple/ ReadmeMagic" -ForegroundColor Green
Write-Host ""
Write-Host "步骤 5: 上传到正式 PyPI" -ForegroundColor Yellow
Write-Host "-------------------------------------------"
Write-Host ""
Write-Host "python -m twine upload dist/*" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "本地测试 (不需要 PyPI)" -ForegroundColor Yellow
Write-Host "========================================"
Write-Host ""
Write-Host "安装到本地:"
Write-Host "pip install -e ." -ForegroundColor Green
Write-Host ""
Write-Host "测试 CLI:"
Write-Host "readme-magic --help" -ForegroundColor Green
Write-Host ""
