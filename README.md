# Frappe GraphQL (Refined for Frappe v16)

GraphQL API Layer for Frappe Framework - Refined and adapted for Frappe v16 compatibility.

## Inspiration & Source

This version is **inspired by and prepared based on** the original work by [Leam Technology Systems](https://github.com/leam-tech/frappe_graphql).

**Original Source:** https://github.com/leam-tech/frappe_graphql

## What's Changed

This refined version includes fixes and improvements for:
- **Frappe v16 compatibility** - Updated imports and module structure
- **Namespace package issues** - Fixed Python import path problems
- **Error handling** - Improved error logging and graceful degradation
- **Schema processors** - Made optional to prevent import failures

## Installation

```bash
bench get-app frappe_graphql <your-repo-url>
bench --site <site-name> install-app frappe_graphql
```

## Setup

Generate the SDLs first:

```bash
bench --site <site-name> graphql generate_sdl
```

## Usage

Start making your GraphQL requests against:

```
/api/method/graphql
```

## Features

- ✅ Single Document queries (`<doctype>`)
- ✅ Filtered DocType lists (`<doctype-plural>`)
- ✅ Nested queries for linked documents
- ✅ Cursor-based pagination
- ✅ Role-based permissions integration
- ✅ Standard mutations (set_value, save_doc, delete_doc)
- ✅ File uploads
- ✅ Custom schema extensions via hooks

## Example Queries

### Get a single document
```graphql
{
    User(name: "Administrator") {
        name,
        email
    }
}
```

### Get filtered list
```graphql
{
    Users(filter: [["name", "like", "%a%"]], sortBy: { field: NAME, direction: ASC }) {
        totalCount,
        edges {
            node {
                name,
                first_name
            }
        }
    }
}
```

### Nested queries
```graphql
{
    ToDo(limit_page_length: 1) {
        name,
        priority,
        assigned_by {
            full_name
        }
    }
}
```

## Configuration

### Hooks

Add to your app's `hooks.py`:

```python
# GraphQL SDL directories
graphql_sdl_dir = [
    "./your-app/your-app/graphql"
]

# Schema processors
graphql_schema_processors = [
    "your-app.your-app.graphql.processors.bind_custom_queries"
]

# Middlewares
graphql_middlewares = [
    "frappe_graphql.utils.middlewares.disable_introspection_queries.disable_introspection_queries"
]
```

## License

MIT (same as original)

## Credits

- **Original Work:** [Leam Technology Systems](https://github.com/leam-tech/frappe_graphql)
- **Refined for:** Frappe v16 compatibility
- **Maintainer:** Your Organization

## Notes

This is a refined version prepared to work with Frappe v16. Some advanced features (like subscriptions and certain schema processors) may require additional setup or may be disabled if dependencies are not available.
