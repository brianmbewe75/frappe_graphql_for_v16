# GraphQL Returns {} - Troubleshooting

## Issue
GraphQL queries return empty `{}` response.

## Solution Steps

### 1. Verify SDL Files Are Fixed
The SDL files should have these fields in the type definition:
```graphql
type Car implements BaseDocType {
  ...
  parent: BaseDocType
  parentfield: String
  parenttype: String
  ...
}
```

Check files in: `sites/plastkort.nu/doctype_sdls/`

### 2. Restart Bench Server
**CRITICAL:** The GraphQL schema is cached in memory. You MUST restart bench:

```bash
bench restart
```

### 3. Clear Schema Cache (if restart doesn't work)
```python
# In bench console
import frappe_graphql.utils.loader
frappe_graphql.utils.loader.graphql_schemas = {}
frappe.cache().delete_value("graphql_schema")
```

### 4. Test Query
```bash
curl -X POST http://localhost:8000/api/method/frappe_graphql.api.execute_gql_query \
  -H "Content-Type: application/json" \
  -d '{"query": "query { Cars { edges { node { name car_name brand } } } }"}'
```

### 5. Check for Errors
If still getting `{}`, check:
- Bench logs for errors
- GraphQL Error Log in Frappe (if DocType exists)
- Verify data exists: `frappe.get_all("Car")`

## Expected Response
```json
{
  "data": {
    "Cars": {
      "edges": [
        {
          "node": {
            "name": "...",
            "car_name": "Toyota Camry",
            "brand": "Toyota"
          }
        }
      ]
    }
  }
}
```

## Common Issues

1. **Schema not reloaded** → Restart bench
2. **Missing BaseDocType fields** → Regenerate SDL or manually add them
3. **Permission issues** → Check DocType permissions
4. **No data** → Verify records exist in database
