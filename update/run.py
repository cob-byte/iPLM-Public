import os
import mysql.connector
import json
import environ
from pathlib import Path

# Build paths - assuming this script is in the same directory as manage.py or settings.py
BASE_DIR = Path(__file__).resolve().parent

# Setup environment
env = environ.Env(
    # Set casting and default values
    DB_HOST=(str, 'localhost'),
    DB_USER=(str, 'root'),
    DB_PASSWORD=(str, ''),
    DB_PORT=(int, 3306),
    DB_NAME=(str, 'railway'),
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

try:
    print('\n  ---------------------------------------')
    print(' |   U P D A T I N G   D A T A B A S E   |')
    print('  ---------------------------------------\n')
    print('     ESTABLISHING CONNECTIONS\n')
    
    # Get database configuration from environment variables
    _db = mysql.connector.connect(
        host=env('DB_HOST'),
        user=env('DB_USER'),
        password=env('DB_PASSWORD'),
        port=env('DB_PORT')
    )
    print('             CONNECTED TO SERVER\n')

    Q = _db.cursor()

    db_exists = False # db exist boolean
    print("     LOCATING DATABASE\n")
    Q.execute('SHOW DATABASES')
    
    # Get database name from environment variables
    target_database = env('DB_NAME')
    
    # Check if database exists
    for exist_db in Q:
        if exist_db[0] == target_database:  # More reliable way to check
            print("             DATABASE LOCATED\n")
            db_exists = True
            break

    # Create database if it doesn't exist
    if not db_exists:
        print(f"     CREATING DATABASE: {target_database}\n")
        Q.execute(f"CREATE DATABASE IF NOT EXISTS `{target_database}`")
        print("             DATABASE CREATED\n")

    # Update database using config.json
    try:
        Q.execute(f'USE `{target_database}`')  # Use database name from settings
        to_file = os.path.join(BASE_DIR, "update")  # Path to config file (cross-platform)
        print("     LOCATING DATABASE CONFIGURATIONS\n")
        
        config_file_path = os.path.join(to_file, "config.json")
        with open(config_file_path, "r") as get_config:
            _config = json.load(get_config)
            print("             CONFIGURATIONS LOCATED\n")
            print("     APPLYING DATABASE UPDATES\n")
            print("              What's new ?\n")
            
            for x in _config:
                _events = x['events']
                try:
                    Q_events = f"CREATE TABLE IF NOT EXISTS crs_event (id INT AUTO_INCREMENT PRIMARY KEY, {_events['eventTitle']} TEXT, {_events['eventDescription']} TEXT, {_events['eventCategory']} TEXT, {_events['eventStartDate']} DATETIME, {_events['eventEndDate']} DATETIME)"
                    Q.execute(Q_events)
                    print("                 ADDED EVENTS TABLE\n")
                except Exception as e:
                    # Better error handling
                    print(f"\n QUERY ERROR: {str(e)}")
                    print(" " + Q_events)
                    
        # Commit changes
        _db.commit()
        print("     DATABASE UPDATES APPLIED\n")

        print('  ---------------------------------------------------------------------')
        print(' |   F I N I S H E D   R E Q U I R E D   S Y S T E M   U P D A T E S   |')
        print(' |        Y O U   C A N   R U N   T H E   S Y S T E M   N O W          |')
        print('  ---------------------------------------------------------------------')
        
    except FileNotFoundError:
        print("")
        for x in range(0, 5):
            print(" UNEXPECTED ERROR OCCURRED. PLEASE CHECK IF update/config.json EXISTS.")
        print(f" LOOKING FOR: {config_file_path}")
    except Exception as e:
        print(f"\n DATABASE UPDATE ERROR: {str(e)}")
        
    finally:
        # Always close the connection
        if '_db' in locals():
            _db.close()

except mysql.connector.Error as e:
    print(f"\n DATABASE CONNECTION ERROR: {str(e)}")
    print(f" HOST: {env('DB_HOST')}")
    print(f" USER: {env('DB_USER')}")
    print(f" PORT: {env('DB_PORT')}")
    print(f" DATABASE: {env('DB_NAME')}")
    for x in range(0, 5):
        print(' ERROR: SERVER CONNECTION FAILED. PLEASE CHECK DATABASE CONFIGURATION.')
except Exception as e:
    print(f"\n UNEXPECTED ERROR: {str(e)}")
    for x in range(0, 5):
        print(' ERROR: SERVER CONNECTION FAILED. PLEASE CHECK IF DATABASE SERVER IS RUNNING PROPERLY.')