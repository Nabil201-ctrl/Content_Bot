# Import the AsyncIOMotorClient from the motor library for asynchronous MongoDB connections.
from motor.motor_asyncio import AsyncIOMotorClient
# Import the Optional type hint from the typing module.
from typing import Optional
# Import the settings object from the core.config module.
from .core.config import settings

# Declare a global variable 'client' of type AsyncIOMotorClient, initially set to None.
client: Optional[AsyncIOMotorClient] = None

# Asynchronous function to connect to the MongoDB database.
async def connect_to_mongo(app):
    # Access the global 'client' variable.
    global client
    try:
        # Create an instance of AsyncIOMotorClient using the MONGO_URI from the settings.
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        # Test the connection
        await client.admin.command('ismaster')
        # Assign the database instance to the app's state for access in other parts of the application.
        app.state.db = client[settings.DB_NAME]
        # Print a confirmation message to the console.
        print("Connected to MongoDB")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Starting app without MongoDB. Chat features will not work.")
        app.state.db = None

# Asynchronous function to close the MongoDB connection.
async def close_mongo_connection(app):
    # Access the global 'client' variable.
    global client
    # Check if the client instance exists.
    if client:
        # Close the MongoDB connection.
        client.close()
        # Print a confirmation message to the console.
        print("Disconnected from MongoDB")