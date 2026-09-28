// Azure + Azure Databricks — Resource Group contents
// Deploy into an existing RG, or use deploy.sh which creates the RG first.
// Suggested names match the beginner guide:
//   RG: rg-ecomm-pipeline
//   Workspace: adb-ecomm-pipeline
//   Tier: premium (Unity Catalog)

@description('Azure region for the Databricks workspace (use same as resource group).')
param location string = resourceGroup().location

@description('Databricks workspace name')
param workspaceName string = 'adb-ecomm-pipeline'

@description('Databricks pricing tier. Use premium for Unity Catalog.')
@allowed(['standard', 'premium', 'trial'])
param pricingTier string = 'premium'

@description('Managed Resource Group name created by Databricks')
param managedResourceGroupName string = 'databricks-rg-${workspaceName}'

resource workspace 'Microsoft.Databricks/workspaces@2024-05-01' = {
  name: workspaceName
  location: location
  sku: {
    name: pricingTier
  }
  properties: {
    managedResourceGroupId: subscriptionResourceId('Microsoft.Resources/resourceGroups', managedResourceGroupName)
    publicNetworkAccess: 'Enabled'
  }
}

output databricksWorkspaceId string = workspace.id
output databricksWorkspaceName string = workspace.name
output databricksWorkspaceUrl string = workspace.properties.workspaceUrl
output location string = workspace.location
