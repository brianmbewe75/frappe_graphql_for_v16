# Plastkort GraphQL API Documentation

## Overview

This GraphQL API provides a single endpoint that covers all REST API functionality. All operations from the REST API have been converted to GraphQL queries and mutations.

**✅ Status:** Fully functional and tested  
**📍 App Location:** `plastkort_custom` app  
**🔧 Data Sources:**
- **Products**: Retrieved from `Item` doctype in Frappe (with PostgreSQL cache layer)
- **Orders**: Retrieved from `Sales Order` doctype in Frappe
- **Carts**: Stored in PostgreSQL `shopping_carts` table
- **Customers**: Retrieved from `Customer` doctype in Frappe

**Data Sources:**
- **Products**: Retrieved from `Item` doctype in Frappe (with PostgreSQL cache layer)
- **Orders**: Retrieved from `Sales Order` doctype in Frappe
- **Carts**: Stored in PostgreSQL `shopping_carts` table
- **Customers**: Retrieved from `Customer` doctype in Frappe

## Endpoint

```
POST /api/method/graphql
```

Or via Frappe's standard method API:
```
POST /api/method/frappe_graphql.api.execute_gql_query
```

## Authentication

- **Public Queries**: Health check, products, categories (no auth required)
- **Authenticated Queries**: Carts, orders, customer profile (Bearer token in Authorization header)
- **Public Mutations**: Customer registration, session creation (no auth required)
- **Authenticated Mutations**: Cart operations, order operations (Bearer token required)

## Standard Response Format

### Success Response
```json
{
  "data": {
    "queryName": { ... }
  }
}
```

### Error Response
```json
{
  "errors": [
    {
      "message": "Error message",
      "locations": [...],
      "path": [...]
    }
  ]
}
```

---

## Quick Reference - All Available Operations

### Queries (Read Operations)
- `health` - System health check
- `products` - List products with pagination, search, and category filters
- `product` - Get single product by item_code
- `categories` - List all product categories
- `cart` - Get shopping cart by session_id or customer_id
- `session` - Get session details
- `order` - Get order by order_id
- `orders` - List orders with filters
- `orderReferences` - List order references
- `orderReference` - Get order reference
- `customerProfile` - Get customer profile
- `apiClient` - Get API client
- `apiClients` - List API clients
- `apiKeys` - List API keys

### Mutations (Write Operations)
- `registerCustomer` - Register/update customer
- `createSession` - Create customer portal session
- `updateSessionData` - Update session data
- `createCart` - Create shopping cart
- `addCartItem` - Add item to cart
- `updateCartItem` - Update cart item quantity
- `removeCartItem` - Remove item from cart
- `clearCart` - Clear all items from cart
- `createOrder` - Create order from cart
- `updateOrder` - Update order (draft only)
- `cancelOrder` - Cancel order
- `syncProductFromFrappe` - Sync product from Frappe
- `createCategory` - Create product category
- `createApiClient` - Create API client
- `revokeApiKey` - Revoke API key
- `createOAuthToken` - Create OAuth token
- `revokeOAuthToken` - Revoke OAuth token

---

## Queries

### Health Check

```graphql
query {
  health {
    postgresql
    frappe
    status
  }
}
```

### Register Customer

```graphql
mutation {
  registerCustomer(input: {
    email: "customer@example.com"
    first_name: "John"
    last_name: "Doe"
    company_name: "Doe Industries AB"
    phone: "+46 70 123 4567"
    address_line1: "Main Street 123"
    city: "Stockholm"
    pincode: "111 22"
    country: "Sweden"
  }) {
    customer_id
    lead_id
    contact_id
    registration_status
    message
  }
}
```

### Create Session

```graphql
mutation {
  createSession(input: {
    email: "customer@example.com"
    customer_id: "CUST-00001"
    expires_in_hours: 24
  }) {
    id
    session_id
    customer_id
    email
    expires_at
    created_at
  }
}
```

**Note:** Either `email` or `customer_id` can be provided. For guest sessions, use `email`. For authenticated customers, use `customer_id`.

### Get Session

```graphql
query {
  session(session_id: "your-session-id") {
    id
    session_id
    customer_id
    email
    session_data
    cart_id
    expires_at
    created_at
  }
}
```

### Update Session Data

```graphql
mutation {
  updateSessionData(input: {
    session_id: "your-session-id"
    session_data: "{\"preferences\": {\"theme\": \"dark\"}}"
    cart_id: "cart-uuid"
  }) {
    id
    session_id
    session_data
    cart_id
  }
}
```

**Note:** 
- `session_data` should be a JSON string (e.g., `"{\"key\": \"value\"}"`)
- `cart_id` is optional - use it to link a cart to the session
- The resolver automatically parses the JSON string before sending to the REST API

### List Products

```graphql
query {
  products(
    category: "Products"
    search: "PVC"
    page: 1
    page_size: 20
  ) {
    products {
      id
      item_code
      item_name
      description
      price
      stock_qty
    }
    pagination {
      page
      page_size
      total
      pages
    }
  }
}
```

### Get Product

```graphql
query {
  product(item_code: "TEST-PVC-003") {
    id
    item_code
    item_name
    description
    price
    stock_qty
    item_group
    category
  }
}
```

**Note:** Replace `TEST-PVC-003` with an actual item code from your system (e.g., TEST-MEMBERSHIP-001, TEST-BADGE-001). If not in cache, it will be automatically fetched from Frappe.

### List Categories

```graphql
query {
  categories {
    id
    name
    description
    parent_category_id
  }
}
```

**Note:** Categories are automatically generated from Item Groups in Frappe. If the PostgreSQL cache is empty, it will fetch unique item groups from your Items and cache them.

### Get Cart

```graphql
query {
  cart(session_id: "session_123") {
    id
    items {
      id
      item_code
      item_name
      quantity
      unit_price
    }
    subtotal
    item_count
    total_quantity
  }
}
```

### Create Cart

```graphql
mutation {
  createCart(input: {
    session_id: "session_123"
    email: "customer@example.com"
  }) {
    id
    session_id
    email
    item_count
  }
}
```

### Add Item to Cart

```graphql
mutation {
  addCartItem(input: {
    cart_id: "cart-uuid"
    item_code: "TEST-PVC-003"
    quantity: 2
    unit_price: 5.00
    session_id: "your-session-id"
  }) {
    id
    item_code
    quantity
    unit_price
    item_name
  }
}
```

**Parameters:**
- `cart_id` (required): The cart ID to add item to
- `item_code` (required): Product item code (e.g., "TEST-PVC-003", "TEST-MEMBERSHIP-001")
- `quantity` (required): Quantity to add (must be > 0)
- `unit_price` (optional): Price per unit (auto-fetched from product cache or Frappe if missing)
- `item_name` (optional): Item name (auto-fetched from Frappe if missing)
- `configurator_data` (optional): Product configuration JSON string
- `session_id` (optional but recommended): Session ID for validation - ensures cart belongs to this session
- `customer_id` (optional): Customer ID for validation - ensures cart belongs to this customer

**Behavior:**
- If the item already exists in the cart, the quantity is **added** to the existing quantity (not replaced)
- If `unit_price` is not provided, it's automatically fetched from the product cache or Frappe
- If `item_name` is not provided, it's automatically fetched from Frappe

**Security Note:** 
- **Always provide `session_id` or `customer_id`** to ensure users can only add items to their own carts
- Without validation, any user with a `cart_id` could add items to any cart
- The system validates that the cart belongs to the specified session/customer before adding items

**Success Response:**
```json
{
  "data": {
    "addCartItem": {
      "id": "item-uuid",
      "item_code": "TEST-PVC-003",
      "quantity": 2,
      "unit_price": 5.0,
      "item_name": "Premium PVC Card with Chip"
    }
  }
}
```

**Error Responses:**

**`NOT_FOUND: Cart not found or does not belong to this session/customer`**
- **Cause:** The `cart_id` doesn't exist, belongs to a different session, or the cart has expired
- **Solution:** 
  1. Create a new cart: `createCart(input: { session_id: "your-session-id" })`
  2. Or get existing cart: `cart(session_id: "your-session-id") { id }`
  3. Ensure `session_id` matches the cart's session

**`INVALID_QUANTITY: Quantity must be greater than 0`**
- **Cause:** Quantity is 0 or negative
- **Solution:** Use a quantity > 0

**`ITEM_NOT_FOUND: Item {item_code} not found`**
- **Cause:** Product doesn't exist in Frappe
- **Solution:** Use a valid item_code (check with `products` query)

**Example Workflow:**
1. Create a session: `createSession(input: { email: "customer@example.com" })`
2. Create a cart: `createCart(input: { session_id: "session-id" })`
3. Add items: `addCartItem(input: { cart_id: "cart-id", item_code: "TEST-PVC-003", quantity: 2, session_id: "session-id" })`

### Update Cart Item

**⚠️ IMPORTANT: Before updating, get the correct `item_id` from your cart!**

**Step 1: Get your cart items (to find the correct item_id):**
```graphql
query {
  cart(session_id: "your-session-id") {
    id
    items {
      id          # ← Copy THIS id for updateCartItem
      item_code
      item_name
      quantity
      unit_price
    }
  }
}
```

**Step 2: Update the item using the id from Step 1:**
```graphql
mutation {
  updateCartItem(input: {
    item_id: "item-uuid-from-step-1"  # ← Use id from items array above
    quantity: 3
    session_id: "your-session-id"     # ← Must match cart's session
  }) {
    id
    item_code
    quantity
    unit_price
    item_name
  }
}
```

**Parameters:**
- `item_id` (required): The cart item ID to update (get from `getCart` query)
- `quantity` (required): New quantity (must be > 0)
- `session_id` (optional but recommended): Session ID for validation - ensures item belongs to this session
- `customer_id` (optional): Customer ID for validation - ensures item belongs to this customer

**Behavior:**
- **Replaces** the existing quantity with the new quantity (unlike `addCartItem` which adds to existing)
- Only updates the quantity field (other fields like `unit_price` remain unchanged)

**Security Note:** 
- **Always provide `session_id` or `customer_id`** to ensure users can only update items from their own carts
- Without validation, any user with an `item_id` could update items from any cart
- The system validates that the cart item belongs to the specified session/customer before updating

**Success Response:**
```json
{
  "data": {
    "updateCartItem": {
      "id": "item-uuid",
      "item_code": "TEST-PVC-003",
      "quantity": 3,
      "unit_price": 5.0,
      "item_name": "Premium PVC Card with Chip"
    }
  }
}
```

**Error Responses:**

**`NOT_FOUND: Cart item not found or does not belong to this session/customer`**
- **Cause:** The `item_id` doesn't exist, belongs to a different session, or the cart has expired
- **Solution:** 
  1. Query your cart first: `cart(session_id: "your-session-id") { items { id } }`
  2. Use the `id` from the items array
  3. Ensure `session_id` matches the cart's session

**`INVALID_QUANTITY: Quantity must be greater than 0`**
- **Cause:** Quantity is 0 or negative
- **Solution:** Use a quantity > 0, or use `removeCartItem` to remove the item

**`INVALID_REQUEST: No updates provided`**
- **Cause:** Missing `quantity` parameter
- **Solution:** Always provide `quantity` when updating

**Example Workflow:**
1. Get current cart: `cart(session_id: "session-id") { items { id item_code quantity } }`
2. Update item: `updateCartItem(input: { item_id: "item-id", quantity: 5, session_id: "session-id" })`

**Troubleshooting:**
- If you get an error, verify:
  1. The `item_id` is correct (use `getCart` to see current items)
  2. The `session_id` matches the cart's session
  3. The item hasn't been removed already
  4. The quantity is greater than 0

### Remove Cart Item

```graphql
mutation {
  removeCartItem(
    item_id: "item-uuid"
    session_id: "your-session-id"
  )
}
```

**Parameters:**
- `item_id` (required): The cart item ID to remove
- `session_id` (optional): Session ID for validation - ensures item belongs to this session
- `customer_id` (optional): Customer ID for validation - ensures item belongs to this customer

**Response:**
- Returns `true` if the item was successfully removed
- Returns `false` if the item was not found, doesn't belong to the session, or removal failed

**Example Response:**
```json
{
  "data": {
    "removeCartItem": true
  }
}
```

**Security Note:** 
- **Always provide `session_id` or `customer_id`** to ensure users can only remove items from their own carts
- Without validation, any user with an `item_id` could remove items from any cart
- The system validates that the cart item belongs to the specified session/customer before removal

**Example with Session Validation:**
```graphql
mutation {
  removeCartItem(
    item_id: "item-uuid"
    session_id: "your-session-id"
  )
}
```

**Troubleshooting:**
- If you get `false`, check:
  1. The `item_id` is correct (use `getCart` to verify)
  2. The `session_id` matches the cart's session
  3. The item hasn't already been removed

### Clear Cart

```graphql
mutation {
  clearCart(cart_id: "cart-uuid")
}
```

**Response:**
- Returns `true` if the cart was successfully cleared
- Returns `false` if the cart was not found or clearing failed

**Example Response:**
```json
{
  "data": {
    "clearCart": true
  }
}
```

**Note:** This removes all items from the cart but keeps the cart itself. The cart will still exist but will be empty.

### Create Order

**⚠️ IMPORTANT: Customer must be registered before creating an order!**

**Step 1: Register Customer (if not already registered)**
```graphql
mutation {
  registerCustomer(input: {
    email: "customer@example.com"
    first_name: "John"
    last_name: "Doe"
  }) {
    customer_id
  }
}
```

**Step 2: Create Cart**
```graphql
mutation {
  createCart(input: {
    session_id: "your-session-id"
    customer_id: "CUST-00001"
  }) {
    id  # ← Save this cart_id
    session_id
    email
    item_count
  }
}
```

**Step 3: Add Valid Items to Cart**
```graphql
# Add Premium PVC Card
mutation {
  addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-PVC-003"  # ← Valid item code
    quantity: 2
    session_id: "your-session-id"
  }) {
    id
    item_code
    item_name
    quantity
    unit_price
  }
}

# Or add Membership Card
mutation {
  addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-MEMBERSHIP-001"  # ← Valid item code
    quantity: 1
    session_id: "your-session-id"
  }) {
    id
    item_code
    item_name
    quantity
    unit_price
  }
}
```

**Available Valid Item Codes:**
- `TEST-PVC-003` - Premium PVC Card with Chip
- `TEST-MEMBERSHIP-001` - Membership Card
- `TEST-BADGE-001` - Name Badge
- `TEST-PVC-002` - Premium PVC Card with Chip
- `TEST-LANYARD-001` - Standard Lanyard

**Step 4: Create Order**
```graphql
mutation {
  createOrder(input: {
    cart_id: "your-cart-id"  # ← Use the cart_id from Step 2
    customer_id: "CUST-00001"  # Required - from registerCustomer
    payment_mode: "PREPAY"
    notes: "Please deliver to front door"
  }) {
    name
    customer
    status
    total
    grand_total
    items {
      item_code
      item_name
      qty
      rate
      amount
    }
  }
}
```

**Complete Example (Copy-Paste Ready):**
```graphql
# Step 1: Register Customer
mutation {
  registerCustomer(input: {
    email: "customer@example.com"
    first_name: "John"
    last_name: "Doe"
    company_name: "Doe Industries AB"
  }) {
    customer_id  # ← Save: "Doe Industries AB"
  }
}

# Step 2: Create Session
mutation {
  createSession(input: {
    email: "customer@example.com"
  }) {
    session_id  # ← Save this
  }
}

# Step 3: Create Cart
mutation {
  createCart(input: {
    session_id: "your-session-id"
    customer_id: "Doe Industries AB"
  }) {
    id  # ← Save this cart_id
  }
}

# Step 4: Add Valid Item
mutation {
  addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-PVC-003"  # ← Valid item
    quantity: 2
    session_id: "your-session-id"
  }) {
    id
    item_code
    item_name
    quantity
  }
}

# Step 5: Create Order
mutation {
  createOrder(input: {
    cart_id: "your-cart-id"
    customer_id: "Doe Industries AB"
    payment_mode: "PREPAY"
    notes: "Please deliver to front door"
  }) {
    name
    customer
    status
    total
    grand_total
    items {
      item_code
      item_name
      qty
      rate
      amount
    }
  }
}
```

**Parameters:**
- `cart_id` (conditional): Cart UUID (required if session_id and customer_id not provided)
- `session_id` (conditional): Session ID (required if cart_id and customer_id not provided)
- `customer_id` (conditional but recommended): Customer ID from `registerCustomer` (required if cart_id and session_id not provided)
- `payment_mode` (optional): Payment mode (e.g., "PREPAY", "AFTERPAY")
- `notes` (optional): Order notes

**Note:** At least one of `cart_id`, `session_id`, or `customer_id` must be provided. **Always provide `customer_id`** to ensure the order is linked to the correct customer.

**Success Response:**
```json
{
  "data": {
    "createOrder": {
      "name": "SAL-ORD-2026-00005",
      "customer": "Test Customer",
      "status": "To Deliver and Bill",
      "total": 10.0,
      "grand_total": 10.0,
      "items": [
        {
          "item_code": "TEST-PVC-003",
          "item_name": "Premium PVC Card with Chip",
          "qty": 2.0,
          "rate": 5.0,
          "amount": 10.0
        }
      ]
    }
  }
}
```

**Error Responses:**

**`CART_NOT_FOUND: Cart not found or expired`**
- **Cause:** The cart doesn't exist, has expired (30 days), or was already used to create an order
- **Solution:** 
  1. **Check if cart exists:** `cart(session_id: "your-session-id") { id items { id } }`
  2. **If cart doesn't exist:** Create a new cart: `createCart(input: { session_id: "..." })`
  3. **If cart expired:** Carts expire after 30 days - create a new cart
  4. **If cart was used:** Carts are automatically cleared after successful order creation - create a new cart for another order

**`NO_VALID_ITEMS: No valid items found in cart`**
- **Cause:** Cart contains items that don't exist in Frappe (invalid `item_code`)
- **Solution:**
  1. **Check cart items:** `cart(session_id: "your-session-id") { items { item_code item_name } }`
  2. **Remove invalid items:** `removeCartItem(input: { item_id: "..." session_id: "..." })`
  3. **Add valid items only:** Use valid item codes like:
     - `TEST-PVC-003` - Premium PVC Card with Chip
     - `TEST-MEMBERSHIP-001` - Membership Card
     - `TEST-BADGE-001` - Name Badge
     - `TEST-PVC-002` - Premium PVC Card with Chip
     - `TEST-LANYARD-001` - Standard Lanyard
  4. **Verify item exists:** Query `products(item_code: "TEST-PVC-003") { item_code }` before adding to cart

**`EMPTY_CART: Cart is empty`**
- **Cause:** No items in the cart
- **Solution:** Add items using `addCartItem` before creating order

**`CUSTOMER_REQUIRED: Customer not found. Please register or provide customer_id`**
- **Cause:** Customer must be registered before creating an order
- **Solution:** 
  1. Register customer first: `registerCustomer(input: { email: "..." })`
  2. Use the `customer_id` from the response in `createOrder`

**Important Notes:**
- **Carts are deleted after order creation** - you cannot reuse a cart_id after creating an order
- **Carts expire after 30 days** - create a new cart if expired
- **Always create a fresh cart** for each new order
- **Customer must be registered** before creating an order

### Get Order

```graphql
query {
  order(order_id: "SO-00001") {
    name
    customer
    customer_name
    status
    total
    grand_total
    delivery_date
    items {
      item_code
      item_name
      qty
      rate
      amount
    }
  }
}
```

### List Orders

```graphql
query {
  orders(
    customer_id: "CUST-00001"
    status: "Submitted"
    page: 1
    page_size: 20
  ) {
    orders {
      id
      order_id
      customer_id
      status
      total
      created_at
    }
    pagination {
      page
      page_size
      total
      pages
    }
  }
}
```

### Update Order

```graphql
mutation {
  updateOrder(input: {
    order_id: "SO-00001"
    notes: "Updated notes"
    delivery_date: "2026-02-01"
  }) {
    name
    notes
    delivery_date
  }
}
```

### Cancel Order

```graphql
mutation {
  cancelOrder(order_id: "SO-00001") {
    name
    status
  }
}
```

### Create Session

```graphql
mutation {
  createSession(input: {
    email: "customer@example.com"
    expires_in_hours: 24
  }) {
    id
    session_id
    email
    expires_at
  }
}
```

### Create OAuth Token

```graphql
mutation {
  createOAuthToken(input: {
    customer_id: "CUST-00001"
    expires_in: 3600
  }) {
    id
    access_token
    expires_at
  }
}
```

### List Categories

```graphql
query {
  categories(parent_category_id: null) {
    id
    name
    description
    parent_category_id
  }
}
```

### Get Customer Profile

```graphql
query {
  customerProfile(customer_id: "CUST-00001") {
    customer_id
    customer_name
    email
    phone
    address
    preferences
  }
}
```

---

## Complete Example: Shopping Flow

### 1. Register Customer
```graphql
mutation {
  registerCustomer(input: {
    email: "john@example.com"
    first_name: "John"
    last_name: "Doe"
    company_name: "Doe Industries AB"
    phone: "+46 70 123 4567"
    address_line1: "Main Street 123"
    city: "Stockholm"
    pincode: "111 22"
    country: "Sweden"
  }) {
    customer_id
    lead_id
    contact_id
    registration_status
    message
  }
}
```

### 2. Create Session
```graphql
mutation {
  createSession(input: {
    email: "john@example.com"
  }) {
    session_id
  }
}
```

### 3. Create Cart
```graphql
mutation {
  createCart(input: {
    session_id: "session_123"
  }) {
    id
  }
}
```

### 4. Add Items to Cart
```graphql
mutation {
  addCartItem(input: {
    cart_id: "cart-uuid"
    item_code: "ITEM-001"
    quantity: 2
  }) {
    id
    quantity
  }
}
```

### 5. Get Cart
```graphql
query {
  cart(session_id: "session_123") {
    id
    items {
      item_code
      item_name
      quantity
      unit_price
    }
    subtotal
  }
}
```

### 6. Create Order
```graphql
mutation {
  createOrder(input: {
    cart_id: "cart-uuid"
    payment_mode: "PREPAY"
  }) {
    name
    status
    total
  }
}
```

---

## Error Handling

All errors follow GraphQL error format:

```json
{
  "errors": [
    {
      "message": "Cart not found",
      "locations": [{"line": 2, "column": 3}],
      "path": ["cart"]
    }
  ]
}
```

Common error codes:
- `CART_NOT_FOUND` - Cart missing or expired
- `EMPTY_CART` - No cart items
- `CUSTOMER_REQUIRED` - Customer missing
- `NOT_FOUND` - Resource not found
- `PERMISSION_DENIED` - Access violation
- `VALIDATION_ERROR` - Invalid input

---

## Testing with cURL

**Health Check:**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { health { postgresql frappe status } }"
  }'
```

**List Products:**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { products(page: 1, page_size: 10) { products { item_code item_name price } pagination { total } } }"
  }'
```

**Add Item to Cart (with Session Validation):**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { addCartItem(input: { cart_id: \"cart-uuid\" item_code: \"TEST-PVC-003\" quantity: 2 session_id: \"session-id\" }) { id item_code quantity unit_price } }"
  }'
```

**Update Cart Item (with Session Validation):**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { updateCartItem(input: { item_id: \"item-uuid\" quantity: 5 session_id: \"session-id\" }) { id quantity unit_price } }"
  }'
```

**Search Products:**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { products(search: \"PVC\", page: 1, page_size: 10) { products { item_code item_name price } pagination { total } } }"
  }'
```

**Create Session:**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createSession(input: { email: \"customer@example.com\" expires_in_hours: 24 }) { id session_id email expires_at created_at } }"
  }'
```

**Update Session Data:**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { updateSessionData(input: { session_id: \"your-session-id\" session_data: \"{\\\"preferences\\\": {\\\"theme\\\": \\\"dark\\\"}}\" }) { id session_id session_data } }"
  }'
```

**Note:** In the JSON string, escape quotes with `\\\"` when embedding JSON in the query string.

**Register Customer:**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { registerCustomer(input: { email: \"test@example.com\" first_name: \"John\" last_name: \"Doe\" }) { customer_id registration_status } }"
  }'
```

**Create Order (with customer_id):**
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createOrder(input: { cart_id: \"cart-uuid\" customer_id: \"CUST-00001\" payment_mode: \"PREPAY\" notes: \"Test order\" }) { name customer status total grand_total items { item_code item_name qty rate amount } } }"
  }'
```

**Note:** Customer must be registered first using `registerCustomer` mutation.

With authentication:
```bash
curl -X POST https://system.plastkort.nu/api/method/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "query": "query { cart(session_id: \"session_123\") { id items { item_code quantity } } }"
  }'
```

---

## GraphQL vs REST API Mapping

| REST Endpoint | GraphQL Operation |
|--------------|-------------------|
| `GET /health` | `query { health }` |
| `POST /auth/sessions` | `mutation { createSession }` |
| `GET /auth/sessions/{id}` | `query { session }` |
| `PATCH /auth/sessions/{id}` | `mutation { updateSessionData }` |
| `POST /register_customer` | `mutation { registerCustomer }` |
| `GET /products` | `query { products }` |
| `GET /products/{code}` | `query { product }` |
| `GET /categories` | `query { categories }` |
| `GET /carts` | `query { cart }` |
| `POST /carts` | `mutation { createCart }` |
| `POST /carts/{id}/items` | `mutation { addCartItem }` |
| `POST /orders` | `mutation { createOrder }` |
| `GET /orders/{id}` | `query { order }` |
| `GET /orders` | `query { orders }` |
| `GET /orders` | `query { orders }` |
| `PATCH /orders/{id}` | `mutation { updateOrder }` |
| `POST /orders/{id}/cancel` | `mutation { cancelOrder }` |

---

## Quick Start Examples

### ✅ Working Product Queries

**Get All Products:**
```graphql
query {
  products(page: 1, page_size: 20) {
    products {
      id
      item_code
      item_name
      price
    }
    pagination {
      total
    }
  }
}
```

**Search Products:**
```graphql
query {
  products(search: "PVC", page: 1, page_size: 20) {
    products {
      item_code
      item_name
      price
    }
    pagination {
      total
    }
  }
}
```

**Filter by Item Group:**
```graphql
query {
  products(category: "Plastic Cards", page: 1, page_size: 20) {
    products {
      item_code
      item_name
      price
    }
    pagination {
      total
    }
  }
}
```

---

## Use Cases & Scenarios

### Scenario 1: Guest Customer - Complete Shopping Flow

**Use Case:** A new visitor browses products, adds items to cart, registers, and creates an order.

```graphql
# Step 1: Browse Products
query {
  products(page: 1, page_size: 20) {
    products {
      item_code
      item_name
      price
      description
      category
    }
    pagination {
      total
      pages
    }
  }
}

# Step 2: Create Guest Session
mutation {
  createSession(input: {
    email: "guest@example.com"
    expires_in_hours: 24
  }) {
    session_id
    id
    email
    expires_at
  }
}

# Step 3: Create Cart
mutation {
  createCart(input: {
    session_id: "your-session-id"
  }) {
    id
    session_id
    item_count
  }
}

# Step 4: Add Items to Cart
mutation {
  addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-PVC-003"
    quantity: 2
    session_id: "your-session-id"
  }) {
    id
    item_code
    item_name
    quantity
    unit_price
    total_price
  }
}

# Step 5: Register Customer (at checkout)
mutation {
  registerCustomer(input: {
    email: "guest@example.com"
    first_name: "John"
    last_name: "Doe"
    company_name: "Doe Industries AB"
    phone: "+46 70 123 4567"
    address_line1: "Main Street 123"
    city: "Stockholm"
    pincode: "111 22"
    country: "Sweden"
  }) {
    customer_id
    registration_status
  }
}

# Step 6: Create Order
mutation {
  createOrder(input: {
    cart_id: "your-cart-id"
    customer_id: "Doe Industries AB"
    payment_mode: "PREPAY"
    notes: "Please deliver to front door"
  }) {
    name
    customer
    status
    total
    grand_total
    items {
      item_code
      item_name
      qty
      rate
      amount
    }
  }
}
```

---

### Scenario 2: Returning Customer - Quick Reorder

**Use Case:** An existing customer logs in, views order history, and creates a new order.

```graphql
# Step 1: Create Session (with customer_id)
mutation {
  createSession(input: {
    customer_id: "Doe Industries AB"
    expires_in_hours: 24
  }) {
    session_id
    customer_id
    email
  }
}

# Step 2: View Order History
query {
  orders(customer_id: "Doe Industries AB", page: 1, page_size: 10) {
    orders {
      order_id
      status
      total
      created_at
    }
    pagination {
      total
      pages
    }
  }
}

# Step 3: Get Previous Order Details
query {
  order(order_id: "SAL-ORD-2026-00007") {
    name
    customer
    status
    items {
      item_code
      item_name
      qty
      rate
    }
  }
}

# Step 4: Create New Cart
mutation {
  createCart(input: {
    session_id: "your-session-id"
    customer_id: "Doe Industries AB"
  }) {
    id
  }
}

# Step 5: Add Items from Previous Order
mutation {
  addCartItem(input: {
    cart_id: "new-cart-id"
    item_code: "TEST-PVC-003"
    quantity: 2
    session_id: "your-session-id"
  }) {
    id
    item_code
    quantity
  }
}

# Step 6: Create Order
mutation {
  createOrder(input: {
    cart_id: "new-cart-id"
    customer_id: "Doe Industries AB"
    payment_mode: "PREPAY"
  }) {
    name
    status
    total
  }
}
```

---

### Scenario 3: Product Search & Discovery

**Use Case:** Customer searches for products, filters by category, and views details.

```graphql
# Search Products by Keyword
query {
  products(search: "PVC", page: 1, page_size: 20) {
    products {
      item_code
      item_name
      description
      price
      category
      stock_quantity
      is_available
    }
    pagination {
      total
      pages
    }
  }
}

# Filter by Category
query {
  products(category: "Products", page: 1, page_size: 20) {
    products {
      item_code
      item_name
      price
    }
  }
}

# Get Product Details
query {
  product(item_code: "TEST-PVC-003") {
    item_code
    item_name
    description
    price
    unit_price
    category
    stock_quantity
    is_available
    images
  }
}

# Browse Categories
query {
  categories {
    id
    name
    description
    parent_category_id
  }
}
```

---

### Scenario 4: Cart Management

**Use Case:** Customer manages cart items - add, update quantities, remove items.

```graphql
# Get Current Cart
query {
  cart(session_id: "your-session-id") {
    id
    item_count
    total_amount
    items {
      id
      item_code
      item_name
      quantity
      unit_price
      total_price
    }
  }
}

# Add Multiple Items
mutation {
  item1: addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-PVC-003"
    quantity: 2
    session_id: "your-session-id"
  }) {
    id
    item_code
    quantity
  }
  
  item2: addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-MEMBERSHIP-001"
    quantity: 1
    session_id: "your-session-id"
  }) {
    id
    item_code
    quantity
  }
}

# Update Item Quantity
mutation {
  updateCartItem(input: {
    item_id: "item-uuid"
    quantity: 5
    session_id: "your-session-id"
  }) {
    id
    quantity
    unit_price
    total_price
  }
}

# Remove Item
mutation {
  removeCartItem(item_id: "item-uuid", session_id: "your-session-id")
}

# Clear Entire Cart
mutation {
  clearCart(cart_id: "your-cart-id")
}
```

---

### Scenario 5: Order Management

**Use Case:** Customer views orders, updates draft orders, and cancels orders.

```graphql
# List All Orders
query {
  orders(customer_id: "Doe Industries AB", page: 1, page_size: 20) {
    orders {
      id
      order_id
      customer_id
      status
      total
      created_at
      updated_at
    }
    pagination {
      page
      page_size
      total
      pages
    }
  }
}

# Filter Orders by Status
query {
  orders(
    customer_id: "Doe Industries AB"
    status: "To Deliver and Bill"
    page: 1
    page_size: 20
  ) {
    orders {
      order_id
      status
      total
    }
  }
}

# Get Order Details
query {
  order(order_id: "SAL-ORD-2026-00007") {
    name
    customer
    customer_name
    status
    transaction_date
    delivery_date
    total
    grand_total
    items {
      item_code
      item_name
      qty
      rate
      amount
    }
    notes
    custom_artwork_status
    custom_proof_status
    created_at
    modified
  }
}

# Update Draft Order
mutation {
  updateOrder(input: {
    order_id: "SAL-ORD-2026-00007"
    notes: "Updated delivery instructions"
    delivery_date: "2026-02-20"
  }) {
    name
    status
    notes
    delivery_date
  }
}

# Cancel Order
mutation {
  cancelOrder(order_id: "SAL-ORD-2026-00007") {
    name
    status
    customer
    total
  }
}
```

---

### Scenario 6: OAuth Token & API Client Management

**Use Case:** Partner integration setup and token management.

```graphql
# Create API Client
mutation {
  createApiClient(input: {
    client_name: "Partner Integration"
    client_type: "partner"
    ip_whitelist: ["192.168.1.1", "10.0.0.1"]
    rate_limit_per_minute: 100
  }) {
    id
    name
    type
    rate_limit_per_minute
    created_at
  }
}

# List API Clients
query {
  apiClients {
    id
    name
    type
    rate_limit_per_minute
    created_at
  }
}

# Create OAuth Token
mutation {
  createOAuthToken(input: {
    customer_id: "Doe Industries AB"
    api_client_id: "client-uuid"
    expires_in: 3600
  }) {
    id
    customer_id
    access_token
    expires_at
    created_at
  }
}

# Revoke OAuth Token
mutation {
  revokeOAuthToken(token_id: "token-uuid")
}
```

---

### Scenario 7: Customer Profile Management

**Use Case:** View and manage customer profile data.

```graphql
# Get Customer Profile
query {
  customerProfile(customer_id: "Doe Industries AB") {
    customer_id
    customer_name
    email
    phone
    address
    preferences
    last_updated
  }
}

# Update Session Data (store preferences)
mutation {
  updateSessionData(input: {
    session_id: "your-session-id"
    session_data: "{\"preferences\": {\"theme\": \"dark\", \"language\": \"en\"}}"
  }) {
    id
    session_id
    session_data
  }
}
```

---

### Scenario 8: Product Sync & Category Management

**Use Case:** Admin syncs products from Frappe and manages categories.

```graphql
# Sync Product from Frappe
mutation {
  syncProductFromFrappe(item_code: "TEST-PVC-003") {
    item_code
    item_name
    description
    unit_price
    category
    stock_quantity
    is_available
  }
}

# Create Product Category
mutation {
  createCategory(
    name: "Premium Cards"
    description: "High-end premium card products"
    parent_category_id: null
  ) {
    id
    name
    description
    parent_category_id
  }
}
```

---

## Error Handling Scenarios

### Scenario 1: Cart Not Found

**Error:**
```json
{
  "errors": [{
    "message": "CART_NOT_FOUND: Cart not found or expired"
  }]
}
```

**Solution:**
```graphql
# Create a new cart
mutation {
  createCart(input: {
    session_id: "your-session-id"
    customer_id: "your-customer-id"
  }) {
    id
  }
}
```

---

### Scenario 2: Invalid Item Code

**Error:**
```json
{
  "errors": [{
    "message": "NO_VALID_ITEMS: No valid items found in cart"
  }]
}
```

**Solution:**
```graphql
# First, verify item exists
query {
  product(item_code: "TEST-PVC-003") {
    item_code
    item_name
    is_available
  }
}

# Then add valid item
mutation {
  addCartItem(input: {
    cart_id: "your-cart-id"
    item_code: "TEST-PVC-003"
    quantity: 2
    session_id: "your-session-id"
  }) {
    id
  }
}
```

---

### Scenario 3: Customer Not Registered

**Error:**
```json
{
  "errors": [{
    "message": "CUSTOMER_REQUIRED: Customer not found. Please register or provide customer_id"
  }]
}
```

**Solution:**
```graphql
# Register customer first
mutation {
  registerCustomer(input: {
    email: "customer@example.com"
    first_name: "John"
    last_name: "Doe"
  }) {
    customer_id
  }
}

# Then create order with customer_id
mutation {
  createOrder(input: {
    cart_id: "your-cart-id"
    customer_id: "Doe Industries AB"
    payment_mode: "PREPAY"
  }) {
    name
  }
}
```

---

### Scenario 4: Order Update Not Allowed

**Error:**
```json
{
  "errors": [{
    "message": "ORDER_NOT_EDITABLE: Order can only be updated when status is 'Draft'. Current status: To Deliver and Bill"
  }]
}
```

**Solution:**
- Only Draft orders can be updated
- Create a new order if you need to make changes
- Or cancel the existing order and create a new one

---

### Scenario 5: Order Cancellation Not Allowed

**Error:**
```json
{
  "errors": [{
    "message": "CANCELLATION_NOT_ALLOWED: Order cannot be cancelled. Current status: Cancelled"
  }]
}
```

**Solution:**
- Orders that are already Cancelled, Completed, or Closed cannot be cancelled
- Check order status first:
```graphql
query {
  order(order_id: "SAL-ORD-2026-00008") {
    name
    status
  }
}
```

---

## Best Practices

### 1. Session Management
- **Always create a session** before creating a cart
- **Store session_id** in your application (localStorage, cookies, etc.)
- **Use session_id** for all cart operations to ensure security
- **Sessions expire after 30 days** - create new session if expired

### 2. Cart Lifecycle
- **Carts are deleted after order creation** - create a new cart for each order
- **Carts expire after 30 days** - create a new cart if expired
- **Always validate session ownership** when adding/updating cart items

### 3. Order Creation
- **Register customer first** before creating order
- **Verify cart has valid items** before creating order
- **Always provide customer_id** in createOrder mutation
- **Store order_id** after successful order creation

### 4. Error Handling
- **Always check for errors** in GraphQL response
- **Handle null responses** gracefully (cart, order, customerProfile can be null)
- **Validate input data** before sending mutations
- **Use error codes** to determine appropriate user action

### 5. Performance
- **Use pagination** for large lists (products, orders)
- **Fetch only required fields** in queries
- **Cache product data** on client side
- **Use orderReferences** for fast order listing

### 6. Security
- **Use session validation** for all cart operations
- **Never expose session_id** in URLs or logs
- **Use OAuth tokens** for authenticated API access
- **Validate customer ownership** before showing orders

---

## Common Patterns

### Pattern 1: Optimistic UI Updates

```graphql
# Add item optimistically
mutation {
  addCartItem(input: {
    cart_id: "cart-id"
    item_code: "TEST-PVC-003"
    quantity: 1
    session_id: "session-id"
  }) {
    id
    quantity
  }
}

# Then refresh cart to get accurate totals
query {
  cart(session_id: "session-id") {
    total_amount
    item_count
  }
}
```

### Pattern 2: Batch Operations

```graphql
# Add multiple items in parallel
mutation {
  item1: addCartItem(input: {
    cart_id: "cart-id"
    item_code: "TEST-PVC-003"
    quantity: 2
    session_id: "session-id"
  }) {
    id
  }
  
  item2: addCartItem(input: {
    cart_id: "cart-id"
    item_code: "TEST-MEMBERSHIP-001"
    quantity: 1
    session_id: "session-id"
  }) {
    id
  }
}
```

### Pattern 3: Conditional Queries

```graphql
# Query with variables
query GetCart($sessionId: String, $customerId: String) {
  cart(session_id: $sessionId, customer_id: $customerId) {
    id
    items {
      id
      item_code
      quantity
    }
  }
}

# Variables:
# {
#   "sessionId": "session-id",
#   "customerId": null
# }
```

---

## Troubleshooting Guide

### Issue: Products returning empty list

**Check:**
1. Verify products exist in Frappe Item doctype
2. Check if products are disabled
3. Try syncing product: `syncProductFromFrappe(item_code: "...")`
4. Check PostgreSQL cache is populated

**Solution:**
```graphql
# Force sync product
mutation {
  syncProductFromFrappe(item_code: "TEST-PVC-003") {
    item_code
    item_name
  }
}

# Then query again
query {
  products(page: 1, page_size: 20) {
    products {
      item_code
      item_name
    }
  }
}
```

---

### Issue: Cart operations failing

**Check:**
1. Verify session exists and is not expired
2. Check session_id matches cart's session_id
3. Verify cart hasn't been used to create an order (carts are deleted after order creation)

**Solution:**
```graphql
# Check session
query {
  session(session_id: "your-session-id") {
    id
    expires_at
  }
}

# Check cart
query {
  cart(session_id: "your-session-id") {
    id
    item_count
  }
}

# If cart doesn't exist, create new one
mutation {
  createCart(input: {
    session_id: "your-session-id"
  }) {
    id
  }
}
```

---

### Issue: Order creation failing

**Check:**
1. Customer is registered
2. Cart has valid items (items exist in Frappe)
3. Cart hasn't expired (30 days)
4. Cart hasn't been used already (carts are deleted after order creation)

**Solution:**
```graphql
# Step 1: Verify customer
mutation {
  registerCustomer(input: {
    email: "customer@example.com"
    first_name: "John"
    last_name: "Doe"
  }) {
    customer_id
  }
}

# Step 2: Check cart
query {
  cart(session_id: "your-session-id") {
    id
    items {
      item_code
      quantity
    }
  }
}

# Step 3: Create order with customer_id
mutation {
  createOrder(input: {
    cart_id: "your-cart-id"
    customer_id: "Doe Industries AB"
    payment_mode: "PREPAY"
  }) {
    name
  }
}
```

---

## Real-World Examples

### Example 1: E-commerce Checkout Flow

```graphql
# Complete checkout flow
mutation CheckoutFlow {
  # 1. Register customer
  register: registerCustomer(input: {
    email: "customer@example.com"
    first_name: "John"
    last_name: "Doe"
    company_name: "Doe Industries AB"
    phone: "+46 70 123 4567"
    address_line1: "Main Street 123"
    city: "Stockholm"
    pincode: "111 22"
    country: "Sweden"
  }) {
    customer_id
  }
  
  # 2. Create session
  session: createSession(input: {
    email: "customer@example.com"
    expires_in_hours: 24
  }) {
    session_id
  }
  
  # 3. Create cart
  cart: createCart(input: {
    session_id: "session-id-from-step-2"
    customer_id: "customer-id-from-step-1"
  }) {
    id
  }
  
  # 4. Add items
  item1: addCartItem(input: {
    cart_id: "cart-id-from-step-3"
    item_code: "TEST-PVC-003"
    quantity: 2
    session_id: "session-id-from-step-2"
  }) {
    id
  }
  
  # 5. Create order
  order: createOrder(input: {
    cart_id: "cart-id-from-step-3"
    customer_id: "customer-id-from-step-1"
    payment_mode: "PREPAY"
    notes: "Please deliver to front door"
  }) {
    name
    status
    total
    grand_total
  }
}
```

---

### Example 2: Order Status Tracking

```graphql
# Track order status over time
query OrderTracking {
  # Get order details
  order(order_id: "SAL-ORD-2026-00007") {
    name
    status
    transaction_date
    delivery_date
    items {
      item_code
      item_name
      qty
    }
    custom_artwork_status
    custom_proof_status
    custom_production_ready
  }
  
  # Get order history
  orders(customer_id: "Doe Industries AB", page: 1, page_size: 10) {
    orders {
      order_id
      status
      total
      created_at
    }
  }
}
```

---

### Example 3: Product Catalog Browsing

```graphql
# Browse product catalog
query ProductCatalog {
  # Get categories
  categories {
    id
    name
    description
  }
  
  # Get products by category
  products(category: "Products", page: 1, page_size: 20) {
    products {
      item_code
      item_name
      description
      price
      stock_quantity
      is_available
    }
    pagination {
      total
      pages
    }
  }
  
  # Get product details
  product(item_code: "TEST-PVC-003") {
    item_code
    item_name
    description
    price
    unit_price
    category
    stock_quantity
    is_available
    images
  }
}
```

---

## API Limits & Constraints

### Cart Limits
- **Cart expiration:** 30 days
- **Cart deletion:** Automatically deleted after order creation
- **Item validation:** Items must exist in Frappe Item doctype

### Order Limits
- **Update restriction:** Only Draft orders can be updated
- **Cancellation restriction:** Cannot cancel Cancelled/Completed/Closed orders
- **Customer requirement:** Customer must be registered before order creation

### Session Limits
- **Session expiration:** Default 24 hours (configurable)
- **Maximum expiration:** 30 days
- **Session validation:** Required for cart operations

### Product Limits
- **Cache TTL:** 1 hour (products are cached in PostgreSQL)
- **Sync requirement:** Use `syncProductFromFrappe` to force refresh
- **Availability:** Only enabled products are returned

---

## Migration from REST API

### REST → GraphQL Mapping

| REST Endpoint | GraphQL Operation | Notes |
|--------------|-------------------|-------|
| `GET /health` | `query { health }` | Same functionality |
| `POST /register_customer` | `mutation { registerCustomer }` | Same parameters |
| `POST /auth/sessions` | `mutation { createSession }` | Same functionality |
| `GET /auth/sessions/{id}` | `query { session }` | Same response |
| `PATCH /auth/sessions/{id}` | `mutation { updateSessionData }` | JSON string for session_data |
| `GET /products` | `query { products }` | Pagination, search, filters |
| `GET /products/{code}` | `query { product }` | Same response |
| `GET /categories` | `query { categories }` | Same response |
| `GET /carts` | `query { cart }` | Use session_id or customer_id |
| `POST /carts` | `mutation { createCart }` | Same functionality |
| `POST /carts/{id}/items` | `mutation { addCartItem }` | Include session_id for validation |
| `PATCH /carts/items/{id}` | `mutation { updateCartItem }` | Include session_id for validation |
| `DELETE /carts/items/{id}` | `mutation { removeCartItem }` | Include session_id for validation |
| `DELETE /carts/{id}` | `mutation { clearCart }` | Same functionality |
| `POST /orders` | `mutation { createOrder }` | Requires customer_id |
| `GET /orders/{id}` | `query { order }` | Same response |
| `GET /orders` | `query { orders }` | Requires customer_id |
| `PATCH /orders/{id}` | `mutation { updateOrder }` | Draft orders only |
| `POST /orders/{id}/cancel` | `mutation { cancelOrder }` | Works for all cancellable orders |

---

**Documentation Version:** 2.0  
**Last Updated:** 2026-01-26  
**GraphQL Endpoint:** `/api/method/graphql`  
**App:** `plastkort_custom`  
**Status:** ✅ Verified Working - Production Ready
