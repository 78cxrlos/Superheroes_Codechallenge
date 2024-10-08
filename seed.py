from app import app, db, Hero  

# Use the application context to perform database operations
with app.app_context():
    # Drop all tables (optional, only if you need to reset the database)
    db.drop_all()

    # Create all tables based on the models
    db.create_all()

    # Add seed data
    hero1 = Hero(name='Kamala Khan', super_name='Ms. Marvel')
    hero2 = Hero(name='Peter Parker', super_name='Spider-Man')
    hero3 = Hero(name='Carol Danvers', super_name='Captain Marvel')
    hero4 = Hero(name='Bruce Wayne', super_name='Batman')
    hero5 = Hero(name='Clark Kent', super_name='Superman')

    # Add the hero objects to the session
    db.session.add_all([hero1, hero2, hero3, hero4, hero5])

    # Commit the transaction to save data in the database
    db.session.commit()

    print("Database seeded successfully!")
