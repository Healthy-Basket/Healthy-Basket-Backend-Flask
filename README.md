# Healthy Basket Backend API

## Overview
The Healthy Basket Backend API is a Flask-based application that provides endpoints for user management, Google Fit integration, and Fitbit integration. This README will guide you through the process of setting up the project, installing dependencies, and understanding the available API endpoints.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Cloning the Repository](#cloning-the-repository)
- [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
- [Installing Dependencies](#installing-dependencies)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [User Management](#user-management)
  - [Google Fit Integration](#google-fit-integration)
  - [Fitbit Integration](#fitbit-integration)
- [Expected Outputs](#expected-outputs)
- [License](#license)

## Prerequisites
- Python 3.x
- Git
- A MongoDB instance (local or cloud)
- Familiarity with command line interface

## Cloning the Repository
To clone the repository, open your terminal and run the following command:
```
   https://github.com/Healthy-Basket/Healthy-Basket-Backend-Flask
```
## Setting Up a Virtual Environment
```
Navigate to the project directory:
cd repository_name


Create a virtual environment:
python -m venv venv


Activate the virtual environment:

On Windows:
.\venv\Scripts\activate


On macOS/Linux:
source venv/bin/activate
```

## Installing Dependencies
```
Upgrade pip:
python -m pip install --upgrade pip


Install the required packages from `requirements.txt`:

pip install -r requirements.txt
```


## Environment Variables
```
Create a `.env` file in the root of the project and add the following variables:
CLIENT_ID1=your_google_fit_client_id
CLIENT_SECRET1=your_google_fit_client_secret
REDIRECT_URI1=your_google_fit_redirect_uri
CLIENT_ID=your_fitbit_client_id
CLIENT_SECRET=your_fitbit_client_secret
REDIRECT_URI=your_fitbit_redirect_uri
```

Make sure to replace the placeholders with your actual credentials.

## Running the Application
To run the application, execute the following command:
python wsgi.py


The application will start on `http://127.0.0.1:5000/`.

## API Endpoints

### User Management
1. **POST /api/v1/saveuser**
   - **Description:** Saves a new user to the database.
   - **Request Body:**
     ```json
     {
       "username": "string",
       "email": "string"
     }
     ```
   - **Response:**
     - **Success (201):**
       ```json
       {
         "msg": "User saved successfully"
       }
       ```
     - **Error (400):**
       ```json
       {
         "error": "Invalid input"
       }
       ```

2. **POST /api/v1/signup**
   - **Description:** Registers a new user with email and password.
   - **Request Body:**
     ```json
     {
       "email": "string",
       "password": "string"
     }
     ```
   - **Response:**
     - **Success (201):**
       ```json
       {
         "message": "User registered successfully"
       }
       ```
     - **Error (400):**
       ```json
       {
         "error": "User already exists"
       }
       ```

3. **POST /api/v1/login**
   - **Description:** Logs in a user with email and password.
   - **Request Body:**
     ```json
     {
       "email": "string",
       "password": "string"
     }
     ```
   - **Response:**
     - **Success (200):**
       ```json
       {
         "message": "Logged in successfully"
       }
       ```
     - **Error (401):**
       ```json
       {
         "error": "Invalid email or password"
       }
       ```

### Google Fit Integration
4. **GET /googlefit/googlefit**
   - **Description:** Home route for Google Fit integration.
   - **Response:**
     ```html
     <h1>Welcome to the Healthy Basket API</h1><a href='/auth'>Authenticate with Google Fit</a>
     ```

5. **GET /googlefit/auth**
   - **Description:** Initiates the OAuth process for Google Fit authentication.
   - **Response:** Redirects to Google authentication page.

6. **GET /googlefit/callback**
   - **Description:** Handles the callback from Google after authentication.
   - **Response:**
     - **Success (200):**
       ```json
       {
         "message": "Google Fit authentication successful"
       }
       ```
     - **Error (400):**
       ```json
       {
         "error": "Authentication failed"
       }
       ```

### Fitbit Integration
7. **GET /fitbit/fitbit**
   - **Description:** Home route for Fitbit integration.
   - **Response:**
     ```html
     <h1>Welcome to the Healthy Basket API</h1><a href='/fitbit/auth'>Authenticate with Fitbit</a>
     ```

8. **GET /fitbit/auth**
   - **Description:** Initiates the OAuth process for Fitbit authentication.
   - **Response:** Redirects to Fitbit authentication page.

9. **GET /fitbit/callback**
   - **Description:** Handles the callback from Fitbit after authentication.
   - **Response:**
     - **Success (200):**
       ```json
       {
         "message": "Fitbit authentication successful"
       }
       ```
     - **Error (400):**
       ```json
       {
         "error": "Authentication failed"
       }
       ```

## Expected Outputs
- The `/api/v1/saveuser` endpoint will return a success message upon saving a user.
- The `/api/v1/signup` endpoint will return a success message upon successful registration.
- The `/api/v1/login` endpoint will return a success message upon successful login.
- The Google Fit and Fitbit authentication endpoints will redirect users to their respective authentication pages and return success messages upon successful authentication.

## License
This project is licensed under the MIT License - see the LICENSE file for details.