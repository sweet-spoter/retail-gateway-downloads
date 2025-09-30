# Retail Gateway Platform - MSI Installer Downloads

This repository contains the latest MSI installer packages for the Retail Gateway Platform.

## 📦 Available MSI Installers

### Latest Version (1.1.0)
- **Proxy Service**: [GatewayProxyService-v1.1.0.msi](proxy-service/latest/GatewayProxyService-v1.1.0.msi)
- **Gateway Service**: [GatewayLaneService-v1.1.0.msi](gateway-service/latest/GatewayLaneService-v1.1.0.msi)

### Metadata
- **Proxy Metadata**: [metadata.json](proxy-service/latest/metadata.json)
- **Gateway Metadata**: [metadata.json](gateway-service/latest/metadata.json)

### Version History
- [Proxy Service v1.1.0](proxy-service/1.1.0/)
- [Gateway Service v1.1.0](gateway-service/1.1.0/)

## 📋 Installation Instructions

### Windows (MSI Installers)
1. Download [GatewayProxyService-v1.1.0.msi](proxy-service/latest/GatewayProxyService-v1.1.0.msi)
2. Download [GatewayLaneService-v1.1.0.msi](gateway-service/latest/GatewayLaneService-v1.1.0.msi)
3. Run each MSI file as Administrator
4. Both services will be installed as Windows Services and start automatically

### Silent Installation
```cmd
msiexec /i GatewayProxyService-v1.1.0.msi /quiet
msiexec /i GatewayLaneService-v1.1.0.msi /quiet
```

## 🔗 Integration

This repository is automatically updated when new MSI installers are built in the main project.

**Last Updated**: 2025-09-30 00:34:36 UTC
**Source Repository**: [retail-gateway-platform](https://github.com/sweet-spoter/retail-gateway-platform)
