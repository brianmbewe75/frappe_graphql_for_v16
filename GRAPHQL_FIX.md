# GraphQL Query Returns {} - Fixed

## Problem
When querying for Cars (or Animals/Fruits), you get an empty `{}` response.

## Root Cause
The generated GraphQL SDL files were missing required fields from the `BaseDocType` interface:
- `parent: BaseDocType`
- `parentfield: String`
- `parenttype: String`

## Solution Applied
Fixed the SDL files in `/home/frappe/frappe-bench/sites/plastkort.nu/doctype_sdls/`:
- `car.graphql` ✅
- `animal.graphql` ✅
- `fruit.graphql` ✅

## Next Steps

### 1. Restart Bench Server
The GraphQL schema is cached in memory. You need to restart bench:

```bash
bench restart
```

### 2. Test Your Query
After restart, test with:

```json
{
  "query": "query { Cars { edges { node { name car_name brand } } } }"
}
```

**Endpoint:** `POST /api/method/frappe_graphql.api.execute_gql_query`

### 3. Expected Result
You should now get data like:
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
        },
        ...
      ]
    }
  }
}
```

## Note
If you regenerate SDL files in the future, make sure the generator includes these BaseDocType fields. The issue is in the SDL generation code that should be fixed upstream.
