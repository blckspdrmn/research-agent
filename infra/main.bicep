@minLength(2) // ACRの名前が最低5文字（${prefix}acr）なので、prefixは2文字以上
@maxLength(22) // Storageの名前が最大24文字（${prefix}st）なので、prefixは22文字以下
param prefix string // 全リソース共通のprefix

param location string = resourceGroup().location

// Log Analytics（最初の5GB/月まで無料）
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.operationalinsights/2025-07-01/workspaces?pivots=deployment-language-bicep
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2025-07-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

// Azure Container Registry（Standardは12ヶ月無料枠の対象）
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.containerregistry/2025-11-01/registries?pivots=deployment-language-bicep
resource acr 'Microsoft.ContainerRegistry/registries@2025-11-01' = {
  name: '${prefix}acr'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    // 管理者ユーザー（ID+パスワード）は無効。pullはManaged Identityで行う
    adminUserEnabled: false
  }
}

// ACRからイメージをpullするためのManaged Identity（アプリがAzure上で名乗るID。無料）
// https://learn.microsoft.com/ja-jp/entra/identity/managed-identities-azure-resources/overview
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.managedidentity/2024-11-30/userassignedidentities?pivots=deployment-language-bicep
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: '${prefix}-pull'
  location: location
}

// 上記IdentityにACRからのpull roleを与える
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.authorization/2022-04-01/roleassignments?pivots=deployment-language-bicep
// https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/scenarios-rbac
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, pullIdentity.id, 'AcrPull') // role assignment id はGUID必須
  scope: acr // 権限の適用範囲
  properties: {
    principalId: pullIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId( // https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/bicep-functions-resource#subscriptionresourceid-example
      'Microsoft.Authorization/roleDefinitions',
      '7f951dda-4ed3-4680-a7ca-43fe172d538d' // AcrPullロールのid: https://learn.microsoft.com/ja-jp/azure/role-based-access-control/built-in-roles
    )
  }
}

// Storage Account（Blob=レポートPDFの置き場、Queue=リサーチジョブの行列）

// 12ヶ月無料枠の対象は【Blobのみ】: 5GB LRSホットブロック + 読取2万回/書込1万回。
//   https://azure.microsoft.com/ja-jp/pricing/free-services/
// 従量課金は以下のリンク先のとおり
//   Blob : https://azure.microsoft.com/ja-jp/pricing/details/storage/blobs/
//   Queue: https://azure.microsoft.com/ja-jp/pricing/details/storage/queues/

// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.storage/2026-04-01/storageaccounts?pivots=deployment-language-bicep
resource storage 'Microsoft.Storage/storageAccounts@2026-04-01' = {
  name: '${prefix}st'
  location: location
  kind: 'StorageV2' // Blob/Queue/Table/Fileを全部使える汎用型
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
  }
}

// Blobサービス
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.storage/2026-04-01/storageaccounts/blobservices?pivots=deployment-language-bicep
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2026-04-01' = {
  parent: storage
  name: 'default'
}

// Blobサービス内の実際のコンテナ（ファイル置き場）
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.storage/2026-04-01/storageaccounts/blobservices/containers?pivots=deployment-language-bicep
resource reportsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: blobService
  name: 'reports'
  properties: {
    publicAccess: 'None'
  }
}

// Queueサービス
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.storage/2026-04-01/storageaccounts/queueservices?pivots=deployment-language-bicep
resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2026-04-01' = {
  parent: storage
  name: 'default'
}

// リサーチ依頼を積むキュー
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.storage/2026-04-01/storageaccounts/queueservices/queues?pivots=deployment-language-bicep
resource researchQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2026-04-01' = {
  parent: queueService
  name: 'research-jobs'
}

// 処理に失敗し続けたメッセージの隔離先。無いと同じ失敗を無限に繰り返す
resource poisonQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2026-04-01' = {
  parent: queueService
  name: 'research-jobs-poison'
}

// Container Apps 環境（アプリとジョブを載せる土台）
// 月18万vCPU秒/36万GiB秒の無料付与あり: https://azure.microsoft.com/ja-jp/pricing/details/container-apps/
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.app/2026-01-01/managedenvironments?pivots=deployment-language-bicep
resource containerEnv 'Microsoft.App/managedEnvironments@2026-01-01' = {
  name: '${prefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

@secure() // https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/parameters#secure-parameters
param dbAdminPassword string

param myIpAddress string // DBへの接続を許可する自分のIP。curl --ipv4 -s https://api.ipify.orge で調べる

// PostgreSQL Flexible Server（この構成で唯一の固定費源。ただし12ヶ月無料枠の範囲）
// 無料枠: B1ms を月750時間（=1台を24時間稼働してちょうど）+ ストレージ32GB + バックアップ32GB
//   https://azure.microsoft.com/ja-jp/pricing/free-services/
//   https://azure.microsoft.com/ja-jp/pricing/details/postgresql/flexible-server/
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.dbforpostgresql/2025-08-01/flexibleservers?pivots=deployment-language-bicep
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2025-08-01' = {
  name: '${prefix}-pg'
  location: location
  sku: {
    name: 'Standard_B1ms' // B=Burstable / 1=vCPU / m=メモリ増量 / s=Premium SSD対応
    tier: 'Burstable'
  }
  properties: {
    version: '18' // ローカルの postgres:18 と揃える
    administratorLogin: 'appadmin'
    administratorLoginPassword: dbAdminPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled' // FWで絞る
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// DB本体
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.dbforpostgresql/2025-08-01/flexibleservers/databases?pivots=deployment-language-bicep
resource appDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2025-08-01' = {
  parent: postgres
  name: 'research_agent'
}

// DBにFWルールを追加
// https://learn.microsoft.com/ja-jp/azure/postgresql/flexible-server/concepts-networking-public
// https://learn.microsoft.com/ja-jp/azure/postgresql/flexible-server/concepts-firewall-rules
// https://learn.microsoft.com/ja-jp/azure/templates/microsoft.dbforpostgresql/2025-08-01/flexibleservers/firewallRules?pivots=deployment-language-bicep

// ① 自分のMacから繋ぐ（psqlコマンドによるDB確認用）
resource allowMyIp 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2025-08-01' = {
  parent: postgres
  name: 'AllowMyHome'
  properties: {
    startIpAddress: myIpAddress
    endIpAddress: myIpAddress
  }
}

// ② Container Appsから繋ぐ
resource allowAzureServices 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2025-08-01' = {
  parent: postgres
  name: 'AllowAllAzureServices'
  properties: { // Container Appsの送信IPが固定できないため、他のサブスクリプション含めてAzureからのすべての接続を許可するようにファイアウォールを構成（パスワードによる認証は設定する）
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}
