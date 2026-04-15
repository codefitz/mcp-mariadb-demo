# Core entities

## ASSET_HOST
Purpose:
- One row per discovered host.

Important identifiers:
- `ID`: numeric primary key
- `GUID`: stable asset identifier used across relationship and UMAP tables
- `NAME`: display or discovered host name
- `HOSTNAME`: short hostname

Important descriptive columns:
- `OS`
- `OS_TYPE`
- `OS_VENDOR`
- `IP_ADDRESS`
- `ALL_IP_ADDRS`

Notes:
- Prefer `GUID` for joins into relationship and UMAP tables.
- `NAME` and `HOSTNAME` may differ.

## ASSET_SOFTWAREINSTANCE
Purpose:
- Stores discovered software instances installed or running on assets.

Important identifiers:
- `ID`: numeric primary key

Important descriptive columns:
- `TYPE`
- `VERSION`
- `RUNNING_ON`

Notes:
- Prefer joining through `ASSET_SOFTWAREINSTANCE_RELATIONSHIP`.
- `RUNNING_ON` is a denormalised helper field and is not the most trusted join key.

## ASSET_SOFTWAREINSTANCE_RELATIONSHIP
Purpose:
- Bridge table linking software instances to parent assets.

Important columns:
- `PARENT_ID`
- `PARENT_GUID`
- `PARENT_KIND`
- `CHILD_ID`
- `CHILD_KIND`

Notes:
- For host-to-software queries, filter by:
  - `PARENT_KIND = 'Host'`
  - `CHILD_KIND = 'SoftwareInstance'`
- Prefer `PARENT_GUID` when joining back to `ASSET_HOST.GUID`.

## UMAP_CI
Purpose:
- Maps assets into logical or CMDB entities.

Important columns:
- `ASSET_GUID`
- `ENVIRONMENT_ID`

## UMAP_ENVIRONMENT
Purpose:
- Stores environment definitions such as Production, Test, and Dev.

Important columns:
- `ID`
- `NAME`

## ASSET_NETWORKINTERFACE
Purpose:
- Stores discovered network interfaces.

Important identifiers:
- `ID` may or may not be present depending on the exact table design.

Important descriptive columns:
- `NAME`
- `DEVICE_ID`
- `IP_ADDRESS`
- `MAC_ADDR` or `MAC_ADDRESS`
- `INTERFACE_NAME`
- `SPEED`

Notes:
- No trusted host foreign key has been confirmed in the current notes.
- Treat host mapping as unresolved unless a bridge table or explicit join column is found in the live schema.
