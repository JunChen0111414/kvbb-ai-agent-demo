Copy-Item .env.azure .env -Force
Write-Host "Switched to AZURE environment"
python -c "from shared.config import get_business_data_config; print(get_business_data_config())"