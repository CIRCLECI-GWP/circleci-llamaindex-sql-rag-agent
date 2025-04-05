# import packages
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from db_creator import State

# Test if db was created and populated correctly
def test_database():
    """Test if the database was created and populated correctly."""
    print("\n----- TESTING DATABASE -----")
    
    # Connect to the database
    engine = sa.create_engine('sqlite:///states.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if the table exists
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        if 'states' not in tables:
            print("Error: 'states' table not found in database!")
            return
        
        # Count total records
        state_count = session.query(State).count()
        print(f"Total states in database: {state_count}")
        
        # Check a few specific states
        print("\nSample state data:")
        sample_states = ['Alabama', 'Alaska', 'Wyoming']
        for state_name in sample_states:
            state = session.query(State).filter_by(name=state_name).first()
            if state:
                print(f"- {state.name}: Capital: {state.capital}, Population: {state.population}")
            else:
                print(f"- {state_name}: Not found in database!")
        
        # Show schema details
        print("\nTable columns:")
        for column in inspector.get_columns('states'):
            print(f"- {column['name']}: {column['type']}")
            
        # Run some additional queries
        print("\nStates with population over 5 million:")
        populous_states = session.query(State).filter(State.population > 5000000).all()
        for state in populous_states:
            print(f"{state.name}: {state.population}")
            
        print("\nStates with largest city same as capital:")
        capital_largest = session.query(State).filter(State.capital == State.largest_city).all()
        for state in capital_largest:
            print(f"{state.name}: {state.capital}")
    
    finally:
        session.close()