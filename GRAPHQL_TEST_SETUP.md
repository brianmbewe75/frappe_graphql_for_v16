# GraphQL Test Setup - Quick Guide

## Overview
This setup creates three simple DocTypes (Animals, Cars, Fruits) with minimal data to test GraphQL functionality.

## Setup Steps

### 1. Create DocTypes (if not already created)
The DocTypes should be created via the Frappe UI or using bench console. They are:
- **Animal** - with fields: `animal_name`, `animal_type`
- **Car** - with fields: `car_name`, `brand`
- **Fruit** - with fields: `fruit_name`, `color`

### 2. Generate GraphQL SDL
After creating the DocTypes, generate the GraphQL schema:

```bash
bench --site plastkort.nu graphql generate_sdl --doctype Animal --doctype Car --doctype Fruit
```

### 3. Create Test Data
You can create test data manually via Frappe UI or use bench console:

**Animals:**
- Lion (Wild)
- Tiger (Wild)
- Eagle (Wild)

**Cars:**
- Toyota Camry (Toyota)
- Honda Civic (Honda)
- BMW 3 (BMW)

**Fruits:**
- Apple (Red)
- Banana (Yellow)
- Orange (Orange)

### 4. Test GraphQL Endpoint

**Endpoint:** `POST /api/method/frappe_graphql.api.execute_gql_query`

**Example Query:**
```json
{
  "query": "query { Animals { edges { node { name animal_name animal_type } } } Cars { edges { node { name car_name brand } } } Fruits { edges { node { name fruit_name color } } } }"
}
```

## Postman Collection

Import `Postman_Collection_GraphQL.json` into Postman to test all queries.

## GraphQL Benefits Demonstrated

1. **Single Endpoint**: One endpoint (`/api/method/frappe_graphql.api.execute_gql_query`) for all queries
2. **Request Only What You Need**: Specify exactly which fields you want
3. **Multiple Resources in One Query**: Query Animals, Cars, and Fruits in a single request
4. **Type Safety**: GraphQL validates queries before execution
5. **Self-Documenting**: Use introspection queries to discover available types

## Example Queries

### Get All Animals
```graphql
query {
  Animals {
    edges {
      node {
        name
        animal_name
        animal_type
      }
    }
  }
}
```

### Get All Three Types
```graphql
query {
  Animals {
    edges {
      node {
        animal_name
      }
    }
  }
  Cars {
    edges {
      node {
        car_name
        brand
      }
    }
  }
  Fruits {
    edges {
      node {
        fruit_name
        color
      }
    }
  }
}
```

### Get Single Record
```graphql
query {
  Animal(name: "Lion") {
    name
    animal_name
    animal_type
  }
}
```

## Troubleshooting

1. **If DocTypes don't appear in GraphQL**: Run the SDL generation command
2. **If queries fail**: Check that the DocType names match (Animal, Car, Fruit - case sensitive)
3. **If no data returned**: Ensure test data exists in Frappe
