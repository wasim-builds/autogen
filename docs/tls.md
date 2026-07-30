# Full TLS setup between all nodes

This document provides instructions and examples on how to set up full TLS communication between all nodes in an AutoGen deployment.

## Overview
To secure communication between nodes, we recommend setting up TLS using Azure Load Balancer and Azure Key Vault for certificate management.

## Deployment with Bicep

See the provided `docs/bicep/tls-setup.bicep` file for an example of deploying an Azure Key Vault and Load Balancer with TLS configuration.

1. Create a resource group:
   ```bash
   az group create --name my-autogen-rg --location eastus
   ```
2. Deploy the Bicep template:
   ```bash
   az deployment group create --resource-group my-autogen-rg --template-file docs/bicep/tls-setup.bicep
   ```
3. Configure your AutoGen nodes to use the deployed Load Balancer and certificate for secure communication.
