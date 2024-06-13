# Django Rest Framework Social Media Application

### Features :-
- Signup (Using email-only)
- Login (Generates JWT Tokens) (using email & password(email-only)
- Search Feature (via email OR name) (Paginated Response)
- Send/ Accept/ Reject Friend Reques between users (With Throttling)
- List Friends API (Also used to list Mutual Friends)
- List Pending Friend Requests API

## Installation Steps :-
1. Install Docker
2. Install Postman (To check API endpoints)
3. Build docker image and up container :
   `$ docker-compose up build --d`

4. Check status of running instances :
   `$ docker-compose ps`

5. The App is available after successful startup of social_media container on following endpoint :-
   **http://0.0.0.0:8026/**

6. Open Postman and import following collection :-

The collection is named:  **__social_media_drf.postman_collection.json__**
It is included in the root directory in __master__ branch

## Steps for Successfully running Collection :-
1. Signup with **_valid_** email :-
   
Endpoint (POST) : http://0.0.0.0:8026/signup/users/

Request (JSON): {"email": <email_id>}

`Response : {
    "id": <user_id>,
    "email": <email_id>
}`


<img width="1792" alt="Screenshot 2024-06-13 at 12 59 03 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/91fbf40f-9fb6-4df2-80c6-05f64d693f5c">



2. Login with email (as username) and password (same as email).

Endpoint : http://0.0.0.0:8026/login/jwt/create/

Request (form_data): username:demo_user5@gmail.com
                     password:demo_user5@gmail.com

`Response : {
    "refresh": <refresh_token>,
    "access": <access_token>
}`
   

<img width="1792" alt="Screenshot 2024-06-13 at 1 00 16 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/1726fdc5-9131-4577-9da2-dd58f6268521">



3. Copy Access Token obtained from Login API Response.


<img width="1792" alt="Screenshot 2024-06-13 at 1 01 15 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/2536c7ff-7f81-47b6-a565-ccc8953b9409">


**Use this token as Bearer Authentication in each of the further APIs.**



4. Create User Profile with first_name, last_name :-

Endpoint (POST) : http://0.0.0.0:8026/accounts/profile/

Request (JSON): {"first_name": <first_name>,
                  "last_name": <last_name>}

`Response : {
    "user": <user_id>,
    "first_name": "test",
    "last_name": "user2"
}`

  
 <img width="1792" alt="Screenshot 2024-06-13 at 1 01 47 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/c838f3dc-7f33-4f39-a236-3e05152db5bc">



5. Search for any user via email OR name :-

Endpoint (GET) : http://0.0.0.0:8026/accounts/search/

Request (form-data): search_key:name OR email
                     search_val:e OR <exact_email>

`Response : {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "user": {
                "id": 8,
                "email": "user@example.in"
            },
            "first_name": "example",
            "last_name": "user",
            "name": "example user",
            "bio": ""
        },
   }
   ]}`
   

<img width="1792" alt="Screenshot 2024-06-13 at 1 32 48 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/4c42ceae-2ab5-4785-b6ba-0eef02b5d1fc">


   **You can use user_id for listed Profiles/Users to send Friend Requests in respective APIs.**



6. Send Friend Request :-

Endpoint (POST): http://0.0.0.0:8026/accounts/friend_request/

Request (json): {
                    "receiver_id": <receiver's user_id>
                }

`Response : {
    "response": "Friend request sent.",
    "friend_request_id": <friend_request_id>
}`

   
<img width="1792" alt="Screenshot 2024-06-13 at 1 35 34 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/39d1c583-4ee1-4f90-b3e4-1067d44bdf57">



7. Accept/Reject Friend Request :-

PS: You can only accept/reject friend request by logging in and using access tokens from the user the Request was sent to.

Endpoint (PUT): http://0.0.0.0:8026/accounts/friend_request_accept/<friend_request_id>/
 
 OR

http://0.0.0.0:8026/accounts/friend_request_decline/<friend_request_id>/

Request (None): None

`Response : {
    "response": "Friend request accepted."
}`

OR

`Response: {
    "response": "Friend request declined."
}`
   

<img width="1792" alt="Screenshot 2024-06-13 at 1 39 46 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/b47d229e-400a-465e-be16-397e5d7d4659">



8. List Pending Friend Request :-

Endpoint (GET): http://0.0.0.0:8026/accounts/friend_requests/<user_id>/

Request (None): None

`Response : {
    "friend_requests": [
        {
            "<friend_request_id>": "<sender_user>-<receiver_user>-<request_status>"
        }
    ]
}`

 
 <img width="1792" alt="Screenshot 2024-06-13 at 1 42 32 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/3ed1783a-f45c-44d6-bf33-ca4574bbb605">



9. List All Friends API :-

Endpoint (GET): http://0.0.0.0:8026/accounts/list/<user_id>

Request (None): None

`Response : {
    "this_user": {
        "username": "demo_user5@gmail.com",
        "user_id": 16
    },
    "friends": [
        [
            {
                "friend_username": "testuser2@gmail.com",
                "user_id": 13
            },
            true
        ]
    ]
}`

  
<img width="1792" alt="Screenshot 2024-06-13 at 1 43 15 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/1bb89017-2d33-497c-b68d-bb51e1bb773d">



10. Remove a Friend :-

Endpoint (POST): http://0.0.0.0:8026/accounts/friend_remove/

Request (json): {
                    "receiver_user_id": <receiver's user_id>
                }

`Response :{
    "response": "Successfully removed that friend."
}`


  <img width="1792" alt="Screenshot 2024-06-13 at 1 40 54 PM" src="https://github.com/Sherdil28/social_network/assets/57909176/85937dd1-c5a9-4c82-94c2-e1620f76e482">


   
   
