# Step-by-Step Guide for Setting Up Environment Variables
>This document provides instructions for obtaining and setting up the necessary environment variables for deploying the application.

## MongoDB
1. Navigate to MongoDB Atlas:

* Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
* Sign in or create an account.
* Create a new cluster or use an existing one.
* In the cluster, navigate to the "Database Access" section to create a user with the necessary permissions.
* Go to the "Network Access" section to whitelist your IP address.
* In the "Clusters" section, click "Connect" and choose "Connect your application".
* Copy the connection string and replace the placeholder values with your database user credentials.
**Environment Variable:**
```
MONGO_URI=mongodb+srv://username:password@cluster-name.mongodb.net/database-name
```
## JWT (JSON Web Token)
1. Generate a JWT Secret Key:

* Use a secure method to generate a secret key. You can use online tools or libraries to generate a strong secret key.
**Environment Variable:**
```
JWT_SECRET_KEY=your_secret_key_here
```

## Fitbit API
1. Navigate to Fitbit Developer:

* Go to Fitbit Developer.
* Sign in or create an account.
* Create a new application.
* Note down the **CLIENT_ID** and **CLIENT_SECRET**.
* Set the REDIRECT_URI to your application's callback URL.
**Environment Variables:**
```
CLIENT_ID="xxxxxx"
CLIENT_SECRET="xxxxxxxxxxxxxxxxxxx"
FITBIT_AUTHORIZATION_URI="https://www.fitbit.com/oauth2/authorize"
TOKEN_REQUEST_URI="https://api.fitbit.com/oauth2/token"
REDIRECT_URI="https://example.com/callback"
```


## Google Fit API
1. Navigate to Google Cloud Console:

* Go to [Google Cloud Console](https://console.cloud.google.com/).
* Create a new project or select an existing one.
* Enable the "Fitness API".
* Go to "Credentials" and create OAuth 2.0 Client IDs for Web Application.
* Note down the CLIENT_ID1 and CLIENT_SECRET1.
* Set the REDIRECT_URI1 to your application's callback URL.
**Environment Variables:**
```
CLIENT_ID1  = "xxxxxxxxxxxx.apps.googleusercontent.com"
CLIENT_SECRET1 = "xxxxxxxxxxxxxxxxxxxx"
REDIRECT_URI1 = "https://example.com/oauth2callback"
```
## Google OAuth
1. Navigate to Google Cloud Console:

* Follow the same steps as for Google Fit API to create OAuth 2.0 Client IDs for Web Application.
* Note down the client_id and client_secret.
* Set the redirect_uri to your application's callback URL.
**Environment Variables**:
```
client_id = "xxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com"
client_secret = "GOxxxxxxxxxxxxxxxxxxxglYP"
redirect_uri = "https://example.com/google_callback"
```
## iOS Application
1. Navigate to Apple Developer:

* Go to [Apple Developer](https://developer.apple.com/).
* Sign in or create an account.
* Create a new App ID and configure it for your application.
* Note down the IOS_BUNDLE_ID.
* Create OAuth 2.0 Client IDs for iOS Application in Google Cloud Console.
* Note down the IOS_GOOGLE_CLIENT_ID.
**Environment Variables**:
```
IOS_BUNDLE_ID = "com.healthybasket.Healthy-basket"
IOS_GOOGLE_CLIENT_ID = "xxxxxxxxxxxxxxxx.apps.googleusercontent.com"
```
**Ensure all these environment variables are set in your .env file before deploying the application.**

*happy deployment*
