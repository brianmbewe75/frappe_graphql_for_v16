"""Quick setup for GraphQL test data - simple version"""
import frappe

# Create Animals DocType
if not frappe.db.exists("DocType", "Animal"):
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Animal",
        "module": "Custom",
        "custom": 1,
        "fields": [
            {"fieldname": "animal_name", "fieldtype": "Data", "label": "Animal Name", "reqd": 1, "unique": 1},
            {"fieldname": "animal_type", "fieldtype": "Data", "label": "Type"}
        ],
        "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}, {"role": "Guest", "read": 1}]
    })
    doc.insert(ignore_permissions=True)
    print("✅ Created Animal DocType")

# Create Cars DocType
if not frappe.db.exists("DocType", "Car"):
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Car",
        "module": "Custom",
        "custom": 1,
        "fields": [
            {"fieldname": "car_name", "fieldtype": "Data", "label": "Car Name", "reqd": 1, "unique": 1},
            {"fieldname": "brand", "fieldtype": "Data", "label": "Brand"}
        ],
        "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}, {"role": "Guest", "read": 1}]
    })
    doc.insert(ignore_permissions=True)
    print("✅ Created Car DocType")

# Create Fruits DocType
if not frappe.db.exists("DocType", "Fruit"):
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Fruit",
        "module": "Custom",
        "custom": 1,
        "fields": [
            {"fieldname": "fruit_name", "fieldtype": "Data", "label": "Fruit Name", "reqd": 1, "unique": 1},
            {"fieldname": "color", "fieldtype": "Data", "label": "Color"}
        ],
        "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}, {"role": "Guest", "read": 1}]
    })
    doc.insert(ignore_permissions=True)
    print("✅ Created Fruit DocType")

frappe.db.commit()

# Create 3 animals
animals = ["Lion", "Tiger", "Eagle"]
for name in animals:
    if not frappe.db.exists("Animal", name):
        frappe.get_doc({"doctype": "Animal", "animal_name": name, "animal_type": "Wild"}).insert(ignore_permissions=True)
print(f"✅ Created {len(animals)} animals")

# Create 3 cars
cars = [{"name": "Toyota Camry", "brand": "Toyota"}, {"name": "Honda Civic", "brand": "Honda"}, {"name": "BMW 3 Series", "brand": "BMW"}]
for car in cars:
    if not frappe.db.exists("Car", car["name"]):
        frappe.get_doc({"doctype": "Car", "car_name": car["name"], "brand": car["brand"]}).insert(ignore_permissions=True)
print(f"✅ Created {len(cars)} cars")

# Create 3 fruits
fruits = [{"name": "Apple", "color": "Red"}, {"name": "Banana", "color": "Yellow"}, {"name": "Orange", "color": "Orange"}]
for fruit in fruits:
    if not frappe.db.exists("Fruit", fruit["name"]):
        frappe.get_doc({"doctype": "Fruit", "fruit_name": fruit["name"], "color": fruit["color"]}).insert(ignore_permissions=True)
print(f"✅ Created {len(fruits)} fruits")

frappe.db.commit()
print("\n✅ All done! Ready for GraphQL testing")
