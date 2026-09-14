"""Unified, searchable Shopiva seller catalogue.

The catalogue combines the original master directory with vehicle parts and a
large expansion covering phones/accessories, kitchen and home, electronics,
vehicle customisation, bicycles, baby products, office, sports, pet, tools,
agriculture and other everyday marketplace goods.

This is a seller taxonomy, not live inventory. A seller must still provide the
actual price, stock, photos and compatibility details before publishing.
"""

from .product_catalog import CATALOG as BASE_CATALOG
from .vehicle_parts_catalog import VEHICLE_PARTS_CATALOG

CATALOG_EXPANSION = [
    # ─────────────────────────────────────────────────────────────────────
    # PHONES, TABLETS & MODEL-SPECIFIC ACCESSORIES
    # ─────────────────────────────────────────────────────────────────────
    ("Phones & Tablets", "Google", ["Pixel 10", "Pixel 10 Pro", "Pixel 10 Pro XL", "Pixel 9a", "Pixel 9", "Pixel 9 Pro", "Pixel 9 Pro XL", "Pixel Fold", "Pixel Tablet"]),
    ("Phones & Tablets", "OnePlus", ["OnePlus 13", "OnePlus 13R", "OnePlus Nord 5", "OnePlus Nord 4", "OnePlus Open", "OnePlus Pad 2"]),
    ("Phones & Tablets", "Vivo", ["V40", "V40 Pro", "V50", "V50 Lite", "Y28", "Y36", "Y39", "X100", "X200", "X200 Pro"]),
    ("Phones & Tablets", "OPPO", ["Find X8", "Find X8 Pro", "Reno 13", "Reno 13 Pro", "A5 Pro", "A60", "A5", "Pad 4 Pro"]),
    ("Phones & Tablets", "Realme", ["GT 7", "GT 6", "GT 6T", "13 Pro+", "14 Pro", "14 Pro+", "C75", "C65"]),
    ("Phones & Tablets", "Motorola", ["Edge 60", "Edge 60 Pro", "Moto G Power", "Moto G Stylus", "Razr 60", "Razr 60 Ultra"]),
    ("Phones & Tablets", "Honor", ["Magic7 Pro", "Magic V3", "200 Pro", "X8c", "X9c", "Pad 9"]),
    ("Phones & Tablets", "Sony", ["Xperia 1 VII", "Xperia 10 VII", "Xperia 5 V"]),
    ("Phones & Tablets", "Asus", ["ROG Phone 9", "ROG Phone 9 Pro", "Zenfone 12 Ultra"]),
    ("Phones & Tablets", "Nothing", ["Phone (3)", "Phone (3a)", "Phone (3a) Pro", "CMF Phone 2 Pro"]),
    ("Phones & Tablets", "ZTE", ["nubia Z70 Ultra", "nubia Neo 3", "RedMagic 10 Pro"]),
    ("Phones & Tablets", "TCL", ["TCL 50", "TCL 60", "TCL NXTPAPER", "TCL Tab 11"]),
    ("Phones & Tablets", "Alcatel", ["1B", "1S", "3L", "3X", "1T Tablet"]),
    ("Phones & Tablets", "Generic", ["Android Smartphone", "Feature Phone", "5G Smartphone", "4G LTE Smartphone", "Dual SIM Phone", "Rugged Smartphone", "Senior Phone", "Kids Phone", "Android Tablet", "Windows Tablet", "Drawing Tablet", "E-reader"]),

    ("Phone Accessories - Apple", "Apple Compatible", ["iPhone 16 Case", "iPhone 16 Plus Case", "iPhone 16 Pro Case", "iPhone 16 Pro Max Case", "iPhone 15 Case", "iPhone 15 Pro Case", "iPhone 15 Pro Max Case", "iPhone 14 Case", "iPhone 13 Case", "iPhone 12 Case", "iPhone SE Case", "iPad Case", "iPad Pro Case", "iPad Air Case", "Apple Pencil Compatible Stylus", "MagSafe Charger", "MagSafe Battery Pack", "USB-C to USB-C Cable", "USB-C Power Adapter", "Lightning Cable", "Screen Protector", "Camera Lens Protector", "MagSafe Car Mount", "MagSafe Wallet"]),
    ("Phone Accessories - Samsung", "Samsung Compatible", ["Galaxy S25 Case", "Galaxy S25+ Case", "Galaxy S25 Ultra Case", "Galaxy S24 Case", "Galaxy S24 Ultra Case", "Galaxy A16 Case", "Galaxy A26 Case", "Galaxy A36 Case", "Galaxy A55 Case", "Galaxy A35 Case", "Galaxy A15 Case", "Galaxy A05 Case", "Galaxy Z Fold Case", "Galaxy Z Flip Case", "Galaxy Tab Case", "Galaxy Watch Strap", "Galaxy SmartTag", "Samsung USB-C Cable", "Samsung Fast Charger", "Screen Protector", "Camera Lens Protector", "S Pen Compatible Stylus"]),
    ("Phone Accessories - Tecno", "Tecno Compatible", ["CAMON 40 Case", "CAMON 40 Pro Case", "CAMON 30 Case", "SPARK 30 Case", "SPARK 30 Pro Case", "POVA 6 Case", "MEGAPAD Case", "Tecno Fast Charger", "Tecno USB-C Cable", "Screen Protector", "Camera Lens Protector", "Phone Ring Holder", "Phone Grip"]),
    ("Phone Accessories - Infinix", "Infinix Compatible", ["NOTE 40 Case", "NOTE 40 Pro Case", "NOTE 50 Case", "HOT 50 Case", "HOT 50 Pro Case", "GT 20 Pro Case", "XPad Case", "Infinix Fast Charger", "Infinix USB-C Cable", "Screen Protector", "Camera Lens Protector", "Phone Ring Holder", "Gaming Finger Sleeves"]),
    ("Phone Accessories - Xiaomi", "Xiaomi Compatible", ["Redmi Note 14 Case", "Redmi Note 14 Pro Case", "Redmi 14C Case", "Poco X6 Case", "Poco M6 Case", "Xiaomi 14 Case", "Xiaomi 14T Case", "Xiaomi Pad Case", "Mi Band Strap", "Xiaomi Fast Charger", "USB-C Cable", "Screen Protector", "Camera Lens Protector"]),
    ("Phone Accessories - OPPO/Vivo/Realme", "Android Compatible", ["OPPO Reno Case", "OPPO A-Series Case", "Vivo V-Series Case", "Vivo Y-Series Case", "Realme GT Case", "Realme C-Series Case", "Fast Charger", "SuperVOOC Compatible Charger", "USB-C Cable", "Screen Protector", "Camera Lens Protector", "Phone Wallet Case", "Phone Ring Holder"]),
    ("Phone Accessories - Universal", "Universal", ["Universal Phone Case", "Wallet Phone Case", "Clear Phone Case", "Rugged Phone Case", "Shockproof Case", "Privacy Screen Protector", "Tempered Glass", "Hydrogel Screen Protector", "Camera Lens Protector", "Pop Grip", "Ring Holder", "Phone Lanyard", "Neck Holder", "Desk Phone Stand", "Adjustable Phone Stand", "Tripod Phone Mount", "Selfie Stick", "Gimbal Stabilizer", "Car Phone Mount", "Dashboard Phone Mount", "Vent Phone Mount", "Motorcycle Phone Mount", "Bicycle Phone Mount", "Wireless Charger", "Magnetic Wireless Charger", "Car Wireless Charger", "Power Bank", "MagSafe Power Bank", "Solar Power Bank", "USB-C Power Bank", "Wall Charger", "Multi-Port Charger", "GaN Charger", "Car Charger", "USB Adapter", "OTG Adapter", "USB-C Hub", "USB-C to HDMI Adapter", "Lightning Adapter", "Bluetooth Receiver", "Bluetooth Transmitter"]),
    ("Phone Repair Parts", "Universal", ["Phone Display Screen", "OLED Display", "LCD Display", "Touchscreen Digitizer", "Replacement Battery", "Battery Adhesive", "Charging Port", "USB-C Port", "Lightning Port", "Power Button Flex", "Volume Button Flex", "Camera Module", "Earpiece Speaker", "Loudspeaker", "Vibration Motor", "Back Glass", "Back Cover", "SIM Tray", "Camera Lens Glass", "Replacement Frame", "Phone Repair Tool Kit", "Precision Screwdriver Kit", "Screen Repair Mat"]),
    ("Audio Accessories", "Universal", ["True Wireless Earbuds", "Sports Earbuds", "Neckband Earphones", "Wired Earphones", "USB-C Earphones", "Lightning Earphones", "Bluetooth Headphones", "Noise Cancelling Headphones", "Gaming Headset", "USB Headset", "Conference Speakerphone", "Portable Bluetooth Speaker", "Party Speaker", "Soundbar", "Subwoofer", "Microphone", "Wireless Microphone", "Lavalier Microphone", "Studio Headphones", "Audio Cable", "AUX Cable", "Optical Cable", "RCA Cable", "Speaker Wire"]),
    ("Smart Devices & Wearables", "Universal", ["Smartwatch", "Kids Smartwatch", "Fitness Band", "Smart Ring", "Smart Glasses", "VR Headset", "AR Headset", "Smart Tracker", "Digital Voice Recorder", "E-book Reader"]),

    # ─────────────────────────────────────────────────────────────────────
    # KITCHEN UTENSILS, COOKWARE & DINING
    # ─────────────────────────────────────────────────────────────────────
    ("Kitchen Utensils", "Generic", ["Chef Knife", "Paring Knife", "Bread Knife", "Kitchen Scissors", "Cutting Board", "Chopping Board", "Peeler", "Grater", "Zester", "Garlic Press", "Can Opener", "Bottle Opener", "Corkscrew", "Kitchen Tongs", "Serving Tongs", "Whisk", "Balloon Whisk", "Silicone Spatula", "Wooden Spatula", "Turner", "Slotted Spoon", "Serving Spoon", "Ladle", "Pasta Server", "Potato Masher", "Meat Tenderizer", "Kitchen Brush", "Basting Brush", "Rolling Pin", "Measuring Cups", "Measuring Spoons", "Kitchen Scale", "Colander", "Sieve", "Strainer", "Funnel", "Mortar & Pestle", "Oil Dispenser", "Pepper Grinder", "Salt Shaker", "Spice Jar Set"]),
    ("Cookware", "Generic", ["Frying Pan", "Non-Stick Frying Pan", "Saucepan", "Stock Pot", "Cooking Pot Set", "Pressure Cooker", "Cast Iron Pot", "Cast Iron Pan", "Wok", "Grill Pan", "Crepe Pan", "Milk Pan", "Egg Pan", "Dutch Oven", "Steamer Pot", "Double Boiler", "Roasting Pan", "Baking Tray", "Baking Sheet", "Pizza Tray", "Casserole Dish", "Ovenproof Dish", "Casserole Pot", "Cookware Lid", "Universal Pot Lid", "Pot Handle"]),
    ("Cutlery & Tableware", "Generic", ["Dinner Plate", "Side Plate", "Soup Bowl", "Cereal Bowl", "Serving Bowl", "Dinner Set", "Tea Set", "Coffee Cup", "Mug", "Glass Tumbler", "Wine Glass", "Champagne Glass", "Jug", "Pitcher", "Water Bottle", "Travel Mug", "Thermos Flask", "Cutlery Set", "Table Knife", "Table Fork", "Table Spoon", "Teaspoon", "Chopsticks", "Serving Tray", "Cake Stand", "Butter Dish", "Sugar Bowl", "Salt & Pepper Set"]),
    ("Food Storage", "Generic", ["Food Storage Container", "Airtight Container", "Glass Food Container", "Lunch Box", "Bento Box", "Thermal Lunch Box", "Water Bottle", "Sports Bottle", "Storage Jar", "Spice Rack", "Bread Bin", "Cake Tin", "Meal Prep Container", "Freezer Bag", "Food Wrap", "Aluminium Foil", "Baking Paper", "Vacuum Storage Bags"]),
    ("Baking Supplies", "Generic", ["Cake Pan", "Loaf Pan", "Muffin Tray", "Cupcake Liners", "Cookie Cutter Set", "Cake Turntable", "Icing Spatula", "Cake Scraper", "Piping Bag", "Piping Nozzle Set", "Rolling Mat", "Pastry Brush", "Cooling Rack", "Digital Kitchen Timer", "Cake Decorating Kit", "Baking Mould", "Silicone Baking Mat"]),

    # ─────────────────────────────────────────────────────────────────────
    # HOME APPLIANCES, CLEANING & LAUNDRY
    # ─────────────────────────────────────────────────────────────────────
    ("Home Appliances", "Ramtons", ["Electric Pressure Cooker", "Electric Oven", "Microwave Oven", "Air Fryer", "Toaster", "Sandwich Maker", "Electric Kettle", "Rice Cooker", "Slow Cooker", "Food Processor", "Hand Mixer", "Stand Mixer", "Coffee Maker", "Espresso Machine", "Water Dispenser", "Electric Iron", "Garment Steamer", "Vacuum Cleaner", "Handheld Vacuum", "Steam Mop", "Carpet Cleaner", "Room Heater", "Standing Fan", "Table Fan", "Air Purifier"]),
    ("Home Appliances", "Mika", ["Electric Pressure Cooker", "Microwave Oven", "Air Fryer", "Toaster", "Sandwich Maker", "Electric Kettle", "Rice Cooker", "Blender", "Food Processor", "Hand Mixer", "Electric Iron", "Garment Steamer", "Vacuum Cleaner", "Standing Fan", "Table Fan", "Room Heater", "Water Dispenser"]),
    ("Home Appliances", "Von Hotpoint", ["Microwave Oven", "Built-in Oven", "Freestanding Cooker", "Gas Cooker", "Electric Cooker", "Air Fryer", "Blender", "Electric Kettle", "Toaster", "Rice Cooker", "Food Processor", "Electric Iron", "Vacuum Cleaner", "Steam Mop", "Water Dispenser", "Air Purifier", "Tower Fan"]),
    ("Small Appliances", "Generic", ["Blender", "Personal Blender", "Hand Blender", "Juicer", "Citrus Juicer", "Food Chopper", "Food Processor", "Coffee Grinder", "Coffee Maker", "Espresso Machine", "Milk Frother", "Electric Kettle", "Travel Kettle", "Toaster", "Sandwich Maker", "Waffle Maker", "Donut Maker", "Popcorn Maker", "Slow Cooker", "Rice Cooker", "Pressure Cooker", "Air Fryer", "Electric Hot Plate", "Induction Cooker", "Electric Griddle"]),
    ("Cleaning Appliances", "Generic", ["Vacuum Cleaner", "Robot Vacuum", "Handheld Vacuum", "Wet & Dry Vacuum", "Steam Mop", "Pressure Washer", "Carpet Cleaner", "Window Vacuum", "Floor Polisher", "Electric Mop", "Air Purifier", "Dehumidifier", "Humidifier", "Mosquito Killer"]),
    ("Laundry Appliances", "Generic", ["Twin Tub Washing Machine", "Front Load Washing Machine", "Top Load Washing Machine", "Washer Dryer", "Dryer", "Clothes Steamer", "Garment Iron", "Ironing Board", "Clothes Drying Rack", "Laundry Basket", "Laundry Hamper"]),

    # ─────────────────────────────────────────────────────────────────────
    # ELECTRONICS, COMPUTING, NETWORKING & POWER
    # ─────────────────────────────────────────────────────────────────────
    ("Computers & Accessories", "Generic", ["Desktop Computer", "Mini PC", "All-in-One PC", "Gaming PC", "Workstation PC", "Chromebook", "Monitor", "Ultrawide Monitor", "Portable Monitor", "Keyboard", "Mechanical Keyboard", "Mouse", "Gaming Mouse", "Mouse Pad", "Webcam", "USB Hub", "USB-C Dock", "External Hard Drive", "External SSD", "Flash Drive", "Memory Card", "Card Reader", "Laptop Stand", "Cooling Pad", "Laptop Bag", "Laptop Sleeve", "Docking Station", "Graphics Tablet", "Drawing Tablet"]),
    ("Printers & Office Electronics", "Generic", ["Inkjet Printer", "Laser Printer", "Multifunction Printer", "Photo Printer", "Label Printer", "Thermal Receipt Printer", "POS Printer", "Barcode Scanner", "Document Scanner", "Laminator", "Binding Machine", "Paper Shredder", "Projector", "Projector Screen", "Presentation Remote", "Digital Whiteboard", "UPS", "Surge Protector", "Extension Cable", "Power Strip"]),
    ("Networking", "Generic", ["Wi-Fi Router", "5G Router", "4G LTE Router", "Mesh Wi-Fi System", "Wi-Fi Extender", "Access Point", "Network Switch", "PoE Switch", "Ethernet Cable", "Cat6 Cable", "Cat7 Cable", "Fiber Patch Cable", "USB Wi-Fi Adapter", "Bluetooth Adapter", "Network Tester", "Crimping Tool", "Patch Panel", "Network Rack", "Cable Organizer"]),
    ("CCTV & Security", "Generic", ["Indoor Security Camera", "Outdoor Security Camera", "PTZ Camera", "Wi-Fi Camera", "4G CCTV Camera", "Solar Security Camera", "Doorbell Camera", "Baby Monitor", "CCTV DVR", "CCTV NVR", "PoE NVR", "Hard Drive for CCTV", "CCTV Monitor", "CCTV Cable", "BNC Connector", "Power Supply", "Motion Sensor", "Door Sensor", "Smart Lock", "Access Control Keypad", "Biometric Fingerprint Reader"]),
    ("Power & Charging", "Generic", ["UPS", "Inverter", "Pure Sine Wave Inverter", "Car Inverter", "Voltage Stabilizer", "AVR", "Power Bank", "Portable Power Station", "Emergency Power Station", "Solar Generator", "Extension Cable", "Extension Socket", "Surge Protector", "Power Strip", "USB Power Meter", "Battery Charger", "AA Battery Charger", "Power Adapter", "Universal Adapter", "DC Adapter"]),
    ("Solar & Energy", "Generic", ["Solar Panel", "Monocrystalline Solar Panel", "Polycrystalline Solar Panel", "Solar Inverter", "Hybrid Solar Inverter", "Solar Charge Controller", "MPPT Controller", "PWM Controller", "Solar Battery", "Gel Battery", "Lithium Battery", "Solar Flood Light", "Solar Security Light", "Solar Street Light", "Solar Home Kit", "Solar Lantern", "Solar Water Pump", "Solar Cable", "MC4 Connector", "Solar Mounting Kit"]),
    ("LED & Lighting Electronics", "Generic", ["LED Bulb", "Smart Bulb", "LED Strip Light", "RGB LED Strip", "LED Downlight", "LED Panel Light", "LED Tube", "Flood Light", "Security Light", "Motion Sensor Light", "Desk Lamp", "Reading Lamp", "Bedside Lamp", "Ring Light", "Studio Light", "Neon Light", "Rechargeable Lantern", "Emergency Light", "Headlamp", "Flashlight"]),
    ("Audio & Home Entertainment", "Generic", ["Smart Speaker", "Bluetooth Speaker", "Party Speaker", "Soundbar", "Home Theatre System", "AV Receiver", "Amplifier", "Karaoke Machine", "Karaoke Microphone", "Wireless Microphone", "Studio Microphone", "Podcast Microphone", "DJ Controller", "Turntable", "CD Player", "Streaming Device", "Android TV Box", "Media Player", "FM Radio", "Portable Radio"]),

    # ─────────────────────────────────────────────────────────────────────
    # CAR, MOTORCYCLE & BICYCLE ACCESSORIES / CUSTOMISATION
    # ─────────────────────────────────────────────────────────────────────
    ("Car Accessories", "Universal", ["Car Phone Holder", "Magnetic Car Mount", "Car Charger", "USB Car Charger", "Car Bluetooth Adapter", "Dash Camera", "Rear Camera", "Parking Sensor", "TPMS Monitor", "Car Vacuum Cleaner", "Car Air Compressor", "Tyre Inflator", "Tyre Pressure Gauge", "Jump Starter", "Battery Charger", "Emergency Triangle", "Reflective Vest", "Warning Beacon", "First Aid Kit", "Car Fire Extinguisher", "Seat Cover", "Steering Wheel Cover", "Floor Mat", "Boot Mat", "Dashboard Mat", "Sun Shade", "Window Sunshade", "Car Curtain", "Neck Pillow", "Seat Cushion", "Lumbar Support", "Car Trash Bin", "Air Freshener", "Car Organizer", "Boot Organizer", "Roof Rack", "Roof Box", "Bike Rack", "Tow Rope", "Recovery Strap", "Tow Hitch Accessory"]),
    ("Car Exterior Styling", "Universal", ["LED Headlight Upgrade", "LED Fog Light", "Daytime Running Light", "Sequential Indicator", "LED Tail Light", "Number Plate Light", "Door Handle Cover", "Mirror Cover", "Side Skirt", "Front Lip", "Rear Diffuser", "Spoiler", "Roof Spoiler", "Mud Flap", "Wheel Arch Trim", "Window Visor", "Rain Guard", "Door Sill Plate", "Chrome Trim", "Carbon Trim", "Vinyl Wrap", "Chrome Delete Film", "Decal Set", "Body Sticker", "Tint Film"]),
    ("Car Interior Customisation", "Universal", ["Ambient LED Lighting", "Dashboard LED Strip", "Footwell Lighting", "Star Ceiling Kit", "Custom Seat Cover", "Leather Seat Cover", "Steering Wheel Upgrade", "Custom Steering Cover", "Gear Knob", "Gear Boot", "Hand Brake Cover", "Pedal Cover Set", "Door Sill Plate", "Interior Trim Kit", "Carbon Fibre Trim", "Dashboard Cover", "Custom Floor Mats", "Trunk Organizer", "Seat Back Organizer", "Tablet Headrest Mount"]),
    ("Car Tools & Workshop", "Generic", ["OBD2 Scanner", "Car Diagnostic Scanner", "Multimeter", "Battery Tester", "Torque Wrench", "Socket Set", "Spanner Set", "Screwdriver Set", "Pliers Set", "Jack", "Hydraulic Jack", "Jack Stand", "Wheel Chock", "Wheel Nut Socket", "Breaker Bar", "Impact Wrench", "Cordless Drill", "Workshop Creeper", "Mechanic Tool Box", "Oil Drain Pan", "Funnel Set", "Grease Gun", "Inspection Lamp", "Work Light"]),
    ("Motorcycle Accessories", "Universal", ["Motorcycle Phone Holder", "USB Motorcycle Charger", "Motorcycle Dash Camera", "Bluetooth Helmet Intercom", "Top Box", "Side Pannier", "Tank Bag", "Saddle Bag", "Tail Bag", "Cargo Net", "Motorcycle Cover", "Tank Pad", "Crash Bar", "Engine Guard", "Bash Plate", "Hand Guard", "Windshield", "Adjustable Brake Lever", "Adjustable Clutch Lever", "Bar End Mirror", "LED Headlight", "LED Indicators", "LED Tail Light", "Auxiliary Fog Lights", "Horn", "Alarm", "GPS Tracker", "USB Socket", "Handlebar Riser", "Foot Peg Upgrade", "Rear Set Footrest", "Seat Pad", "Gel Seat Cover", "Chain Guard", "Fender Eliminator", "License Plate Holder"]),
    ("Motorcycle Customisation", "Universal", ["Custom Fairing Kit", "Fairing Decal Kit", "Graphics Kit", "Full Body Wrap", "Tank Grip Pads", "Custom Seat", "Seat Upholstery", "Alloy Wheel Upgrade", "Spoke Wheel Upgrade", "Handlebar Upgrade", "Fat Bar", "Clip-On Handlebar", "Bar End Weights", "Performance Exhaust", "Slip-On Exhaust", "Exhaust Heat Shield", "Air Filter Upgrade", "LED Projector", "Custom Mirrors", "Custom Grips", "Custom Levers", "Adjustable Rearsets", "Footrest Kit", "Swingarm Spools", "Radiator Guard", "Oil Cooler Guard", "Engine Case Cover", "Frame Sliders", "Axle Sliders", "Fork Protectors", "Wheel Decals", "Chain Colour Kit", "Sprocket Upgrade", "Stunt Cage", "Wheelie Bar Kit"]),
    ("Bicycle Spare Parts", "Generic", ["Bicycle Brake Pads", "Brake Cable", "Brake Housing", "Brake Lever", "Disc Brake Rotor", "Mechanical Disc Brake", "Hydraulic Disc Brake", "Derailleur", "Rear Derailleur", "Front Derailleur", "Shifter", "Shift Cable", "Cassette", "Freewheel", "Chain", "Chainring", "Crankset", "Bottom Bracket", "Pedal", "Clipless Pedal", "Flat Pedal", "Hub", "Front Hub", "Rear Hub", "Wheelset", "Rim", "Spoke", "Nipple", "Headset", "Stem", "Handlebar", "Seatpost", "Saddle", "Seat Clamp", "Fork", "Suspension Fork", "Rear Shock", "Tyre", "Tube", "Tubeless Tyre", "Tubeless Rim Tape", "Tubeless Valve", "Bicycle Pump", "Floor Pump", "CO2 Inflator", "Bike Tool Kit", "Chain Tool", "Cassette Tool", "Bottom Bracket Tool"]),
    ("Bicycle Customisation", "Universal", ["Custom Handlebar", "Drop Handlebar", "Flat Handlebar", "Aero Handlebar", "Carbon Handlebar", "Handlebar Tape", "Premium Grips", "Lock-On Grips", "Handlebar Riser", "Adjustable Stem", "Carbon Stem", "Colour-Matched Stem", "Performance Saddle", "Carbon Seatpost", "Dropper Seatpost", "Seatpost Clamp", "Custom Pedals", "Platform Pedals", "Clipless Pedals", "Pedal Reflectors", "Wheel Upgrade", "Aero Wheelset", "Carbon Wheelset", "Deep Section Rims", "Colour Spokes", "Hub Upgrade", "Tubeless Conversion Kit", "Hydraulic Brake Upgrade", "Rotor Upgrade", "Brake Colour Kit", "Drivetrain Upgrade", "Wide-Range Cassette", "Performance Chain", "Colour Chain", "Chainring Upgrade", "Crank Arm Upgrade", "Suspension Fork Upgrade", "Rear Shock Upgrade", "Frame Protection Kit", "Frame Wrap", "Custom Decals", "Custom Graphics", "Reflective Decals", "Bottle Cage", "Carbon Bottle Cage", "Frame Bag", "Top Tube Bag", "Saddle Bag", "Rear Rack", "Front Rack", "Mudguard Set", "Fender Set", "Bicycle Lights", "Turn Signal Kit", "Smart Bike Computer", "GPS Bike Computer", "Bike Alarm", "Bike Tracker", "Phone Mount", "Camera Mount", "Action Camera Mount"]),

    # ─────────────────────────────────────────────────────────────────────
    # FASHION, BAGS, JEWELRY & TRAVEL
    # ─────────────────────────────────────────────────────────────────────
    ("Fashion - Men", "Generic", ["T-Shirt", "Polo Shirt", "Dress Shirt", "Oxford Shirt", "Denim Shirt", "Henley Shirt", "Sweatshirt", "Hoodie", "Jacket", "Blazer", "Suit", "Waistcoat", "Jeans", "Chinos", "Cargo Trousers", "Track Pants", "Joggers", "Shorts", "Swim Shorts", "Underwear", "Vest", "Socks", "Tie", "Bow Tie", "Belt", "Cap", "Beanie", "Scarf", "Gloves"]),
    ("Fashion - Women", "Generic", ["T-Shirt", "Blouse", "Shirt", "Crop Top", "Tank Top", "Camisole", "Dress", "Maxi Dress", "Midi Dress", "Mini Dress", "Jumpsuit", "Romper", "Skirt", "Pleated Skirt", "Jeans", "Trousers", "Palazzo Trousers", "Leggings", "Shorts", "Jacket", "Blazer", "Cardigan", "Sweater", "Hoodie", "Lingerie", "Pajamas", "Socks", "Stockings", "Scarf", "Shawl"]),
    ("Fashion - Kids", "Generic", ["Baby Bodysuit", "Baby Romper", "Kids T-Shirt", "Kids Polo", "Kids Shirt", "Kids Dress", "Kids Skirt", "Kids Jeans", "Kids Trousers", "Kids Shorts", "Kids Hoodie", "Kids Jacket", "Kids Pajamas", "Kids Underwear", "Kids Socks", "School Shirt", "School Sweater", "School Trousers", "School Skirt", "School Tie", "School Belt"]),
    ("Bags & Luggage", "Generic", ["Backpack", "School Backpack", "Laptop Backpack", "Travel Backpack", "Duffel Bag", "Gym Bag", "Crossbody Bag", "Shoulder Bag", "Handbag", "Tote Bag", "Messenger Bag", "Waist Bag", "Sling Bag", "Briefcase", "Laptop Bag", "Camera Bag", "Tool Bag", "Makeup Bag", "Travel Organizer", "Passport Holder", "Suitcase", "Cabin Suitcase", "Travel Trunk", "Luggage Set", "Packing Cubes", "Garment Bag", "Shopping Bag"]),
    ("Jewelry & Accessories", "Generic", ["Necklace", "Pendant", "Chain", "Bracelet", "Bangle", "Earrings", "Stud Earrings", "Hoop Earrings", "Ring", "Promise Ring", "Brooch", "Anklet", "Watch", "Sunglasses", "Reading Glasses", "Optical Frames", "Hair Clips", "Hair Bands", "Scrunchies", "Headband", "Wallet", "Card Holder", "Key Holder", "Keychain"]),

    # ─────────────────────────────────────────────────────────────────────
    # BEAUTY, PERSONAL CARE & WELLNESS (NON-PRESCRIPTION GOODS)
    # ─────────────────────────────────────────────────────────────────────
    ("Beauty Tools", "Generic", ["Makeup Brush Set", "Makeup Sponge", "Makeup Mirror", "LED Makeup Mirror", "Eyelash Curler", "Tweezers", "Nail Clipper", "Nail File", "Manicure Set", "Pedicure Set", "Nail Drill", "Hair Dryer", "Hair Straightener", "Hair Curler", "Curling Wand", "Hair Clipper", "Hair Trimmer", "Beard Trimmer", "Electric Shaver", "Facial Steamer", "Facial Cleansing Brush", "Massage Gun", "Body Massager", "Foot Massager", "Electric Toothbrush", "Water Flosser"]),
    ("Personal Care", "Generic", ["Body Wash", "Bath Soap", "Hand Wash", "Hand Sanitizer", "Body Lotion", "Body Cream", "Body Scrub", "Deodorant", "Perfume", "Cologne", "Body Mist", "Sunscreen", "Lip Balm", "Lip Gloss", "Foundation", "Concealer", "Mascara", "Eyeliner", "Eyeshadow Palette", "Blush", "Highlighter", "Lipstick", "Nail Polish", "Hair Shampoo", "Hair Conditioner", "Hair Oil", "Hair Cream", "Hair Gel", "Hair Wax", "Hair Spray", "Wig", "Braiding Hair"]),
    ("Personal Wellness", "Generic", ["Yoga Mat", "Foam Roller", "Resistance Bands", "Skipping Rope", "Massage Ball", "Posture Support", "Sleep Mask", "Hot Water Bottle", "Reusable Ice Pack", "Digital Thermometer", "Pill Organizer", "Water Intake Bottle", "Aromatherapy Diffuser", "Essential Oil Diffuser", "Humidifier"]),

    # ─────────────────────────────────────────────────────────────────────
    # BABY, TOYS & CHILDREN
    # ─────────────────────────────────────────────────────────────────────
    ("Baby Care", "Generic", ["Baby Diapers", "Reusable Baby Diapers", "Baby Wipes", "Baby Lotion", "Baby Shampoo", "Baby Wash", "Baby Oil", "Baby Powder", "Baby Bath Tub", "Baby Nail Kit", "Baby Feeding Bottle", "Baby Bottle Warmer", "Bottle Sterilizer", "Breast Pump", "Baby Bib", "Burp Cloth", "Changing Mat", "Changing Bag", "Baby Carrier", "Baby Sling", "Baby Walker", "Baby Stroller", "Baby Cot", "Cot Mattress", "Baby Bedding", "Baby Blanket", "Baby Monitor", "Baby Night Light"]),
    ("Toys", "Generic", ["Building Blocks", "Construction Set", "Puzzle", "Jigsaw Puzzle", "Board Game", "Card Game", "Remote Control Car", "Toy Train", "Toy Plane", "Toy Helicopter", "Doll", "Doll House", "Action Figure", "Toy Kitchen", "Toy Tool Set", "Doctor Set", "Educational Toy", "Montessori Toy", "Science Kit", "Art Set", "Colouring Book", "Drawing Board", "Plush Toy", "Stuffed Animal", "Outdoor Toy", "Football Toy", "Toy Gun - non-weapon play item"]),

    # ─────────────────────────────────────────────────────────────────────
    # SPORTS, FITNESS & OUTDOOR
    # ─────────────────────────────────────────────────────────────────────
    ("Sports & Fitness", "Generic", ["Football", "Football Boots", "Football Jersey", "Basketball", "Basketball Shoes", "Volleyball", "Rugby Ball", "Rugby Boots", "Tennis Racket", "Tennis Balls", "Badminton Racket", "Badminton Shuttlecock", "Table Tennis Bat", "Table Tennis Balls", "Skipping Rope", "Yoga Mat", "Gym Mat", "Dumbbell", "Adjustable Dumbbell", "Kettlebell", "Barbell", "Weight Plates", "Resistance Bands", "Gym Gloves", "Weightlifting Belt", "Bench", "Exercise Bike", "Spin Bike", "Treadmill", "Elliptical Trainer", "Punching Bag", "Boxing Gloves", "Mouth Guard", "Sports Bottle", "Hydration Pack", "Camping Tent", "Sleeping Bag", "Camping Chair", "Camping Table", "Portable Stove", "Hiking Backpack", "Trekking Poles", "Outdoor Lantern", "Binoculars"]),

    # ─────────────────────────────────────────────────────────────────────
    # OFFICE, SCHOOL, BOOKS & CREATIVE SUPPLIES
    # ─────────────────────────────────────────────────────────────────────
    ("Office Supplies", "Generic", ["Notebook", "Exercise Book", "Diary", "Planner", "Sticky Notes", "Index Cards", "Ballpoint Pen", "Gel Pen", "Marker", "Permanent Marker", "Highlighter", "Pencil", "Mechanical Pencil", "Pencil Sharpener", "Eraser", "Ruler", "Geometry Set", "Stapler", "Staples", "Paper Punch", "Paper Clip", "Binder Clip", "File Folder", "Lever Arch File", "Document Wallet", "Envelope", "Printer Paper", "Labels", "Scissors", "Glue", "Tape", "Correction Fluid", "Calculator", "Desk Organizer", "Pen Holder", "Desk Mat", "Calendar"]),
    ("Books & Media", "Generic", ["Textbook", "Revision Book", "Children's Book", "Novel", "Biography", "Cookbook", "Business Book", "Self-Improvement Book", "Dictionary", "Bible", "Notebook Journal", "Comic Book", "Manga", "Magazine", "Map", "Planner Book"]),
    ("Art & Craft", "Generic", ["Sketchbook", "Canvas", "Acrylic Paint", "Watercolour Paint", "Oil Paint", "Paint Brush Set", "Pencil Set", "Charcoal Set", "Pastel Set", "Crayons", "Colouring Pencils", "Marker Set", "Craft Paper", "Cardstock", "Glue Gun", "Glue Sticks", "Scissors", "Craft Knife", "Beads", "Jewelry Making Kit", "Embroidery Kit", "Sewing Kit", "Knitting Needles", "Crochet Hooks", "Fabric", "Thread", "Yarn"]),

    # ─────────────────────────────────────────────────────────────────────
    # TOOLS, HARDWARE, ELECTRICAL, PLUMBING & BUILDING
    # ─────────────────────────────────────────────────────────────────────
    ("Tools & Hardware", "Generic", ["Hammer", "Claw Hammer", "Sledge Hammer", "Screwdriver", "Screwdriver Set", "Spanner", "Combination Spanner Set", "Adjustable Wrench", "Socket Set", "Ratchet", "Torque Wrench", "Pliers", "Long Nose Pliers", "Locking Pliers", "Wire Cutter", "Allen Key Set", "Hex Key Set", "Drill", "Cordless Drill", "Impact Driver", "Angle Grinder", "Circular Saw", "Jigsaw", "Heat Gun", "Soldering Iron", "Bench Vice", "Hand Saw", "Hacksaw", "Tape Measure", "Spirit Level", "Chisel", "File Set", "Utility Knife", "Tool Box", "Tool Bag", "Ladder", "Work Bench"]),
    ("Electrical Supplies", "Generic", ["Electrical Cable", "Twin & Earth Cable", "Flexible Cable", "Coaxial Cable", "Ethernet Cable", "Plug Top", "Socket Outlet", "Switch", "Dimmer Switch", "Extension Socket", "Extension Lead", "Power Strip", "Circuit Breaker", "MCB", "RCD", "Distribution Board", "Fuse", "Fuse Holder", "Cable Lug", "Terminal Block", "Cable Tie", "Conduit", "Junction Box", "Electrical Tape", "Insulation Tape", "Voltage Tester", "Multimeter", "Electric Meter Box"]),
    ("Plumbing Supplies", "Generic", ["PVC Pipe", "PPR Pipe", "HDPE Pipe", "Pipe Fitting", "Elbow Joint", "Tee Joint", "Reducer", "Union", "Valve", "Ball Valve", "Gate Valve", "Check Valve", "Tap", "Mixer Tap", "Shower Mixer", "Shower Head", "Flexible Hose", "Sink Waste", "Bottle Trap", "Floor Drain", "Toilet Seat", "Toilet Cistern", "Toilet Pan", "Water Tank Fitting", "Pipe Wrench", "Plumber Tape", "PVC Glue", "Silicone Sealant"]),
    ("Building & Home Improvement", "Generic", ["Door Handle", "Door Lock", "Padlock", "Cabinet Handle", "Hinge", "Drawer Slide", "Shelf Bracket", "Wall Bracket", "Curtain Rod", "Curtain Rail", "Wall Hook", "Mirror", "Picture Frame", "Wall Clock", "Paint Roller", "Paint Brush", "Masking Tape", "Sandpaper", "Wood Glue", "Construction Adhesive", "Silicone Sealant", "Caulking Gun", "Door Stopper", "Furniture Leg"]),

    # ─────────────────────────────────────────────────────────────────────
    # HOME DECOR, BEDDING & LIVING
    # ─────────────────────────────────────────────────────────────────────
    ("Home Decor", "Generic", ["Wall Art", "Canvas Print", "Photo Frame", "Mirror", "Decorative Mirror", "Wall Clock", "Vase", "Artificial Plant", "Indoor Plant Pot", "Cushion Cover", "Throw Pillow", "Throw Blanket", "Table Runner", "Table Cloth", "Curtain", "Blackout Curtain", "Sheer Curtain", "Blinds", "Rug", "Carpet", "Doormat", "Laundry Basket", "Storage Basket", "Decorative Tray", "Candle Holder", "LED Candle", "Scented Candle", "Decorative Lamp", "Room Fragrance", "Diffuser"]),
    ("Bedding", "Generic", ["Single Bedsheet Set", "Double Bedsheet Set", "Queen Bedsheet Set", "King Bedsheet Set", "Duvet", "Comforter", "Blanket", "Fleece Blanket", "Weighted Blanket", "Pillow", "Memory Foam Pillow", "Orthopedic Pillow", "Pillow Case", "Mattress Protector", "Mattress Topper", "Mosquito Net", "Bed Cover", "Duvet Cover"]),
    ("Bathroom", "Generic", ["Bath Towel", "Hand Towel", "Face Towel", "Bath Mat", "Shower Curtain", "Soap Dispenser", "Toothbrush Holder", "Toilet Brush", "Toilet Paper Holder", "Bathroom Shelf", "Bathroom Mirror", "Laundry Basket", "Storage Organizer", "Shower Caddy"]),
    ("Cleaning Supplies", "Generic", ["Broom", "Mop", "Bucket", "Dustpan", "Brush", "Scrub Brush", "Squeegee", "Duster", "Microfiber Cloth", "Cleaning Gloves", "Laundry Basket", "Trash Bin", "Dustbin Liners", "Spray Bottle", "Cleaning Caddy", "Sponge", "Dish Brush", "Dish Rack", "Drying Rack"]),

    # ─────────────────────────────────────────────────────────────────────
    # GROCERY EXPANSION & EVERYDAY CONSUMABLES
    # ─────────────────────────────────────────────────────────────────────
    ("Groceries - Staples", "Generic", ["Rice", "Basmati Rice", "Brown Rice", "Pishori Rice", "Sugar", "Wheat Flour", "Maize Flour", "Cassava Flour", "Millet Flour", "Sorghum Flour", "Cooking Oil", "Sunflower Oil", "Canola Oil", "Olive Oil", "Coconut Oil", "Salt", "Tea Leaves", "Coffee", "Cocoa Powder", "Peanut Butter", "Honey", "Jam", "Pasta", "Spaghetti", "Macaroni", "Beans", "Lentils", "Green Grams", "Chickpeas", "Canned Tomatoes", "Tomato Paste", "Canned Tuna", "Baking Flour", "Baking Powder", "Vanilla Essence", "Spices"]),
    ("Groceries - Snacks", "Generic", ["Biscuits", "Cookies", "Crackers", "Potato Crisps", "Popcorn", "Chocolate", "Sweets", "Gum", "Nuts", "Peanuts", "Cashews", "Raisins", "Dried Fruit", "Granola", "Cereal Bars"]),
    ("Groceries - Breakfast", "Generic", ["Corn Flakes", "Oats", "Porridge Flour", "Granola", "Cereal", "Tea", "Coffee", "Hot Chocolate", "Milk Powder", "UHT Milk", "Yoghurt", "Margarine", "Butter", "Cheese", "Bread", "Buns", "Peanut Butter", "Jam", "Honey"]),
    ("Groceries - Fresh & Frozen", "Generic", ["Fresh Milk", "Yoghurt", "Mala", "Eggs", "Sausages", "Bacon", "Chicken", "Beef", "Fish", "Frozen Vegetables", "Frozen Fries", "Frozen Chicken", "Ice Cream", "Fresh Fruits", "Fresh Vegetables"]),
    ("Beverages", "Generic", ["Bottled Water", "Flavoured Water", "Juice", "Fruit Juice", "Energy Drink", "Sports Drink", "Soft Drink", "Soda", "Malt Drink", "Iced Tea", "Instant Coffee", "Ground Coffee", "Tea Bags", "Hot Chocolate"]),

    # ─────────────────────────────────────────────────────────────────────
    # PETS, AGRICULTURE & GARDEN
    # ─────────────────────────────────────────────────────────────────────
    ("Pet Supplies", "Generic", ["Dog Food", "Cat Food", "Puppy Food", "Kitten Food", "Bird Seed", "Pet Treats", "Pet Bowl", "Pet Feeder", "Automatic Pet Feeder", "Pet Water Fountain", "Dog Collar", "Dog Leash", "Harness", "Pet Bed", "Pet Carrier", "Pet Crate", "Cat Litter Box", "Cat Litter", "Scratching Post", "Pet Shampoo", "Pet Brush", "Pet Nail Clipper", "Aquarium", "Fish Tank Filter", "Aquarium Pump", "Fish Food", "Pet Toys"]),
    ("Agriculture & Garden", "Generic", ["Garden Hose", "Hose Reel", "Watering Can", "Sprinkler", "Drip Irrigation Kit", "Garden Shears", "Pruning Secateurs", "Hedge Trimmer", "Garden Rake", "Hoe", "Jembe", "Shovel", "Spade", "Wheelbarrow", "Garden Gloves", "Plant Pot", "Seed Tray", "Plant Support", "Garden Net", "Shade Net", "Greenhouse Film", "Compost Bin", "Water Pump", "Pressure Sprayer", "Knapsack Sprayer", "Seedling Tray", "Bird Net"]),
    ("Farm Equipment", "Generic", ["Water Pump", "Solar Water Pump", "Sprayer", "Knapsack Sprayer", "Chaff Cutter", "Animal Feeder", "Poultry Drinker", "Poultry Feeder", "Beehive", "Egg Incubator", "Milk Can", "Dairy Bucket", "Digital Weighing Scale", "Farm Tool Set"]),

    # ─────────────────────────────────────────────────────────────────────
    # GENERAL MARKETPLACE CATCH-ALLS
    # ─────────────────────────────────────────────────────────────────────
    ("Safety & Security", "Generic", ["Padlock", "Combination Lock", "Door Lock", "Smart Lock", "Safe Box", "Key Safe", "Security Alarm", "Motion Sensor", "Door Sensor", "Smoke Detector", "Carbon Monoxide Detector", "Fire Blanket", "First Aid Kit", "Reflective Vest", "Safety Helmet", "Safety Goggles", "Work Gloves", "Ear Protection", "Dust Mask", "Warning Sign"]),
    ("Travel & Outdoor", "Generic", ["Travel Adapter", "Luggage Scale", "Neck Pillow", "Travel Pillow", "Eye Mask", "Travel Blanket", "Passport Holder", "Travel Wallet", "Water Bottle", "Thermal Flask", "Camping Tent", "Sleeping Bag", "Camping Chair", "Camping Table", "Camping Stove", "Portable Shower", "Torch", "Lantern", "Cooler Box", "Picnic Basket"]),
    ("Musical Instruments", "Generic", ["Acoustic Guitar", "Electric Guitar", "Bass Guitar", "Keyboard", "Digital Piano", "Ukulele", "Violin", "Recorder", "Flute", "Saxophone", "Trumpet", "Drum Kit", "Electronic Drum Kit", "Cajon", "Hand Drum", "Guitar Amp", "Keyboard Stand", "Music Stand", "Instrument Cable", "Guitar Strings", "Tuner", "Metronome", "Instrument Case", "Music Microphone"]),
]


def _flatten(groups):
    """Return unique (key, category, brand, product) catalog rows."""
    seen = set()
    rows = []
    for category, brand, products in groups:
        for product in products:
            key = f"{category}|{brand}|{product}"
            if key in seen:
                continue
            seen.add(key)
            rows.append((key, category, brand, product))
    return rows

ALL_CATALOG_ROWS = _flatten(BASE_CATALOG + VEHICLE_PARTS_CATALOG + CATALOG_EXPANSION)
ALL_CATALOG_KEYS = {row[0] for row in ALL_CATALOG_ROWS}


def catalog_datalist_options():
    """Browser-friendly labels for the seller's native searchable catalogue."""
    return [(row[0], f"{row[3]} — {row[1]} — {row[2]}") for row in ALL_CATALOG_ROWS]


def resolve_catalog_item(value):
    """Resolve a submitted key, product name or search phrase to a catalogue item."""
    text = str(value or "").strip()
    if not text or text.upper() == "CUSTOM PRODUCT":
        return None
    exact_key = next((r for r in ALL_CATALOG_ROWS if r[0].casefold() == text.casefold()), None)
    if exact_key:
        return {"key": exact_key[0], "category": exact_key[1], "brand": exact_key[2], "name": exact_key[3]}

    needle = text.casefold()
    candidates = []
    for key, category, brand, product in ALL_CATALOG_ROWS:
        haystack = f"{product} {brand} {category}".casefold()
        if needle == product.casefold():
            score = 0
        elif needle in product.casefold():
            score = 1
        elif needle in haystack:
            score = 2
        else:
            continue
        candidates.append((score, len(product), key, category, brand, product))

    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    _, _, key, category, brand, product = candidates[0]
    return {"key": key, "category": category, "brand": brand, "name": product}


def catalog_search_choices(limit=2500):
    """Return compact rows suitable for widgets/templates without duplicate entries."""
    return catalog_datalist_options()[:limit]
