"""
Database initialization and seed data script for Café Fausse
Run this script to populate the database with initial data
"""

from app import app, db
from models import MenuCategory, MenuItem, Table, Admin
from datetime import datetime

def init_database():
    """Initialize database and create all tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

def seed_menu_data():
    """Seed the database with menu categories and items from SRS requirements"""
    with app.app_context():
        try:
            # Check if menu data already exists
            if MenuCategory.query.first() and MenuItem.query.first():
                print("Menu data already exists. Skipping menu seeding.")
                return
            
            # Create menu categories
            categories = [
                {'name': 'Starters', 'order': 1},
                {'name': 'Main Courses', 'order': 2},
                {'name': 'Desserts', 'order': 3},
                {'name': 'Beverages', 'order': 4}
            ]
            
            category_objects = {}
            for cat_data in categories:
                category = MenuCategory(
                    category_name=cat_data['name'],
                    display_order=cat_data['order'],
                    is_active=True
                )
                db.session.add(category)
                db.session.flush()  # Get the ID
                category_objects[cat_data['name']] = category
            
            # Create menu items based on SRS requirements
            menu_items = [
                # Starters
                {
                    'category': 'Starters',
                    'name': 'Bruschetta',
                    'description': 'Fresh tomatoes, basil, olive oil, and toasted baguette slices',
                    'price': 8.50,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753924508/cafe-fusse/main/brusttac.png',
                    'order': 1
                },
                {
                    'category': 'Starters',
                    'name': 'Caesar Salad',
                    'description': 'Crisp romaine with homemade Caesar dressing',
                    'price': 9.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753924422/cafe-fusse/main/cfe699e3-eb10-4a95-be19-20668140c1f8.png',
                    'order': 2
                },
                
                # Main Courses
                {
                    'category': 'Main Courses',
                    'name': 'Grilled Salmon',
                    'description': 'Served with lemon butter sauce and seasonal vegetables',
                    'price': 22.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753924401/cafe-fusse/main/39595512-320a-482e-bc47-1e58071302ff.png',
                    'order': 1
                },
                {
                    'category': 'Main Courses',
                    'name': 'Ribeye Steak',
                    'description': '12 oz prime cut with garlic mashed potatoes',
                    'price': 28.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753922657/cafe-fusse/signatures/Ribeye%20Steak.png',
                    'order': 2
                },
                {
                    'category': 'Main Courses',
                    'name': 'Vegetable Risotto',
                    'description': 'Creamy Arborio rice with wild mushrooms',
                    'price': 18.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753923529/cafe-fusse/main/vegetable-risotto-creamy-arborio-rice-with-wild-mu_zrlxl8.png',
                    'order': 3
                },
                
                # Desserts (adding some since SRS mentions desserts but doesn't specify)
                {
                    'category': 'Desserts',
                    'name': 'Tiramisu',
                    'description': 'Classic Italian dessert with espresso and mascarpone',
                    'price': 7.50,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753923525/cafe-fusse/desserts/tiramisu-classic-italian-dessert-with-espresso-and_g5xgit.png',
                    'order': 1
                },
                {
                    'category': 'Desserts',
                    'name': 'Chocolate Lava Cake',
                    'description': 'Warm chocolate cake with molten center and vanilla ice cream',
                    'price': 8.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753922945/cafe-fusse/signatures/lava%20cake.png',
                    'order': 2
                },
                
                # Beverages
                {
                    'category': 'Beverages',
                    'name': 'Red Wine (Glass)',
                    'description': 'A selection of Italian reds',
                    'price': 10.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753923462/cafe-fusse/drinks/red-wine--glass-_aqegnp.png',
                    'order': 1
                },
                {
                    'category': 'Beverages',
                    'name': 'White Wine (Glass)',
                    'description': 'Crisp and refreshing',
                    'price': 9.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753923465/cafe-fusse/drinks/white-wine--glass-_ryalld.png',
                    'order': 2
                },
                {
                    'category': 'Beverages',
                    'name': 'Craft Beer',
                    'description': 'Local artisan brews',
                    'price': 6.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753923465/cafe-fusse/drinks/craft-beer_g7vwwc.png',
                    'order': 3
                },
                {
                    'category': 'Beverages',
                    'name': 'Espresso',
                    'description': 'Strong and aromatic',
                    'price': 3.00,
                    'image_url': 'https://res.cloudinary.com/duym3iexv/image/upload/v1753923467/cafe-fusse/drinks/espresso_eidkih.png',
                    'order': 4
                }
            ]
            
            for item_data in menu_items:
                category_obj = category_objects[item_data['category']]
                item = MenuItem(
                    category_id=category_obj.category_id,
                    item_name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    image_url=item_data['image_url'],
                    display_order=item_data['order'],
                    is_available=True
                )
                db.session.add(item)
            
            db.session.commit()
            print(f"Successfully seeded {len(menu_items)} menu items across {len(categories)} categories!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding menu data: {str(e)}")

def seed_tables():
    """Create 30 tables as specified in requirements (FR-8)"""
    with app.app_context():
        try:
            # Check if tables already exist
            if Table.query.first():
                print("Table data already exists. Skipping table seeding.")
                return
            
            # Create 30 tables with varying capacities
            tables_data = []
            
            # Create tables with different capacities
            # 10 tables for 2 people
            for i in range(1, 11):
                tables_data.append({'number': i, 'capacity': 2})
            
            # 12 tables for 4 people
            for i in range(11, 23):
                tables_data.append({'number': i, 'capacity': 4})
            
            # 6 tables for 6 people
            for i in range(23, 29):
                tables_data.append({'number': i, 'capacity': 6})
            
            # 2 tables for 8 people
            for i in range(29, 31):
                tables_data.append({'number': i, 'capacity': 8})
            
            for table_data in tables_data:
                table = Table(
                    table_number=table_data['number'],
                    capacity=table_data['capacity'],
                    is_active=True
                )
                db.session.add(table)
            
            db.session.commit()
            print(f"Successfully created {len(tables_data)} tables!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding tables: {str(e)}")

def seed_admin_user():
    """Create a default admin user"""
    with app.app_context():
        try:
            # Check if admin already exists
            if Admin.query.first():
                print("Admin user already exists. Skipping admin seeding.")
                return
            
            # Create default admin (password should be hashed in production)
            admin = Admin(
                username='admin',
                password='admin123',  # In production, this should be hashed
                email='admin@cafefausse.com',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Successfully created default admin user (username: admin, password: admin123)")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {str(e)}")

def run_all_seeds():
    """Run all seed functions"""
    print("Starting database initialization...")
    init_database()
    print("\nSeeding menu data...")
    seed_menu_data()
    print("\nSeeding tables...")
    seed_tables()
    print("\nSeeding admin user...")
    seed_admin_user()
    print("\nDatabase initialization complete!")

if __name__ == '__main__':
    run_all_seeds() 