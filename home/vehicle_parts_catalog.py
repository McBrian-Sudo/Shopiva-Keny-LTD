"""Vehicle spare-parts catalogue extension for Shopiva sellers.

The catalogue covers common parts and consumables for cars, motorcycles and
bicycles. Sellers remain responsible for selecting the exact compatible part,
model/year and fitment details before publishing a listing.
"""

VEHICLE_PARTS_CATALOG = [
    ("Automotive Spare Parts - Cars", "Toyota", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm",
        "Ball Joint", "Tie Rod End", "Wheel Bearing", "CV Joint", "Drive Belt",
        "Timing Belt Kit", "Clutch Kit", "Radiator", "Water Pump", "Alternator",
        "Starter Motor", "Battery", "Headlamp", "Tail Lamp", "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Nissan", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm",
        "Ball Joint", "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit",
        "Radiator", "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp",
        "Tail Lamp", "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Subaru", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm", "Ball Joint",
        "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit", "Radiator",
        "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp", "Tail Lamp",
        "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Mazda", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm",
        "Ball Joint", "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit",
        "Radiator", "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp",
        "Tail Lamp", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Honda", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm",
        "Ball Joint", "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit",
        "Radiator", "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp",
        "Tail Lamp", "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Mitsubishi", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Glow Plugs", "Shock Absorbers", "Control Arm", "Ball Joint",
        "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit", "Radiator",
        "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp", "Tail Lamp",
        "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Isuzu", [
        "Oil Filter", "Air Filter", "Fuel Filter", "Diesel Fuel Filter", "Brake Pads",
        "Brake Shoes", "Brake Discs/Rotors", "Clutch Kit", "Clutch Plate", "Shock Absorbers",
        "Leaf Spring", "Wheel Bearing", "Universal Joint", "Water Pump", "Alternator",
        "Starter Motor", "Battery", "Radiator", "Headlamp", "Tail Lamp", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Mercedes-Benz", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Glow Plugs", "Shock Absorbers", "Control Arm", "Ball Joint",
        "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit", "Radiator",
        "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp", "Tail Lamp",
        "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Volkswagen", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm",
        "Ball Joint", "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit",
        "Radiator", "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp",
        "Tail Lamp", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Ford", [
        "Brake Pads", "Brake Discs/Rotors", "Oil Filter", "Air Filter", "Cabin Filter",
        "Fuel Filter", "Spark Plugs", "Ignition Coil", "Shock Absorbers", "Control Arm",
        "Ball Joint", "Tie Rod End", "Wheel Bearing", "CV Joint", "Clutch Kit",
        "Radiator", "Water Pump", "Alternator", "Starter Motor", "Battery", "Headlamp",
        "Tail Lamp", "Side Mirror", "Wiper Blades",
    ]),
    ("Automotive Spare Parts - Cars", "Generic", [
        "Brake Pads", "Brake Shoes", "Brake Discs/Rotors", "Brake Fluid", "Oil Filter",
        "Air Filter", "Cabin Filter", "Fuel Filter", "Spark Plugs", "Glow Plugs",
        "Ignition Coil", "Shock Absorbers", "Control Arm", "Ball Joint", "Tie Rod End",
        "Wheel Bearing", "CV Joint", "Drive Belt", "Timing Belt Kit", "Clutch Kit",
        "Clutch Plate", "Radiator", "Radiator Hose", "Water Pump", "Thermostat",
        "Alternator", "Starter Motor", "Battery", "Fuse Kit", "Bulbs", "Headlamp",
        "Tail Lamp", "Side Mirror", "Wiper Blades", "Wiper Motor", "Horn", "Jack",
        "Wheel Spacers", "Wheel Nuts", "Engine Mount", "Transmission Mount", "Air Conditioning Filter",
    ]),

    ("Motorcycle Spare Parts", "Bajaj", [
        "Brake Pads", "Brake Shoes", "Clutch Plates", "Clutch Cable", "Throttle Cable",
        "Chain & Sprocket Kit", "Drive Chain", "Sprocket", "Air Filter", "Oil Filter",
        "Spark Plug", "Ignition Coil", "Carburetor Repair Kit", "Fuel Tap", "Battery",
        "Rectifier/Regulator", "Starter Motor", "Wheel Bearing", "Fork Seal", "Shock Absorber",
        "Brake Lever", "Clutch Lever", "Side Mirror", "Headlamp", "Tail Lamp", "Indicators",
        "Speedometer Cable", "Tires", "Inner Tube",
    ]),
    ("Motorcycle Spare Parts", "TVS", [
        "Brake Pads", "Brake Shoes", "Clutch Plates", "Clutch Cable", "Throttle Cable",
        "Chain & Sprocket Kit", "Drive Chain", "Sprocket", "Air Filter", "Oil Filter",
        "Spark Plug", "Ignition Coil", "Battery", "Rectifier/Regulator", "Starter Motor",
        "Wheel Bearing", "Fork Seal", "Shock Absorber", "Brake Lever", "Clutch Lever",
        "Side Mirror", "Headlamp", "Tail Lamp", "Indicators", "Tires", "Inner Tube",
    ]),
    ("Motorcycle Spare Parts", "Honda", [
        "Brake Pads", "Brake Shoes", "Clutch Plates", "Clutch Cable", "Throttle Cable",
        "Chain & Sprocket Kit", "Drive Chain", "Sprocket", "Air Filter", "Oil Filter",
        "Spark Plug", "Ignition Coil", "Battery", "Rectifier/Regulator", "Starter Motor",
        "Wheel Bearing", "Fork Seal", "Shock Absorber", "Brake Lever", "Clutch Lever",
        "Side Mirror", "Headlamp", "Tail Lamp", "Indicators", "Tires", "Inner Tube",
    ]),
    ("Motorcycle Spare Parts", "Yamaha", [
        "Brake Pads", "Brake Shoes", "Clutch Plates", "Clutch Cable", "Throttle Cable",
        "Chain & Sprocket Kit", "Drive Chain", "Sprocket", "Air Filter", "Oil Filter",
        "Spark Plug", "Ignition Coil", "Battery", "Rectifier/Regulator", "Starter Motor",
        "Wheel Bearing", "Fork Seal", "Shock Absorber", "Brake Lever", "Clutch Lever",
        "Side Mirror", "Headlamp", "Tail Lamp", "Indicators", "Tires", "Inner Tube",
    ]),
    ("Motorcycle Spare Parts", "Generic", [
        "Brake Pads", "Brake Shoes", "Clutch Plates", "Clutch Cable", "Throttle Cable",
        "Chain & Sprocket Kit", "Drive Chain", "Front Sprocket", "Rear Sprocket", "Air Filter",
        "Oil Filter", "Spark Plug", "Ignition Coil", "Carburetor Repair Kit", "Fuel Tap",
        "Battery", "Rectifier/Regulator", "Starter Motor", "Wheel Bearing", "Fork Seal",
        "Shock Absorber", "Brake Lever", "Clutch Lever", "Side Mirror", "Headlamp",
        "Tail Lamp", "Indicators", "Horn", "Tires", "Inner Tube", "Tubeless Tire",
        "Kick Starter Lever", "Gear Shift Lever", "Foot Pegs", "Engine Gasket Set",
    ]),

    ("Bicycle Spare Parts", "Shimano", [
        "Brake Pads", "Brake Cable", "Gear Cable", "Chain", "Cassette", "Rear Derailleur",
        "Front Derailleur", "Shifter", "Crankset", "Bottom Bracket", "Chainring",
        "Freewheel", "Hub", "Hub Bearings", "Pedals", "Disc Brake Rotor", "Disc Brake Caliper",
        "Handlebar", "Stem", "Seatpost", "Saddle", "Bike Bell", "Chain Tool",
    ]),
    ("Bicycle Spare Parts", "SRAM", [
        "Brake Pads", "Brake Cable", "Gear Cable", "Chain", "Cassette", "Rear Derailleur",
        "Shifter", "Crankset", "Bottom Bracket", "Chainring", "Freehub Body", "Hub",
        "Pedals", "Disc Brake Rotor", "Disc Brake Caliper", "Handlebar", "Stem", "Seatpost",
        "Saddle", "Bike Bell",
    ]),
    ("Bicycle Spare Parts", "Generic", [
        "Brake Pads", "Brake Shoes", "Brake Cable", "Gear Cable", "Chain", "Chain Tensioner",
        "Cassette", "Freewheel", "Rear Derailleur", "Front Derailleur", "Shifter",
        "Crankset", "Bottom Bracket", "Chainring", "Hub", "Hub Bearings", "Spokes",
        "Rim", "Wheel Set", "Pedals", "Disc Brake Rotor", "Disc Brake Caliper", "Handlebar",
        "Stem", "Seatpost", "Saddle", "Kickstand", "Bike Bell", "Mudguards", "Bike Light",
        "Tyre", "Inner Tube", "Tubeless Tire", "Puncture Repair Kit", "Bike Pump", "Bottle Cage",
        "Rear Rack", "Front Rack", "Training Wheels",
    ]),
]


def vehicle_parts_choices():
    choices = [("", "Select a vehicle spare part")]
    for category, brand, products in VEHICLE_PARTS_CATALOG:
        for product in products:
            key = f"vehicle::{category}::{brand}::{product}"
            label = f"{brand} · {product} — {category.replace('Automotive Spare Parts - Cars', 'Cars').replace('Motorcycle Spare Parts', 'Motorcycles').replace('Bicycle Spare Parts', 'Bicycles')}"
            choices.append((key, label))
    return tuple(choices)


def vehicle_parts_item(key):
    if not key or not key.startswith("vehicle::"):
        return None
    try:
        _, category, brand, product = key.split("::", 3)
    except ValueError:
        return None
    for cat, maker, products in VEHICLE_PARTS_CATALOG:
        if cat == category and maker == brand and product in products:
            return {"name": f"{brand} {product}", "category": category}
    return None
