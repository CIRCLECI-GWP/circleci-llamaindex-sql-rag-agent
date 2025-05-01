import json
import os
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create the base class for our models
Base = declarative_base()

# Define our State model
class State(Base):
    __tablename__ = 'states'
    
    id = sa.Column(sa.Integer, primary_key=True)
    object_id = sa.Column(sa.String(50), unique=True)
    name = sa.Column(sa.String(50), unique=True, nullable=False)
    flag_url = sa.Column(sa.String(255))
    link = sa.Column(sa.String(100))
    postal_abbreviation = sa.Column(sa.String(2), unique=True)
    capital = sa.Column(sa.String(50))
    largest_city = sa.Column(sa.String(50))
    established = sa.Column(sa.String(50))
    population = sa.Column(sa.Integer)
    total_area_square_miles = sa.Column(sa.Integer)
    total_area_square_kilometers = sa.Column(sa.Integer)
    land_area_square_miles = sa.Column(sa.Integer)
    land_area_square_kilometers = sa.Column(sa.Integer)
    water_area_square_miles = sa.Column(sa.Integer)
    water_area_square_kilometers = sa.Column(sa.Integer)
    number_representatives = sa.Column(sa.Integer)
    created_at = sa.Column(sa.String(100))
    updated_at = sa.Column(sa.String(100))
    capitals_object_id = sa.Column(sa.String(50))

def main():
    # Check if states.db exists and remove it before creating a new one
    db_file = 'states.db'
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Existing database '{db_file}' was deleted.")
        except Exception as e:
            print(f"Error: Failed to delete existing database. {e}")
            return

    # Connect to the database
    engine = sa.create_engine('sqlite:///states.db', echo=True)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Load the JSON data
    with open('states.json', 'r') as f:
        data = json.load(f)
        states_data = data.get('results', [])
    
    # Insert data
    for state_data in states_data:
        # Create a new State object
        state = State(
            object_id=state_data.get('objectId'),
            name=state_data.get('name'),
            flag_url=state_data.get('flag'),
            link=state_data.get('link'),
            postal_abbreviation=state_data.get('postalAbreviation'),
            capital=state_data.get('capital'),
            largest_city=state_data.get('largestCity'),
            established=state_data.get('established'),
            population=state_data.get('population'),
            total_area_square_miles=state_data.get('totalAreaSquareMiles'),
            total_area_square_kilometers=state_data.get('totalAreaSquareKilometers'),
            land_area_square_miles=state_data.get('landAreaSquareMiles'),
            land_area_square_kilometers=state_data.get('landAreaSquareKilometers'),
            water_area_square_miles=state_data.get('waterAreaSquareMiles'),
            water_area_square_kilometers=state_data.get('waterAreaSquareKilometers'),
            number_representatives=state_data.get('numberRepresentatives'),
            created_at=state_data.get('createdAt'),
            updated_at=state_data.get('updatedAt')
        )
        
        # Handle the capitals pointer
        if 'capitals' in state_data and isinstance(state_data['capitals'], dict):
            state.capitals_object_id = state_data['capitals'].get('objectId')
        
        # Add to session
        session.add(state)
    
    # Commit the session
    try:
        session.commit()
        print(f"Successfully imported {len(states_data)} states to the database.")
    except Exception as e:
        session.rollback()
        print(f"Error: Failed to commit data to database. {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()