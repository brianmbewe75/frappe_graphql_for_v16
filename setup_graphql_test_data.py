"""
Setup test data for GraphQL testing
Creates three DocTypes: Animals, Cars, and Fruits
Each with 10 sample records
"""

import frappe
from frappe import _


def create_test_doctypes():
    """Create three DocTypes for GraphQL testing"""
    
    # 1. Animals DocType
    if not frappe.db.exists("DocType", "Animal"):
        animal_doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Animal",
            "module": "Custom",
            "custom": 1,
            "is_submittable": 0,
            "istable": 0,
            "issingle": 0,
            "autoname": "field:animal_name",
            "fields": [
                {
                    "fieldname": "animal_name",
                    "fieldtype": "Data",
                    "label": "Animal Name",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                },
                {
                    "fieldname": "animal_type",
                    "fieldtype": "Select",
                    "label": "Animal Type",
                    "options": "Mammal\nBird\nReptile\nAmphibian\nFish\nInsect",
                    "in_list_view": 1
                },
                {
                    "fieldname": "habitat",
                    "fieldtype": "Data",
                    "label": "Habitat",
                    "in_list_view": 1
                },
                {
                    "fieldname": "description",
                    "fieldtype": "Small Text",
                    "label": "Description"
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                },
                {
                    "role": "Guest",
                    "read": 1
                }
            ]
        })
        animal_doc.insert(ignore_permissions=True)
        print("✅ Created Animal DocType")
    else:
        print("ℹ️  Animal DocType already exists")
    
    # 2. Car DocType
    if not frappe.db.exists("DocType", "Car"):
        car_doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Car",
            "module": "Custom",
            "custom": 1,
            "is_submittable": 0,
            "istable": 0,
            "issingle": 0,
            "autoname": "field:car_name",
            "fields": [
                {
                    "fieldname": "car_name",
                    "fieldtype": "Data",
                    "label": "Car Name",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                },
                {
                    "fieldname": "brand",
                    "fieldtype": "Data",
                    "label": "Brand",
                    "in_list_view": 1
                },
                {
                    "fieldname": "model_year",
                    "fieldtype": "Int",
                    "label": "Model Year",
                    "in_list_view": 1
                },
                {
                    "fieldname": "car_type",
                    "fieldtype": "Select",
                    "label": "Car Type",
                    "options": "Sedan\nSUV\nHatchback\nCoupe\nConvertible\nTruck",
                    "in_list_view": 1
                },
                {
                    "fieldname": "price",
                    "fieldtype": "Currency",
                    "label": "Price"
                },
                {
                    "fieldname": "description",
                    "fieldtype": "Small Text",
                    "label": "Description"
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                },
                {
                    "role": "Guest",
                    "read": 1
                }
            ]
        })
        car_doc.insert(ignore_permissions=True)
        print("✅ Created Car DocType")
    else:
        print("ℹ️  Car DocType already exists")
    
    # 3. Fruit DocType
    if not frappe.db.exists("DocType", "Fruit"):
        fruit_doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Fruit",
            "module": "Custom",
            "custom": 1,
            "is_submittable": 0,
            "istable": 0,
            "issingle": 0,
            "autoname": "field:fruit_name",
            "fields": [
                {
                    "fieldname": "fruit_name",
                    "fieldtype": "Data",
                    "label": "Fruit Name",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1
                },
                {
                    "fieldname": "color",
                    "fieldtype": "Data",
                    "label": "Color",
                    "in_list_view": 1
                },
                {
                    "fieldname": "taste",
                    "fieldtype": "Select",
                    "label": "Taste",
                    "options": "Sweet\nSour\nBitter\nSweet-Sour\nNeutral",
                    "in_list_view": 1
                },
                {
                    "fieldname": "season",
                    "fieldtype": "Select",
                    "label": "Season",
                    "options": "Spring\nSummer\nFall\nWinter\nYear-round",
                    "in_list_view": 1
                },
                {
                    "fieldname": "price_per_kg",
                    "fieldtype": "Currency",
                    "label": "Price per KG"
                },
                {
                    "fieldname": "description",
                    "fieldtype": "Small Text",
                    "label": "Description"
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                },
                {
                    "role": "Guest",
                    "read": 1
                }
            ]
        })
        fruit_doc.insert(ignore_permissions=True)
        print("✅ Created Fruit DocType")
    else:
        print("ℹ️  Fruit DocType already exists")
    
    frappe.db.commit()
    print("\n✅ All DocTypes created successfully!")


def create_test_animals():
    """Create 10 sample animals"""
    animals_data = [
        {"animal_name": "Lion", "animal_type": "Mammal", "habitat": "Savanna", "description": "King of the jungle"},
        {"animal_name": "Eagle", "animal_type": "Bird", "habitat": "Mountains", "description": "Majestic bird of prey"},
        {"animal_name": "Dolphin", "animal_type": "Mammal", "habitat": "Ocean", "description": "Intelligent marine mammal"},
        {"animal_name": "Tiger", "animal_type": "Mammal", "habitat": "Jungle", "description": "Striped big cat"},
        {"animal_name": "Penguin", "animal_type": "Bird", "habitat": "Antarctica", "description": "Flightless bird"},
        {"animal_name": "Snake", "animal_type": "Reptile", "habitat": "Various", "description": "Slithering reptile"},
        {"animal_name": "Frog", "animal_type": "Amphibian", "habitat": "Pond", "description": "Jumping amphibian"},
        {"animal_name": "Shark", "animal_type": "Fish", "habitat": "Ocean", "description": "Apex predator"},
        {"animal_name": "Butterfly", "animal_type": "Insect", "habitat": "Garden", "description": "Colorful flying insect"},
        {"animal_name": "Elephant", "animal_type": "Mammal", "habitat": "Savanna", "description": "Largest land mammal"}
    ]
    
    created = 0
    for animal_data in animals_data:
        if not frappe.db.exists("Animal", animal_data["animal_name"]):
            animal = frappe.get_doc({
                "doctype": "Animal",
                **animal_data
            })
            animal.insert(ignore_permissions=True)
            created += 1
    
    frappe.db.commit()
    print(f"✅ Created {created} animals (total: {len(animals_data)})")


def create_test_cars():
    """Create 10 sample cars"""
    cars_data = [
        {"car_name": "Toyota Camry", "brand": "Toyota", "model_year": 2023, "car_type": "Sedan", "price": 28000, "description": "Reliable family sedan"},
        {"car_name": "Honda CR-V", "brand": "Honda", "model_year": 2023, "car_type": "SUV", "price": 32000, "description": "Popular compact SUV"},
        {"car_name": "BMW 3 Series", "brand": "BMW", "model_year": 2024, "car_type": "Sedan", "price": 45000, "description": "Luxury sports sedan"},
        {"car_name": "Ford F-150", "brand": "Ford", "model_year": 2023, "car_type": "Truck", "price": 38000, "description": "Best-selling pickup truck"},
        {"car_name": "Tesla Model 3", "brand": "Tesla", "model_year": 2024, "car_type": "Sedan", "price": 42000, "description": "Electric vehicle"},
        {"car_name": "Mercedes GLC", "brand": "Mercedes", "model_year": 2023, "car_type": "SUV", "price": 48000, "description": "Luxury SUV"},
        {"car_name": "Mazda MX-5", "brand": "Mazda", "model_year": 2023, "car_type": "Convertible", "price": 32000, "description": "Sporty convertible"},
        {"car_name": "Audi A4", "brand": "Audi", "model_year": 2024, "car_type": "Sedan", "price": 41000, "description": "Premium sedan"},
        {"car_name": "Jeep Wrangler", "brand": "Jeep", "model_year": 2023, "car_type": "SUV", "price": 35000, "description": "Off-road capable SUV"},
        {"car_name": "Porsche 911", "brand": "Porsche", "model_year": 2024, "car_type": "Coupe", "price": 110000, "description": "Iconic sports car"}
    ]
    
    created = 0
    for car_data in cars_data:
        if not frappe.db.exists("Car", car_data["car_name"]):
            car = frappe.get_doc({
                "doctype": "Car",
                **car_data
            })
            car.insert(ignore_permissions=True)
            created += 1
    
    frappe.db.commit()
    print(f"✅ Created {created} cars (total: {len(cars_data)})")


def create_test_fruits():
    """Create 10 sample fruits"""
    fruits_data = [
        {"fruit_name": "Apple", "color": "Red", "taste": "Sweet", "season": "Fall", "price_per_kg": 3.50, "description": "Crisp and sweet"},
        {"fruit_name": "Banana", "color": "Yellow", "taste": "Sweet", "season": "Year-round", "price_per_kg": 2.00, "description": "Rich in potassium"},
        {"fruit_name": "Orange", "color": "Orange", "taste": "Sweet-Sour", "season": "Winter", "price_per_kg": 4.00, "description": "High in vitamin C"},
        {"fruit_name": "Strawberry", "color": "Red", "taste": "Sweet", "season": "Spring", "price_per_kg": 8.00, "description": "Small and sweet"},
        {"fruit_name": "Grape", "color": "Purple", "taste": "Sweet", "season": "Fall", "price_per_kg": 6.00, "description": "Small and juicy"},
        {"fruit_name": "Lemon", "color": "Yellow", "taste": "Sour", "season": "Year-round", "price_per_kg": 5.00, "description": "Very sour citrus"},
        {"fruit_name": "Mango", "color": "Yellow", "taste": "Sweet", "season": "Summer", "price_per_kg": 7.50, "description": "Tropical sweet fruit"},
        {"fruit_name": "Pineapple", "color": "Yellow", "taste": "Sweet-Sour", "season": "Summer", "price_per_kg": 4.50, "description": "Tropical fruit"},
        {"fruit_name": "Watermelon", "color": "Green/Red", "taste": "Sweet", "season": "Summer", "price_per_kg": 2.50, "description": "Large and refreshing"},
        {"fruit_name": "Kiwi", "color": "Green", "taste": "Sweet-Sour", "season": "Year-round", "price_per_kg": 9.00, "description": "Small and tangy"}
    ]
    
    created = 0
    for fruit_data in fruits_data:
        if not frappe.db.exists("Fruit", fruit_data["fruit_name"]):
            fruit = frappe.get_doc({
                "doctype": "Fruit",
                **fruit_data
            })
            fruit.insert(ignore_permissions=True)
            created += 1
    
    frappe.db.commit()
    print(f"✅ Created {created} fruits (total: {len(fruits_data)})")


def setup_all():
    """Setup all test data"""
    print("=" * 60)
    print("Setting up GraphQL Test Data")
    print("=" * 60)
    
    print("\n1. Creating DocTypes...")
    create_test_doctypes()
    
    print("\n2. Creating Animals...")
    create_test_animals()
    
    print("\n3. Creating Cars...")
    create_test_cars()
    
    print("\n4. Creating Fruits...")
    create_test_fruits()
    
    print("\n" + "=" * 60)
    print("✅ All test data created successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Generate GraphQL SDL: bench --site plastkort.nu graphql generate_sdl --doctype Animal --doctype Car --doctype Fruit")
    print("2. Test GraphQL queries using the Postman collection")


if __name__ == "__main__":
    setup_all()
