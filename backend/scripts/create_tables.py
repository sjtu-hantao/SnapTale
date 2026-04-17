import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import create_db_and_tables 


if __name__ == "__main__":
    create_db_and_tables()