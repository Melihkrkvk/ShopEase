"""
Seed script — populates the database directly without requiring a running server.

Usage:
    uv run python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import create_tables
from app.core.security import hash_password
from app.dao.user_dao import UserDAO
from app.dao.product_dao import ProductDAO


def main():
    engine = create_engine(settings.database_url)
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    user_dao = UserDAO(db)
    product_dao = ProductDAO(db)

    print("ShopEase Seed Script")
    print("=" * 40)

    # --- Users ---
    print("\n[1/2] Creating users...")

    if not user_dao.find_by_email("admin@shopease.com"):
        user_dao.insert({
            "email": "admin@shopease.com",
            "password": hash_password("admin123"),
            "name": "Admin",
        })
        db.execute(
            __import__("sqlalchemy").text("UPDATE users SET is_admin = 1 WHERE email = :e"),
            {"e": "admin@shopease.com"},
        )
        db.commit()
        print("  ✓ admin@shopease.com / admin123  (admin)")
    else:
        print("  - admin@shopease.com already exists, skipped")

    if not user_dao.find_by_email("user@shopease.com"):
        user_dao.insert({
            "email": "user@shopease.com",
            "password": hash_password("user123"),
            "name": "John Doe",
        })
        print("  ✓ user@shopease.com / user123")
    else:
        print("  - user@shopease.com already exists, skipped")

    # --- Products ---
    print("\n[2/2] Creating products...")

    products = [
        # Turntables
        {
            "name": "Audio-Technica AT-LP120XUSB",
            "price": 299.99,
            "stock": 12,
            "category": "turntables",
            "image_url": "https://picsum.photos/seed/atlp120/600/600",
            "description": "Direct-drive professional turntable with USB output. Features a built-in phono preamp, anti-skate control, and adjustable tracking force. Perfect for DJs and audiophiles alike.",
        },
        {
            "name": "Pro-Ject Debut Carbon EVO",
            "price": 499.99,
            "stock": 8,
            "category": "turntables",
            "image_url": "https://picsum.photos/seed/projectevo/600/600",
            "description": "Belt-drive audiophile turntable with a carbon fiber tonearm and Ortofon 2M Red cartridge. Precision engineering for pure, warm analog sound.",
        },
        {
            "name": "Rega Planar 1",
            "price": 475.00,
            "stock": 5,
            "category": "turntables",
            "image_url": "https://picsum.photos/seed/regaplanar/600/600",
            "description": "Award-winning entry-level audiophile turntable from Rega. Features a hand-assembled RB110 tonearm and Carbon MM cartridge. Simple, effective, musical.",
        },
        {
            "name": "Technics SL-1200MK7",
            "price": 1199.99,
            "stock": 4,
            "category": "turntables",
            "image_url": "https://picsum.photos/seed/technics1200/600/600",
            "description": "The legendary DJ turntable, reborn. Direct-drive motor with high torque, adjustable pitch control, and a built-in phono equalizer. The industry standard for over 50 years.",
        },
        # Vinyl
        {
            "name": "Pink Floyd — The Dark Side of the Moon",
            "price": 34.99,
            "stock": 25,
            "category": "vinyl",
            "image_url": "https://picsum.photos/seed/darkside/600/600",
            "description": "180g audiophile remaster of one of the best-selling albums of all time. Pressed at optimal fidelity, this 1973 classic has never sounded better on wax.",
        },
        {
            "name": "Miles Davis — Kind of Blue (180g)",
            "price": 29.99,
            "stock": 18,
            "category": "vinyl",
            "image_url": "https://picsum.photos/seed/kindofblue/600/600",
            "description": "The best-selling jazz album of all time on premium 180g vinyl. Modal improvisation at its finest — essential for any record collection.",
        },
        {
            "name": "Daft Punk — Random Access Memories",
            "price": 39.99,
            "stock": 15,
            "category": "vinyl",
            "image_url": "https://picsum.photos/seed/daftpunkram/600/600",
            "description": "Double LP pressing of the 2013 Grammy Album of the Year. Lush orchestral arrangements, disco grooves, and pristine production. A modern classic.",
        },
        {
            "name": "Arctic Monkeys — AM",
            "price": 27.99,
            "stock": 22,
            "category": "vinyl",
            "image_url": "https://picsum.photos/seed/arcticam/600/600",
            "description": "The definitive indie rock record of the 2010s on standard black vinyl. Heavy riffs, hip-hop influenced drums, and Alex Turner at his lyrical peak.",
        },
        {
            "name": "Kendrick Lamar — To Pimp a Butterfly",
            "price": 37.99,
            "stock": 10,
            "category": "vinyl",
            "image_url": "https://picsum.photos/seed/tpab/600/600",
            "description": "Double LP. One of the most critically acclaimed albums of the decade — jazz, funk, and spoken word woven into a powerful narrative.",
        },
        # Cartridges
        {
            "name": "Ortofon 2M Red MM Cartridge",
            "price": 99.00,
            "stock": 20,
            "category": "cartridges",
            "image_url": "https://picsum.photos/seed/ortofon2m/600/600",
            "description": "The world's best-selling phono cartridge. Moving magnet design with an elliptical stylus. Warm, detailed sound that punches well above its price point.",
        },
        {
            "name": "Audio-Technica VM95E",
            "price": 79.00,
            "stock": 15,
            "category": "cartridges",
            "image_url": "https://picsum.photos/seed/atvm95e/600/600",
            "description": "Elliptical stylus MM cartridge with dual moving magnet technology. Excellent channel separation and tracking ability. Upgradeable stylus system.",
        },
        # Preamps
        {
            "name": "Schiit Mani 2 Phono Preamp",
            "price": 149.00,
            "stock": 9,
            "category": "preamps",
            "image_url": "https://picsum.photos/seed/schiitmani/600/600",
            "description": "High-performance solid-state phono stage supporting MM and MC cartridges. Four gain settings, low noise floor, and built like a tank. Made in USA.",
        },
        {
            "name": "Pro-Ject Phono Box S2",
            "price": 129.00,
            "stock": 7,
            "category": "preamps",
            "image_url": "https://picsum.photos/seed/projectphono/600/600",
            "description": "Compact phono preamplifier with switchable MM/MC input. RIAA equalization, low noise design, and compact aluminum enclosure.",
        },
        # Accessories
        {
            "name": "Vinyl Record Cleaning Kit",
            "price": 24.99,
            "stock": 40,
            "category": "accessories",
            "image_url": "https://picsum.photos/seed/vinylclean/600/600",
            "description": "Complete cleaning kit including a carbon fiber brush, anti-static cleaning fluid, and microfiber cloth. Keep your records in pristine condition.",
        },
        {
            "name": "Record Outer Sleeves (50 pack)",
            "price": 14.99,
            "stock": 60,
            "category": "accessories",
            "image_url": "https://picsum.photos/seed/recordsleeves/600/600",
            "description": "Crystal clear polyethylene outer sleeves for 12-inch LP records. Protects covers from dust, moisture, and wear. 50 sleeves per pack.",
        },
        {
            "name": "Stylus Force Gauge (Digital)",
            "price": 19.99,
            "stock": 30,
            "category": "accessories",
            "image_url": "https://picsum.photos/seed/stylusgauge/600/600",
            "description": "Precision digital scale for measuring turntable stylus tracking force. Accurate to 0.01g. Essential for proper cartridge setup.",
        },
    ]

    existing_names = {
        row["name"]
        for row in db.execute(__import__("sqlalchemy").text("SELECT name FROM products")).mappings().all()
    }

    for p in products:
        if p["name"] in existing_names:
            print(f"  - [{p['category']}] {p['name']} already exists, skipped")
        else:
            product_dao.insert(p)
            print(f"  ✓ [{p['category']}] {p['name']} — ${p['price']}")

    db.close()

    print("\nDone!")
    print("\nCredentials:")
    print("  Admin : admin@shopease.com / admin123")
    print("  User  : user@shopease.com  / user123")


if __name__ == "__main__":
    main()
