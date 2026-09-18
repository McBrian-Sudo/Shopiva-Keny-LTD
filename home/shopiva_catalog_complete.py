"""Supplemental marketplace catalogue for Shopiva.

This module fills common product gaps not covered by the original seller
catalogues. It is a taxonomy for seller listing/search, not live inventory.
"""

CATALOG_COMPLETE = [
    ("Computers & Laptops", "Universal", [
        "Laptop","Gaming Laptop","Business Laptop","Student Laptop","Chromebook","Desktop Computer","All-in-One Computer",
        "Mini PC","Workstation","Server","Tablet PC","2-in-1 Laptop","Laptop Stand","Laptop Sleeve","Laptop Bag",
        "Laptop Cooling Pad","Laptop Charger","Universal Laptop Charger","Laptop Battery","Laptop Screen","Laptop Keyboard",
        "Laptop Hinge","Laptop Dock","USB-C Dock","Desktop Monitor","Ultrawide Monitor","4K Monitor","Monitor Arm","Webcam",
    ]),
    ("Computer Components", "Universal", [
        "CPU","CPU Cooler","Motherboard","RAM","DDR4 RAM","DDR5 RAM","Graphics Card","GPU Cooler","SSD","NVMe SSD","SATA SSD",
        "Hard Disk Drive","External Hard Drive","External SSD","Power Supply Unit","PC Case","Case Fan","CPU Thermal Paste",
        "Wi-Fi Card","Bluetooth Adapter","Sound Card","Capture Card","USB Expansion Card","RAM Heatsink","Cable Management Kit",
        "PC Power Cable","DisplayPort Cable","HDMI Cable","DVI Cable","VGA Cable",
    ]),
    ("Computer Peripherals", "Universal", [
        "Keyboard","Mechanical Keyboard","Wireless Keyboard","Gaming Keyboard","Mouse","Wireless Mouse","Gaming Mouse",
        "Mouse Pad","Gaming Mouse Pad","Monitor Stand","Speakers","USB Speakers","Headset","Gaming Headset","Microphone",
        "USB Microphone","Conference Speaker","Graphics Tablet","Drawing Tablet","Barcode Scanner","USB Hub","Card Reader",
        "External DVD Drive","KVM Switch","USB Extension Cable","HDMI Switch","HDMI Splitter","Printer Cable","Ethernet Adapter",
    ]),
    ("TV, Audio & Home Entertainment", "Universal", [
        "Smart TV","Android TV","Google TV","LED TV","OLED TV","QLED TV","4K TV","Television Wall Mount","TV Stand",
        "Soundbar","Home Theatre System","AV Receiver","Bluetooth Speaker","Portable Speaker","Party Speaker","Subwoofer",
        "Bookshelf Speaker","Tower Speaker","Wireless Earbuds","Over-Ear Headphones","Noise Cancelling Headphones","FM Radio",
        "Digital Radio","DVD Player","Media Player","Streaming Stick","Streaming Box","Universal Remote","TV Antenna","Antenna Booster",
    ]),
    ("Cameras & Photography", "Universal", [
        "Digital Camera","Mirrorless Camera","DSLR Camera","Action Camera","Vlogging Camera","Instant Camera","Camcorder",
        "CCTV Camera","Dash Camera","Drone Camera","Camera Lens","Wide Angle Lens","Telephoto Lens","Portrait Lens",
        "Macro Lens","Camera Flash","LED Video Light","Camera Tripod","Monopod","Gimbal Stabilizer","Camera Bag","Memory Card",
        "Camera Battery","Battery Charger","Camera Strap","Lens Filter","Camera Cleaning Kit","Green Screen","Photo Backdrop","Light Stand",
    ]),
    ("Gaming", "Universal", [
        "Gaming Console","PlayStation Console","Xbox Console","Nintendo Console","Handheld Gaming Console","Gaming PC","Gaming Laptop",
        "Gaming Monitor","Gaming Chair","Gaming Desk","Game Controller","Wireless Controller","Racing Wheel","Flight Joystick",
        "VR Headset","VR Controller","Gaming Headset","Gaming Keyboard","Gaming Mouse","Gaming Mouse Pad","Console Carrying Case",
        "Console Charging Dock","Controller Charging Station","Game Storage Case","Game Disc","Game Accessory Kit","Capture Card",
        "Streaming Microphone","Gaming Speakers","Gaming Light",
    ]),
    ("Smartwatches & Wearables", "Universal", [
        "Smartwatch","Fitness Smartwatch","Kids Smartwatch","Rugged Smartwatch","Smart Band","Fitness Band","Smart Ring",
        "GPS Watch","Sports Watch","Smartwatch Strap","Leather Watch Strap","Metal Watch Strap","Silicone Watch Strap",
        "Watch Screen Protector","Watch Charger","Wireless Charging Dock","Smart Glasses","Fitness Tracker","Heart Rate Tracker",
        "Sleep Tracker","GPS Tracker","Bluetooth Tracker","Kids GPS Tracker","Pet GPS Tracker","Smartwatch Case",
    ]),
    ("Solar & Renewable Energy", "Universal", [
        "Solar Panel","Monocrystalline Solar Panel","Polycrystalline Solar Panel","Solar Inverter","Hybrid Inverter","Off-Grid Inverter",
        "Grid-Tie Inverter","Solar Charge Controller","MPPT Controller","PWM Controller","Solar Battery","Lithium Solar Battery",
        "Lead Acid Battery","Deep Cycle Battery","Solar Water Pump","Solar Street Light","Solar Flood Light","Solar Security Light",
        "Solar Garden Light","Solar Home System","Solar Lantern","Solar Fan","Solar Refrigerator","Solar Water Heater","Solar Cable",
        "MC4 Connector","Solar Mounting Bracket","Solar Combiner Box","DC Breaker","Solar Installation Kit",
    ]),
    ("Electrical & Power", "Universal", [
        "Electrical Wire","Single Core Cable","Twin Cable","Three Core Cable","Armoured Cable","Electrical Conduit","PVC Conduit",
        "Cable Trunking","Circuit Breaker","MCB Breaker","RCCB","RCBO","Fuse","Fuse Box","Distribution Board","Changeover Switch",
        "Isolator Switch","Contactor","Relay","Voltage Stabilizer","AVR","Inverter","UPS","Generator","Portable Generator",
        "Extension Cable","Extension Reel","Power Strip","Surge Protector","Voltage Tester",
    ]),
    ("Automotive Accessories & Consumables", "Universal", [
        "Car Battery","Car Battery Charger","Jump Starter","Engine Oil","Gear Oil","Brake Fluid","Coolant","Power Steering Fluid",
        "Transmission Fluid","Windshield Washer Fluid","Grease","Car Air Freshener","Car Floor Mats","Car Seat Covers","Steering Wheel Cover",
        "Car Sunshade","Car Phone Holder","Car Charger","USB Car Charger","Dash Camera","Parking Sensor","Reverse Camera",
        "LED Headlight Bulb","LED Fog Light","Car Horn","Wiper Blade","Car Vacuum Cleaner","Tyre Inflator","Tyre Pressure Gauge","Car Jack",
    ]),
    ("Motorcycles & Scooters", "Universal", [
        "Motorcycle Helmet","Open Face Helmet","Full Face Helmet","Modular Helmet","Helmet Visor","Helmet Liner","Motorcycle Jacket",
        "Motorcycle Gloves","Motorcycle Boots","Rain Suit","Riding Trousers","Motorcycle Cover","Top Box","Side Pannier","Tank Bag",
        "Motorcycle Phone Mount","USB Motorcycle Charger","Motorcycle Battery","Chain Kit","Chain Sprocket","Brake Pad","Brake Shoe",
        "Clutch Plate","Air Filter","Oil Filter","Spark Plug","Shock Absorber","Motorcycle Tyre","Inner Tube","Motorcycle Mirror",
    ]),
    ("Bicycles & Cycling", "Universal", [
        "Mountain Bike","Road Bike","Hybrid Bike","City Bike","BMX Bike","Gravel Bike","Electric Bicycle","Folding Bicycle","Kids Bicycle",
        "Tricycle","Bicycle Frame","Bicycle Fork","Wheel Set","Bicycle Tyre","Inner Tube","Rim Tape","Spokes","Hub","Freewheel",
        "Cassette","Chain","Crankset","Bottom Bracket","Pedals","Handlebar","Stem","Saddle","Seatpost","Bicycle Helmet","Cycling Gloves",
    ]),
    ("Restaurants & Catering Equipment", "Universal", [
        "Commercial Gas Cooker","Commercial Electric Cooker","Commercial Oven","Convection Oven","Pizza Oven","Commercial Fryer",
        "Grill","Charcoal Grill","Commercial Refrigerator","Display Chiller","Chest Freezer","Ice Maker","Commercial Blender",
        "Food Processor","Commercial Mixer","Meat Grinder","Sausage Machine","Coffee Machine","Espresso Machine","Coffee Grinder",
        "Water Boiler","Juicer","Food Warmer","Chafing Dish","Stainless Steel Table","Commercial Sink","Serving Tray","Food Container",
        "Takeaway Box","Disposable Food Container",
    ]),
    ("Packaging & Business Supplies", "Universal", [
        "Cardboard Box","Courier Bag","Poly Mailer","Bubble Wrap","Stretch Film","Packing Tape","Masking Tape","Packing Strap",
        "Shipping Label","Thermal Label","Barcode Label","Sticker Label","Product Sticker","Paper Bag","Gift Bag","Gift Box",
        "Food Packaging Bag","Vacuum Bag","Zip Lock Bag","Plastic Container","Plastic Cup","Paper Cup","Paper Plate","Disposable Cutlery",
        "Tissue Paper","Wrapping Paper","Bubble Mailer","Packing Peanuts","Pallet Wrap","Shipping Scale",
    ]),
    ("Industrial & Workshop Equipment", "Universal", [
        "Air Compressor","Pressure Washer","Welding Machine","MIG Welder","TIG Welder","Arc Welder","Welding Helmet","Welding Gloves",
        "Welding Rod","Bench Grinder","Bench Drill","Drill Press","Cut-Off Machine","Metal Cutting Saw","Hydraulic Jack","Bottle Jack",
        "Floor Jack","Engine Hoist","Workshop Crane","Tool Trolley","Tool Cabinet","Air Impact Wrench","Impact Socket Set","Bearing Puller",
        "Hydraulic Press","Grease Gun","Parts Washer","Work Light","Inspection Lamp","Workshop Fan",
    ]),
    ("Construction Tools & Equipment", "Universal", [
        "Concrete Mixer","Concrete Vibrator","Plate Compactor","Block Making Machine","Tile Cutter","Tile Saw","Tile Leveling Kit",
        "Laser Distance Meter","Laser Level","Theodolite","Spirit Level","Plumb Bob","Masonry Trowel","Brick Trowel","Float",
        "Cement Trowel","Hacksaw","Bolt Cutter","Crowbar","Pickaxe","Mattock","Wheelbarrow","Scaffolding","Ladder","Safety Harness",
        "Construction Helmet","Safety Boots","Reflective Jacket","Work Light","Extension Ladder",
    ]),
    ("Medical & Care Equipment", "Universal", [
        "Digital Thermometer","Blood Pressure Monitor","Pulse Oximeter","Glucometer","Glucometer Strips","Nebulizer","Medical Scale",
        "First Aid Kit","First Aid Box","Wheelchair","Walking Stick","Crutches","Walker","Commode Chair","Shower Chair","Bedside Rail",
        "Medical Examination Lamp","Stethoscope","Medical Gloves","Surgical Mask","Reusable Face Mask","Digital Weighing Scale",
        "Heating Pad","Cold Pack","Hot Water Bottle","Pill Organizer","Medicine Storage Box","Compression Socks","Knee Support","Back Support",
    ]),
    ("Beauty & Cosmetics", "Universal", [
        "Foundation","Concealer","Face Powder","Setting Powder","Blush","Highlighter","Bronzer","Eyeshadow Palette","Eyeliner",
        "Mascara","Lipstick","Lip Gloss","Lip Liner","Makeup Primer","Makeup Remover","Face Cleanser","Face Toner","Face Serum",
        "Face Moisturizer","Face Mask","Body Lotion","Body Scrub","Sunscreen","Perfume","Cologne","Deodorant","Hair Shampoo",
        "Hair Conditioner","Hair Oil","Hair Gel","Hair Spray",
    ]),
    ("Hair & Salon Equipment", "Universal", [
        "Hair Dryer","Professional Hair Dryer","Hair Straightener","Hair Curler","Curling Wand","Hair Clipper","Hair Trimmer",
        "Beard Trimmer","Electric Shaver","Hair Steamer","Salon Hair Steamer","Hair Wash Basin","Salon Chair","Barber Chair","Salon Trolley",
        "Salon Mirror","Barber Cape","Hair Brush","Detangling Brush","Hair Comb","Hair Scissors","Hair Razor","Hair Clippers Blade",
        "Hair Extension","Braiding Hair","Wig","Wig Stand","Hair Bonnet","Hair Rollers","Manicure Lamp",
    ]),
    ("Footwear", "Universal", [
        "Men's Sneakers","Women's Sneakers","Kids Sneakers","Running Shoes","Walking Shoes","Training Shoes","Football Boots",
        "Basketball Shoes","Tennis Shoes","Hiking Boots","Work Boots","Safety Boots","Formal Shoes","Loafers","Oxford Shoes",
        "Brogues","Sandals","Slides","Slippers","Heels","Wedges","Flats","Espadrilles","Rain Boots","School Shoes",
        "House Shoes","Beach Sandals","Shoe Insoles","Shoe Polish","Shoe Care Kit",
    ]),
    ("Fashion & Clothing", "Universal", [
        "T-Shirt","Polo Shirt","Dress Shirt","Casual Shirt","Formal Shirt","Blouse","Tank Top","Hoodie","Sweatshirt","Sweater",
        "Cardigan","Jacket","Leather Jacket","Rain Jacket","Blazer","Suit","Dress","Maxi Dress","Midi Dress","Skirt","Jeans",
        "Chinos","Cargo Pants","Trousers","Leggings","Joggers","Shorts","Tracksuit","School Uniform","Work Uniform",
    ]),
    ("Baby & Maternity", "Universal", [
        "Baby Bodysuit","Baby Romper","Baby Dress","Baby T-Shirt","Baby Trousers","Baby Socks","Baby Shoes","Baby Blanket",
        "Baby Swaddle","Baby Bib","Burp Cloth","Changing Mat","Changing Bag","Baby Carrier","Baby Sling","Baby Stroller",
        "Travel System","Baby Cot","Cot Mattress","Baby High Chair","Baby Feeding Bottle","Bottle Sterilizer","Bottle Warmer",
        "Breast Pump","Baby Monitor","Baby Bath Tub","Baby Nail Kit","Baby Thermometer","Maternity Pillow","Nursing Pillow",
    ]),
    ("Home Storage & Organization", "Universal", [
        "Storage Box","Plastic Storage Box","Fabric Storage Box","Storage Basket","Laundry Basket","Shoe Organizer","Shoe Rack",
        "Wardrobe Organizer","Drawer Organizer","Kitchen Organizer","Pantry Organizer","Fridge Organizer","Food Container",
        "Airtight Container","Spice Rack","Dish Rack","Cutlery Organizer","Bathroom Organizer","Under Bed Storage","Vacuum Storage Bag",
        "Clothes Hanger","Coat Hanger","Wall Shelf","Floating Shelf","Storage Cabinet","Filing Cabinet","Bookcase","Toy Storage Box","Tool Organizer","Cable Organizer",
    ]),
    ("Mattresses & Sleep", "Universal", [
        "Single Mattress","Double Mattress","Queen Mattress","King Mattress","Orthopedic Mattress","Memory Foam Mattress","Spring Mattress",
        "Pocket Spring Mattress","Foam Mattress","Mattress Topper","Mattress Protector","Pillow","Memory Foam Pillow","Orthopedic Pillow",
        "Neck Pillow","Pregnancy Pillow","Duvet","Comforter","Blanket","Fleece Blanket","Bedsheet Set","Duvet Cover","Pillow Case",
        "Mosquito Net","Bedspread","Electric Blanket","Sleep Mask","Bedside Lamp","Night Light","Bed Frame",
    ]),
    ("Water & Sanitation", "Universal", [
        "Water Tank","Plastic Water Tank","Water Storage Drum","Water Jerrycan","Water Filter","Water Purifier","Water Filter Cartridge",
        "RO Water Purifier","UV Water Purifier","Water Pump","Submersible Pump","Booster Pump","Pressure Pump","Float Valve","Ball Valve",
        "Gate Valve","Check Valve","Water Meter","Water Hose","Garden Hose","PVC Pipe","PPR Pipe","HDPE Pipe","Pipe Fitting",
        "Tap","Mixer Tap","Shower Head","Toilet Pan","Wash Basin","Water Heater",
    ]),
    ("Office Furniture & Equipment", "Universal", [
        "Office Desk","Executive Desk","Computer Desk","Reception Desk","Office Chair","Executive Chair","Visitor Chair","Meeting Table",
        "Filing Cabinet","Mobile Pedestal","Bookshelf","Office Partition","Whiteboard","Glass Board","Notice Board","Projector Screen",
        "Projector","Paper Shredder","Laminator","Binding Machine","Document Scanner","Printer Stand","Monitor Stand","Desk Organizer",
        "Ergonomic Footrest","Keyboard Tray","Cable Tray","Conference Phone","Office Clock","Office Safe",
    ]),
    ("School Supplies", "Universal", [
        "Exercise Book","Revision Book","Notebook","Drawing Book","Textbook","Dictionary","School Bag","Lunch Box","Water Bottle",
        "Pencil Case","Ballpoint Pen","Gel Pen","Pencil","Colored Pencil","Crayon","Marker","Highlighter","Eraser","Sharpener",
        "Ruler","Geometry Set","Calculator","Glue","Scissors","Stapler","File Folder","A4 Paper","Art Set","School Shoes","School Uniform",
    ]),
    ("Hobbies & Collectibles", "Universal", [
        "Jigsaw Puzzle","Board Game","Playing Cards","Chess Set","Checkers Set","Model Car","Model Aircraft","Action Figure","Collectible Figure",
        "Trading Card","Card Sleeves","Coin Album","Stamp Album","Stamp Set","Craft Kit","Sewing Kit","Knitting Kit","Embroidery Kit",
        "Beading Kit","Painting Kit","Sketchbook","Calligraphy Set","Woodworking Kit","Model Building Kit","Remote Control Model","Magic Set",
    ]),
    ("Music & Studio", "Universal", [
        "Acoustic Guitar","Electric Guitar","Bass Guitar","Classical Guitar","Ukulele","Keyboard","Digital Piano","Electronic Drum Kit",
        "Drum Kit","Cajon","Violin","Viola","Cello","Flute","Saxophone","Trumpet","Harmonica","Microphone","Condenser Microphone",
        "Dynamic Microphone","Audio Interface","Mixer","Studio Monitor","Headphone Amplifier","Guitar Amplifier","Keyboard Stand",
        "Microphone Stand","Music Stand","Instrument Cable","Guitar Strings",
    ]),
    ("Fishing & Outdoor Recreation", "Universal", [
        "Fishing Rod","Fishing Reel","Fishing Line","Fishing Hook","Fishing Lure","Fishing Tackle Box","Fishing Net","Fishing Float",
        "Fishing Swivel","Fishing Chair","Cooler Box","Camping Tent","Camping Mattress","Sleeping Bag","Camping Chair","Camping Table",
        "Camping Stove","Gas Camping Stove","Portable Lantern","Headlamp","Torch","Hiking Backpack","Dry Bag","Rain Poncho","Waterproof Jacket",
        "Hiking Boots","Trekking Poles","Binoculars","Compass","Portable Shower",
    ]),
    ("Pet Care & Aquatics", "Universal", [
        "Dog Food","Cat Food","Puppy Food","Kitten Food","Bird Seed","Fish Food","Pet Treats","Dog Bowl","Cat Bowl","Pet Feeder",
        "Automatic Pet Feeder","Water Fountain","Dog Collar","Dog Leash","Dog Harness","Pet Bed","Pet Carrier","Pet Crate","Cat Litter",
        "Litter Box","Scratching Post","Pet Shampoo","Pet Conditioner","Pet Brush","Pet Nail Clipper","Pet Toothbrush","Pet Toy","Bird Cage",
        "Aquarium","Aquarium Filter",
    ]),
    ("Agriculture & Livestock", "Universal", [
        "Seed","Seedling Tray","Fertilizer","Organic Fertilizer","Compost","Manure","Plant Pot","Nursery Bag","Garden Net","Shade Net",
        "Drip Irrigation Kit","Irrigation Pipe","Water Pump","Solar Water Pump","Knapsack Sprayer","Pressure Sprayer","Pesticide Sprayer",
        "Pruning Shears","Garden Shears","Hedge Trimmer","Brush Cutter","Lawn Mower","Chaff Cutter","Animal Feeder","Poultry Feeder",
        "Poultry Drinker","Egg Incubator","Beehive","Milk Can","Digital Farm Scale",
    ]),
    ("Sports Equipment", "Universal", [
        "Football","Football Boots","Football Jersey","Football Goal","Basketball","Basketball Hoop","Volleyball","Rugby Ball","Tennis Racket",
        "Tennis Balls","Badminton Racket","Badminton Shuttlecock","Table Tennis Table","Table Tennis Bat","Table Tennis Balls","Boxing Gloves",
        "Punching Bag","Skipping Rope","Yoga Mat","Exercise Mat","Dumbbell","Kettlebell","Barbell","Weight Plates","Resistance Bands",
        "Gym Bench","Treadmill","Exercise Bike","Elliptical Trainer","Sports Water Bottle",
    ]),
    ("Safety & Workwear", "Universal", [
        "Safety Helmet","Hard Hat","Safety Goggles","Face Shield","Ear Protection","Dust Mask","Respirator","Work Gloves","Cut Resistant Gloves",
        "Safety Vest","Reflective Jacket","Safety Boots","Steel Toe Boots","Rain Workwear","Work Trousers","Work Shirt","Coveralls",
        "Safety Harness","Fall Arrest Lanyard","Knee Pads","Elbow Pads","First Aid Kit","Fire Blanket","Fire Extinguisher","Warning Sign",
        "Cones","Barrier Tape","Safety Sign","Lockout Tag","Lockout Kit",
    ]),
    ("Retail Display & Shop Equipment", "Universal", [
        "Display Shelf","Retail Rack","Gondola Shelf","Checkout Counter","Cash Register","POS Terminal","Cash Drawer","Barcode Scanner",
        "Barcode Printer","Receipt Printer","Label Printer","Price Tag","Shopping Basket","Shopping Cart","Display Mannequin","Clothes Rack",
        "Glass Display Cabinet","Jewelry Display Case","Countertop Display","Acrylic Display Stand","Poster Stand","Banner Stand","Queue Barrier",
        "Store Sign","LED Store Sign","Digital Signage Display","Shopping Bag","Gift Wrapping Station","Security Tag","EAS Tag",
    ]),
]


def catalog_choices_complete():
    choices = []
    for category, brand, items in CATALOG_COMPLETE:
        for item in items:
            key = f"COMPLETE::{category}::{brand}::{item}"
            choices.append((key, f"{category} → {brand} → {item}"))
    return tuple(choices)


def catalog_item_complete(key):
    if not key or not str(key).startswith("COMPLETE::"):
        return None
    parts = str(key).split("::", 3)
    if len(parts) != 4:
        return None
    _, category, brand, name = parts
    for cat, br, items in CATALOG_COMPLETE:
        if cat == category and br == brand and name in items:
            return {"key": key, "category": category, "brand": brand, "name": name}
    return None
