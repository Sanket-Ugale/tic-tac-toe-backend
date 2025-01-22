# Tic-Tac-Toe Backend

This is the backend for a Tic-Tac-Toe game built using Django Rest Framework. The project includes user authentication, game management, real-time updates using WebSocket, and game history tracking. It also features production-level deployment using Docker and supports scalability with Redis and Celery.

## Features

- User Registration and Secure Login (JWT-based)
- Email-based OTP Verification using Celery
- Password Reset with Email Verification
- Real-time Tic-Tac-Toe Gameplay with WebSocket
- Game History Tracking and User Profile Management
- Production-ready with Docker and Redis
- Scalable and modular database design

## Tech Stack

**Backend Framework:** Django, Django Rest Framework  
**Real-time Communication:** Django Channels  
**Asynchronous Tasks:** Celery with Redis  
**Database:** SQLite  
**Deployment:** Docker, Render  
**API Testing Tool:** Postman

## Setup and Installation

### Prerequisites

- Python (>= 3.9)
- Docker and Docker Compose
- Redis
- Postman (optional, for testing APIs)

### Steps to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tic-tac-toe-backend.git
   cd tic-tac-toe-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run Redis Server:
   ```bash
   redis-server
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start Celery workers:
   ```bash
   celery -A tic_tac_toe worker --loglevel=info
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Documentation

### Authentication APIs

#### Sign Up
- **URL:** `/auth/user/signUp/`
- **Method:** POST
- **Body:**
  ```json
  {
    "email": "abc@xyz.com",
    "password": "abc@123"
  }
  ```

#### Login
- **URL:** `/auth/user/signIn/`
- **Method:** POST
- **Body:**
  ```json
  {
    "email": "abc@xyz.com",
    "password": "abc@123"
  }
  ```

#### Forgot Password
- **URL:** `/auth/forgotPassword/`
- **Method:** POST
- **Body:**
  ```json
  {
    "email": "abc@xyz.com"
  }
  ```

#### Reset Password
- **URL:** `/auth/resetPassword/`
- **Method:** POST
- **Body:**
  ```json
  {
    "email": "abc@xyz.com",
    "otp": "123456",
    "resetToken": "your-reset-token",
    "password": "newPassword",
    "confirmPassword": "newPassword"
  }
  ```

#### Verify OTP
- **URL:** `/auth/verifyOTP/`
- **Method:** POST
- **Body:**
  ```json
  {
    "email": "abc@xyz.com",
    "otp": "123456"
  }
  ```

### Game APIs

#### Create Game
- **URL:** `/api/games/create_game/`
- **Method:** POST
- **Headers:**
  ```json
  {
    "Authorization": "Bearer your-jwt-token"
  }
  ```

#### Join Game
- **URL:** `/api/games/join_game/`
- **Method:** POST
- **Body:**
  ```json
  {
    "room_code": "ROOM123"
  }
  ```

#### Game History
- **URL:** `/api/games/game_history/`
- **Method:** GET
- **Headers:**
  ```json
  {
    "Authorization": "Bearer your-jwt-token"
  }
  ```

#### Real-time Gameplay
- **WebSocket URL:** `ws://127.0.0.1:8000/ws/game/{room_code}/?token={jwt_token}`

## Deployment

The backend is deployed using Render and Docker for seamless production hosting. The production-ready setup includes:
- Docker Compose for running the application and Redis
- Celery Beat for managing periodic tasks (e.g., OTP expiration)

## Extra Features

- Production Deployment: Fully deployed backend and frontend with custom domains
- OTP Expiration: Implemented using Celery Beat to invalidate OTPs after 10 minutes
- WebSocket Integration: Real-time gameplay for a smooth user experience
- Comprehensive API Testing: Tested using Postman for all endpoints
