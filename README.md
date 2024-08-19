This project is the capstone for the Coursera course on APIs from Meta Back-End Developer. It demonstrates the implementation of a RESTful API that includes user authentication, data retrieval, and secure API interactions. The project uses Python, Django, and Djoser for managing user registration and authentication, along with signed API calls to ensure data security and integrity. The goal is to build a functional API that can be integrated into larger applications.

# API endpoints
You can view the available API endpoints on the following address (GET request at endpoint): http://localhost:8000/api/

Also we have Djoser's endpoints:

- /api/users/
- /api/users/me/
- /api/users/confirm/
- /api/users/resend_activation/
- /api/users/set_password/
- /api/users/reset_password/
- /api/users/reset_password_confirm/
- /api/users/set_username/
- /api/users/reset_username/
- /api/users/reset_username_confirm/
- /api/token/login/ (Token Based Authentication)
- /api/token/logout/ (Token Based Authentication)

# Users

## Admin
- Id: 1
- Username: admin
- Password: admin@123
- Auth Token: 2691e1f81abbd147094acc1097840b6fc9709bb0

## Manager
- Id: 2
- Username: JoeManager
- Password: manager@123
- Auth Token: 1f80165145d1bb5b009b75f1efc8c1a55cfa233c

## Delivery Crew
- Id: 3
- Username: JohnDelivery
- Password: delivery@123
- Auth Token: a38f9c392a5b7d870f3e20de4f7b2ed665cac598

## Customers

### JaneDoe
- Id: 4
- Username: JaneDoe
- Password: jane@123
- Auth Token: 359b66caf9f1bba1f547726aee1ebd98f1e840d4

### ClaraDoe
- Id: 7
- Username: ClaraDoe
- Password: clara@123
-  Auth Token: b3b8ba0633e5a3ab361cdf7b20c80bccb4e03ad7