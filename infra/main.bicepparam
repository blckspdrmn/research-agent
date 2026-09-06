using 'main.bicep'

// 以下は別途ターミナルでexportしておく
param prefix = readEnvironmentVariable('AZ_PREFIX')
param location = readEnvironmentVariable('AZ_LOCATION')
param dbAdminPassword = readEnvironmentVariable('DB_ADMIN_PASSWORD')
param myIpAddress = readEnvironmentVariable('MY_IP')
