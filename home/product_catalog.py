"""Shopiva's starter master product directory.

This is a broad, editable product taxonomy for sellers. It is intentionally
not presented as an exhaustive list of every manufacturer on earth; sellers
can always choose CUSTOM PRODUCT for anything outside the directory.
"""

CATALOG = [
    ("Phones & Tablets", "Apple", ["iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max", "iPad 10th Gen", "iPad Air", "iPad Pro"]),
    ("Phones & Tablets", "Samsung", ["Galaxy S25", "Galaxy S25+", "Galaxy S25 Ultra", "Galaxy A16", "Galaxy A26", "Galaxy A36", "Galaxy Tab A9", "Galaxy Tab S10"]),
    ("Phones & Tablets", "Tecno", ["CAMON 40", "CAMON 40 Pro", "SPARK 30", "SPARK 30 Pro", "POVA 6", "MEGAPAD 10"]),
    ("Phones & Tablets", "Infinix", ["NOTE 40", "NOTE 40 Pro", "HOT 50", "HOT 50 Pro", "GT 20 Pro", "XPad"]),
    ("Phones & Tablets", "Xiaomi", ["Redmi Note 14", "Redmi Note 14 Pro", "Redmi 14C", "Poco X6", "Poco M6", "Xiaomi Pad 7"]),
    ("Phones & Tablets", "OPPO", ["Reno 12", "Reno 12 Pro", "A5 Pro", "A60", "Pad Neo"]),
    ("Phones & Tablets", "Huawei", ["Nova 12i", "Nova 13", "MatePad 11.5", "Watch GT 5"]),
    ("Phones & Tablets", "Nokia", ["Nokia C32", "Nokia C22", "Nokia G42", "Nokia 3210"]),
    ("Phones & Tablets", "itel", ["A80", "A60s", "P65", "RS4", "City 100"]),

    ("Laptops & Computers", "HP", ["Pavilion 15", "Pavilion x360", "Envy x360", "ProBook 440", "EliteBook 840", "Victus 15"]),
    ("Laptops & Computers", "Dell", ["Inspiron 15", "Inspiron 14", "Vostro 3520", "Latitude 3440", "Latitude 5440", "XPS 13"]),
    ("Laptops & Computers", "Lenovo", ["IdeaPad 1", "IdeaPad 3", "ThinkPad E14", "ThinkPad T14", "Yoga 7", "Legion 5"]),
    ("Laptops & Computers", "ASUS", ["VivoBook 15", "VivoBook 16", "ZenBook 14", "ROG Strix G16", "TUF Gaming A15"]),
    ("Laptops & Computers", "Acer", ["Aspire 3", "Aspire 5", "Swift Go 14", "Nitro V 15", "TravelMate P2"]),
    ("Laptops & Computers", "Apple", ["MacBook Air 13-inch", "MacBook Air 15-inch", "MacBook Pro 14-inch", "MacBook Pro 16-inch", "Mac mini"]),
    ("Laptops & Computers", "Microsoft", ["Surface Laptop", "Surface Pro", "Surface Go"]),

    ("TVs & Home Entertainment", "Samsung", ["Crystal UHD Smart TV", "QLED 4K Smart TV", "Neo QLED 4K TV", "OLED 4K TV"]),
    ("TVs & Home Entertainment", "LG", ["UHD Smart TV", "QNED Smart TV", "OLED evo TV", "NanoCell TV"]),
    ("TVs & Home Entertainment", "Hisense", ["A6 Series 4K TV", "U7 Series Mini-LED TV", "U8 Series Mini-LED TV", "VIDAA Smart TV"]),
    ("TVs & Home Entertainment", "TCL", ["P6 Series 4K TV", "C6 Series QLED TV", "C7 Series QLED TV", "Mini-LED TV"]),
    ("TVs & Home Entertainment", "Sony", ["BRAVIA 3 4K TV", "BRAVIA 5 Mini-LED TV", "BRAVIA 8 OLED TV"]),
    ("TVs & Home Entertainment", "JBL", ["Bar 2.1 Soundbar", "Bar 500 Soundbar", "PartyBox Club 120", "Flip 7 Speaker", "Charge 6 Speaker"]),
    ("TVs & Home Entertainment", "LG", ["S40Q Soundbar", "S65Q Soundbar", "XBOOM Speaker"]),

    ("Cameras & Imaging", "Canon", ["EOS R50", "EOS R10", "EOS R7", "PowerShot V10", "PIXMA G3430 Printer"]),
    ("Cameras & Imaging", "Nikon", ["Z30", "Z50 II", "Z5", "Z6 III", "Coolpix P1100"]),
    ("Cameras & Imaging", "Sony", ["Alpha a6400", "Alpha a6700", "Alpha a7 III", "Alpha a7 IV", "ZV-E10 II"]),
    ("Cameras & Imaging", "GoPro", ["HERO13 Black", "MAX 360", "HERO12 Black"]),
    ("Cameras & Imaging", "DJI", ["Osmo Pocket 3", "Osmo Action 5 Pro", "Mini 4 Pro", "Air 3S"]),

    ("Gaming", "Sony", ["PlayStation 5 Slim", "PlayStation 5 Pro", "DualSense Wireless Controller", "Pulse 3D Headset"]),
    ("Gaming", "Microsoft", ["Xbox Series X", "Xbox Series S", "Xbox Wireless Controller"]),
    ("Gaming", "Nintendo", ["Nintendo Switch OLED", "Nintendo Switch Lite", "Joy-Con Controllers"]),
    ("Gaming", "Logitech", ["G435 Headset", "G502 Gaming Mouse", "G29 Racing Wheel", "G915 Keyboard"]),
    ("Gaming", "Razer", ["BlackWidow Keyboard", "DeathAdder Mouse", "Kraken Headset"]),

    ("Home Appliances", "LG", ["9kg Front Load Washer", "12kg Front Load Washer", "Double Door Refrigerator", "Side-by-Side Refrigerator", "Dual Inverter AC"]),
    ("Home Appliances", "Samsung", ["9kg EcoBubble Washer", "12kg Bespoke Washer", "Double Door Fridge", "Bespoke Refrigerator", "WindFree AC"]),
    ("Home Appliances", "Hisense", ["8kg Front Load Washer", "10kg Front Load Washer", "Combi Refrigerator", "Chest Freezer", "Inverter AC"]),
    ("Home Appliances", "Ramtons", ["8kg Front Load Washer", "Twin Tub Washer", "Double Door Fridge", "Chest Freezer", "Air Conditioner"]),
    ("Home Appliances", "Mika", ["7kg Front Load Washer", "Twin Tub Washer", "Double Door Refrigerator", "Chest Freezer"]),
    ("Home Appliances", "Von Hotpoint", ["Front Load Washer", "Twin Tub Washer", "Double Door Refrigerator", "Chest Freezer", "Microwave Oven"]),

    ("Kitchen Appliances", "Philips", ["Airfryer", "Blender", "Juicer", "Electric Kettle", "Rice Cooker"]),
    ("Kitchen Appliances", "Ramtons", ["Air Fryer", "Blender", "Microwave Oven", "Electric Kettle", "Sandwich Maker", "Food Processor"]),
    ("Kitchen Appliances", "Mika", ["Gas Cooker", "Electric Oven", "Air Fryer", "Blender", "Electric Kettle", "Microwave"]),
    ("Kitchen Appliances", "Von Hotpoint", ["Freestanding Cooker", "Built-in Oven", "Gas Hob", "Microwave", "Air Fryer"]),
    ("Kitchen Appliances", "Bosch", ["Dishwasher", "Built-in Oven", "Induction Hob", "Hand Blender"]),

    ("Furniture", "Generic", ["3-Seater Sofa", "2-Seater Sofa", "Sectional Sofa", "Coffee Table", "TV Stand", "Dining Table", "Dining Chair", "Office Desk", "Office Chair", "Bookshelf", "Wardrobe", "Bedside Table"]),
    ("Mattresses & Bedding", "Silentnight", ["Memory Foam Mattress", "Pocket Spring Mattress", "Orthopedic Mattress"]),
    ("Mattresses & Bedding", "Restonic", ["Orthopedic Mattress", "Pocket Spring Mattress", "Memory Foam Mattress"]),
    ("Mattresses & Bedding", "Generic", ["Single Mattress", "4x6 Mattress", "5x6 Mattress", "6x6 Mattress", "Duvet", "Bedsheet Set", "Pillow", "Blanket"]),

    ("Fashion - Men", "Levi's", ["501 Original Jeans", "511 Slim Jeans", "Trucker Jacket", "Denim Shirt"]),
    ("Fashion - Men", "Nike", ["Dri-FIT T-Shirt", "Sports Shorts", "Tech Fleece Joggers", "Windbreaker Jacket", "Club Hoodie"]),
    ("Fashion - Men", "Adidas", ["Essentials T-Shirt", "Training Shorts", "Tiro Track Pants", "Essentials Hoodie", "Track Jacket"]),
    ("Fashion - Men", "Puma", ["Essentials T-Shirt", "Sweatpants", "Hoodie", "Track Jacket"]),
    ("Fashion - Men", "Generic", ["Men's T-Shirt", "Polo Shirt", "Jeans", "Chinos", "Cargo Pants", "Hoodie", "Sweater", "Jacket", "Shirt", "Suit", "Shorts", "Socks"]),

    ("Fashion - Women", "H&M", ["Basic T-Shirt", "Ribbed Top", "Wide-Leg Trousers", "Denim Jacket", "Knit Dress"]),
    ("Fashion - Women", "Zara", ["Blazer", "Midi Dress", "Wide-Leg Trousers", "Denim Jacket", "Crossbody Bag"]),
    ("Fashion - Women", "Nike", ["Sports Bra", "Leggings", "Dri-FIT T-Shirt", "Running Shorts", "Windrunner Jacket"]),
    ("Fashion - Women", "Adidas", ["Training Leggings", "Sports Bra", "Essentials T-Shirt", "Track Pants", "Hoodie"]),
    ("Fashion - Women", "Generic", ["Women's T-Shirt", "Blouse", "Dress", "Skirt", "Jeans", "Palazzo Trousers", "Leggings", "Sweater", "Jacket", "Jumpsuit", "Handbag", "Scarf"]),

    ("Fashion - Kids", "Adidas", ["Kids T-Shirt", "Kids Tracksuit", "Kids Hoodie", "Kids Shorts"]),
    ("Fashion - Kids", "Nike", ["Kids T-Shirt", "Kids Hoodie", "Kids Joggers", "Kids Shorts"]),
    ("Fashion - Kids", "Generic", ["Kids T-Shirt", "Kids Dress", "Kids Jeans", "Kids Shorts", "Kids Hoodie", "School Sweater", "School Shirt", "School Trousers"]),

    ("Shoes", "Nike", ["Air Force 1", "Air Max", "Air Max Dn", "Pegasus", "Revolution", "Court Vision"]),
    ("Shoes", "Adidas", ["Samba", "Superstar", "Gazelle", "Campus", "Ultraboost", "Duramo"]),
    ("Shoes", "Puma", ["Suede Classic", "RS-X", "Smash", "Velocity Nitro"]),
    ("Shoes", "Skechers", ["Go Walk", "Arch Fit", "D'Lites", "Summits"]),
    ("Shoes", "Bata", ["School Shoes", "Formal Shoes", "Sneakers", "Sandals", "Casual Shoes"]),
    ("Shoes", "Clarks", ["Desert Boot", "Un Aldric", "Bradley Walk", "CourtLite"]),
    ("Shoes", "Generic", ["Men's Sneakers", "Women's Sneakers", "Running Shoes", "School Shoes", "Safety Boots", "Sandals", "Slippers", "Formal Shoes", "Hiking Boots"]),

    ("Beauty & Skincare", "Nivea", ["Body Lotion", "Face Wash", "Deodorant", "Body Cream", "Lip Balm"]),
    ("Beauty & Skincare", "Dove", ["Beauty Bar", "Body Wash", "Body Lotion", "Deodorant"]),
    ("Beauty & Skincare", "Vaseline", ["Petroleum Jelly", "Body Lotion", "Lip Therapy"]),
    ("Beauty & Skincare", "L'Oréal", ["Face Cleanser", "Shampoo", "Conditioner", "Foundation", "Mascara"]),
    ("Beauty & Skincare", "Garnier", ["Micellar Water", "Face Wash", "Sheet Mask", "Vitamin C Serum"]),
    ("Beauty & Skincare", "CeraVe", ["Hydrating Cleanser", "Foaming Cleanser", "Moisturizing Cream", "Facial Moisturizer"]),
    ("Beauty & Skincare", "Maybelline", ["Fit Me Foundation", "Lash Sensational Mascara", "SuperStay Lip Color", "Concealer"]),

    ("Hair Care", "L'Oréal", ["Shampoo", "Conditioner", "Hair Mask", "Hair Serum"]),
    ("Hair Care", "Dove", ["Shampoo", "Conditioner", "Hair Mask"]),
    ("Hair Care", "Head & Shoulders", ["Anti-Dandruff Shampoo", "2-in-1 Shampoo", "Scalp Care Shampoo"]),
    ("Hair Care", "Generic", ["Shampoo", "Conditioner", "Hair Oil", "Hair Cream", "Hair Gel", "Braiding Hair", "Wig", "Hair Dryer", "Hair Straightener", "Hair Curler"]),

    ("Oral Care", "Colgate", ["Total Toothpaste", "MaxFresh Toothpaste", "Toothbrush", "Mouthwash"]),
    ("Oral Care", "Oral-B", ["Pro Toothbrush", "Electric Toothbrush", "Mouthwash", "Replacement Heads"]),
    ("Oral Care", "Sensodyne", ["Repair & Protect Toothpaste", "Fresh Mint Toothpaste", "Toothbrush"]),

    ("Groceries & Food", "Nestlé", ["Nescafé Coffee", "Milo", "Cerelac", "Nesquik", "KitKat"]),
    ("Groceries & Food", "Kellogg's", ["Corn Flakes", "Rice Krispies", "Frosties", "All-Bran"]),
    ("Groceries & Food", "Brookside", ["Fresh Milk", "Long Life Milk", "Yoghurt", "Mala", "Butter"]),
    ("Groceries & Food", "Coca-Cola", ["Coca-Cola", "Fanta Orange", "Sprite", "Schweppes Soda", "Minute Maid Juice"]),
    ("Groceries & Food", "Pepsi", ["Pepsi", "7UP", "Mirinda", "Mountain Dew"]),
    ("Groceries & Food", "Bidco", ["Elianto Cooking Oil", "Kimbo Cooking Fat", "Kabras Sugar", "Choma Maize Oil"]),
    ("Groceries & Food", "Kapa Oil", ["Menengai Oil", "Kasuku Oil", "Fresh Fri"]),
    ("Groceries & Food", "Generic", ["Rice", "Sugar", "Wheat Flour", "Maize Flour", "Cooking Oil", "Pasta", "Tea", "Coffee", "Biscuits", "Canned Beans", "Cereal", "Spices", "Honey", "Peanut Butter"]),

    ("Beverages", "Coca-Cola", ["Coca-Cola 500ml", "Fanta 500ml", "Sprite 500ml", "Coca-Cola 1.25L", "Coca-Cola 2L"]),
    ("Beverages", "Pepsi", ["Pepsi 500ml", "7UP 500ml", "Mirinda 500ml", "Pepsi 1.25L"]),
    ("Beverages", "Keringet", ["Mineral Water 500ml", "Mineral Water 1L", "Mineral Water 1.5L", "Mineral Water 5L"]),
    ("Beverages", "Generic", ["Bottled Water", "Fruit Juice", "Mango Juice", "Orange Juice", "Energy Drink", "Soda", "Tea", "Coffee"]),

    ("Baby Products", "Pampers", ["Baby Dry Diapers", "Premium Care Diapers", "Baby Wipes"]),
    ("Baby Products", "Huggies", ["DryNites", "Little Snugglers", "Baby Wipes"]),
    ("Baby Products", "Johnson's", ["Baby Lotion", "Baby Oil", "Baby Shampoo", "Baby Wash"]),
    ("Baby Products", "Generic", ["Baby Diapers", "Baby Wipes", "Baby Bottle", "Baby Stroller", "Baby Carrier", "Baby Cot", "Baby Clothes", "Changing Mat", "Baby Bath"]),

    ("Cleaning & Household", "Unilever", ["Sunlight Dishwashing Liquid", "Sunlight Bar Soap", "Domestos", "Comfort Fabric Softener"]),
    ("Cleaning & Household", "Reckitt", ["Dettol Antiseptic", "Dettol Soap", "Harpic Toilet Cleaner", "Air Wick"]),
    ("Cleaning & Household", "P&G", ["Ariel Detergent", "Downy Fabric Softener", "Fairy Dishwashing Liquid"]),
    ("Cleaning & Household", "Generic", ["Laundry Detergent", "Dishwashing Liquid", "Bleach", "Toilet Cleaner", "Glass Cleaner", "Floor Cleaner", "Disinfectant", "Air Freshener", "Garbage Bags", "Mop", "Broom", "Bucket"]),

    ("Sports & Fitness", "Adidas", ["Football", "Training Mat", "Resistance Bands", "Yoga Mat", "Sports Bottle"]),
    ("Sports & Fitness", "Nike", ["Football", "Running Belt", "Training Gloves", "Sports Bottle"]),
    ("Sports & Fitness", "Generic", ["Football", "Basketball", "Volleyball", "Tennis Racket", "Skipping Rope", "Yoga Mat", "Exercise Mat", "Dumbbells", "Kettlebell", "Resistance Bands", "Gym Gloves", "Sports Bottle", "Cycling Helmet"]),

    ("Automotive", "Michelin", ["Passenger Tyre", "SUV Tyre", "Light Truck Tyre"]),
    ("Automotive", "Bridgestone", ["Passenger Tyre", "SUV Tyre", "Light Truck Tyre"]),
    ("Automotive", "Castrol", ["Engine Oil 5W-30", "Engine Oil 5W-40", "Engine Oil 10W-40", "Brake Fluid"]),
    ("Automotive", "TotalEnergies", ["Quartz Engine Oil", "Brake Fluid", "Coolant"]),
    ("Automotive", "Generic", ["Car Battery", "Engine Oil", "Brake Pads", "Spark Plugs", "Air Filter", "Oil Filter", "Car Cover", "Floor Mats", "Phone Holder", "Car Vacuum", "Jump Starter", "Tyre Inflator"]),

    ("Tools & Hardware", "Bosch", ["Cordless Drill", "Angle Grinder", "Circular Saw", "Jigsaw", "Impact Driver", "Measuring Laser"]),
    ("Tools & Hardware", "Stanley", ["Tool Box", "Tape Measure", "Screwdriver Set", "Adjustable Wrench", "Utility Knife"]),
    ("Tools & Hardware", "Black+Decker", ["Cordless Drill", "Heat Gun", "Circular Saw", "Sander", "Pressure Washer"]),
    ("Tools & Hardware", "Generic", ["Hammer", "Screwdriver Set", "Spanner Set", "Pliers", "Adjustable Wrench", "Drill", "Grinder", "Saw", "Measuring Tape", "Spirit Level", "Tool Box", "Ladder"]),

    ("Electrical & Lighting", "Philips", ["LED Bulb", "Smart LED Bulb", "LED Tube", "Outdoor Floodlight"]),
    ("Electrical & Lighting", "Osram", ["LED Bulb", "LED Tube", "Automotive Bulb", "Floodlight"]),
    ("Electrical & Lighting", "Generic", ["LED Bulb", "LED Tube", "Floodlight", "Extension Cable", "Power Strip", "Socket", "Switch", "Circuit Breaker", "Solar Light", "Rechargeable Lamp", "Ceiling Light"]),

    ("Solar & Power", "Deye", ["Hybrid Inverter", "Solar Inverter", "Battery Inverter"]),
    ("Solar & Power", "Growatt", ["Hybrid Inverter", "Off-Grid Inverter", "Solar Inverter"]),
    ("Solar & Power", "Generic", ["Solar Panel", "Solar Inverter", "Hybrid Inverter", "Solar Battery", "Charge Controller", "Solar Floodlight", "Solar Water Pump", "Portable Power Station"]),

    ("Office & School", "HP", ["Ink Tank Printer", "Laser Printer", "All-in-One Printer", "Laptop"]),
    ("Office & School", "Canon", ["Ink Tank Printer", "Laser Printer", "All-in-One Printer"]),
    ("Office & School", "Epson", ["EcoTank Printer", "Laser Printer", "Projector", "Scanner"]),
    ("Office & School", "Generic", ["A4 Paper", "Exercise Books", "Notebooks", "Pens", "Pencils", "Markers", "Stapler", "Calculator", "School Bag", "Office Chair", "Desk Organizer", "Whiteboard"]),

    ("Travel & Luggage", "American Tourister", ["Spinner Suitcase", "Carry-On Case", "Backpack", "Laptop Backpack"]),
    ("Travel & Luggage", "Samsonite", ["Spinner Suitcase", "Carry-On Case", "Travel Backpack"]),
    ("Travel & Luggage", "Generic", ["Suitcase", "Carry-On Bag", "Travel Backpack", "Duffel Bag", "Trolley Bag", "Travel Neck Pillow", "Travel Adapter", "Packing Cubes"]),

    ("Jewellery & Accessories", "Generic", ["Necklace", "Bracelet", "Earrings", "Ring", "Watch", "Sunglasses", "Wallet", "Belt", "Cap", "Handbag"]),

    ("Books & Media", "Penguin", ["Fiction Book", "Business Book", "Self-Development Book"]),
    ("Books & Media", "Generic", ["Novel", "Textbook", "Children's Book", "Revision Book", "Business Book", "Notebook", "Planner", "Bible", "Puzzle Book"]),

    ("Pet Supplies", "Generic", ["Dog Food", "Cat Food", "Pet Shampoo", "Pet Bed", "Pet Bowl", "Leash", "Collar", "Pet Carrier", "Cat Litter", "Pet Toy"]),

    ("Garden & Agriculture", "Generic", ["Garden Hose", "Watering Can", "Pruning Shears", "Wheelbarrow", "Shovel", "Rake", "Hoe", "Seed Tray", "Plant Pot", "Fertilizer", "Drip Irrigation Kit", "Water Pump"]),

    ("Building & Construction", "Bamburi", ["Cement", "Ready Mix", "Concrete Products"]),
    ("Building & Construction", "East African Portland Cement", ["Cement"]),
    ("Building & Construction", "Generic", ["Cement", "Sand", "Ballast", "Bricks", "Blocks", "Roofing Sheets", "Timber", "Steel Bars", "Nails", "Screws", "Paint", "Tiles", "Plumbing Pipe", "PVC Fittings"]),
]


def iter_catalog():
    index = 1
    for category, brand, products in CATALOG:
        for name in products:
            yield {
                "id": f"CAT-{index:05d}",
                "category": category,
                "brand": brand,
                "name": name,
            }
            index += 1

CATALOG_ITEMS = tuple(iter_catalog())
CATALOG_BY_ID = {item["id"]: item for item in CATALOG_ITEMS}


def catalog_choices():
    choices = [("", "— Choose a product from Shopiva's master catalogue —")]
    for item in CATALOG_ITEMS:
        choices.append(
            (item["id"], f'{item["brand"]} · {item["name"]} · {item["category"]}')
        )
    return choices


def catalog_item(key):
    return CATALOG_BY_ID.get(str(key or "").strip())
