Copy-Item .env.local .env -Force
Write-Host "Switched to LOCAL environment"
python -c "from shared.config import get_business_data_config; print(get_business_data_config())"