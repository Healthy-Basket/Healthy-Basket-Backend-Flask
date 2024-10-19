from app import create_app  # Ensure you're importing the create_app function

app = create_app()  # Call the factory function to create the app

if __name__ == "__main__":
    app.run()  # Start the app if this script is executed directly
