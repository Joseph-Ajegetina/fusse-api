# Café Fausse API Backend

A Flask-based REST API backend for the Café Fausse restaurant website, providing reservation management, menu data, and newsletter subscription functionality.

## Features

- **Restaurant Reservations**: Table booking system with availability checking and random table assignment
- **Menu Management**: Dynamic menu display with categories (Starters, Main Courses, Desserts, Beverages)
- **Newsletter Subscription**: Email newsletter signup with validation
- **Database Management**: PostgreSQL with SQLAlchemy ORM
- **CORS Support**: Ready for React frontend integration

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Validation**: Email-validator
- **CORS**: Flask-CORS for frontend integration

## Project Structure

```
fusse-api/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── seed_data.py           # Database initialization and seed data
├── requirements.txt       # Python dependencies
├── routes/
│   ├── __init__.py
│   ├── reservations.py    # Reservation endpoints
│   ├── newsletter.py      # Newsletter subscription endpoints
│   └── menu.py           # Menu data endpoints
└── env/                   # Virtual environment (already created)
```

## Setup Instructions

### 1. Environment Setup

The virtual environment is already created. Activate it:

```bash
# On macOS/Linux
source env/bin/activate

# On Windows
env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Configuration

Create a `.env` file in the project root:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://cafe_user:cafe_password@localhost:5432/cafe_fausse_db

# Application Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. PostgreSQL Setup

Ensure PostgreSQL is running and create the database:

```sql
CREATE DATABASE cafe_fausse_db;
CREATE USER cafe_user WITH ENCRYPTED PASSWORD 'cafe_password';
GRANT ALL PRIVILEGES ON DATABASE cafe_fausse_db TO cafe_user;
```

### 5. Initialize Database

Run the seed script to create tables and populate initial data:

```bash
python seed_data.py
```

This will create:
- All database tables
- Menu categories and items (as per SRS requirements)
- 30 restaurant tables with varying capacities
- Default admin user

### 6. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /` - API status
- `GET /health` - Health check

### Reservations
- `POST /api/reservations` - Create a new reservation
- `POST /api/reservations/availability` - Check table availability
- `GET /api/reservations/<id>` - Get reservation details
- `PUT /api/reservations/<id>` - Update reservation status

### Menu
- `GET /api/menu` - Get complete menu with categories
- `GET /api/menu/categories` - Get all categories
- `GET /api/menu/category/<id>` - Get items for specific category
- `GET /api/menu/item/<id>` - Get specific menu item
- `GET /api/menu/search?q=<term>` - Search menu items

### Newsletter
- `POST /api/newsletter/subscribe` - Subscribe to newsletter
- `POST /api/newsletter/unsubscribe` - Unsubscribe from newsletter
- `GET /api/newsletter/subscribers` - Get all subscribers (admin)
- `GET /api/newsletter/check/<email>` - Check subscription status

## API Usage Examples

### Create a Reservation

```bash
curl -X POST http://localhost:5000/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "123-456-7890",
    "reservation_datetime": "2024-01-15T19:00:00",
    "num_of_guests": 4
  }'
```

### Check Table Availability

```bash
curl -X POST http://localhost:5000/api/reservations/availability \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_datetime": "2024-01-15T19:00:00",
    "num_of_guests": 4
  }'
```

### Get Full Menu

```bash
curl http://localhost:5000/api/menu
```

### Subscribe to Newsletter

```bash
curl -X POST http://localhost:5000/api/newsletter/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com"
  }'
```

## Database Schema

The application implements the following key models:

- **Customer**: customer_id, name, email, phone_number
- **Reservation**: reservation_id, customer_id, table_id, reservation_datetime, num_of_guests, status
- **Table**: table_id, table_number, capacity, is_active
- **Newsletter**: newsletter_id, email, date_subscribed, is_active
- **MenuCategory**: category_id, category_name, display_order, is_active
- **MenuItem**: item_id, category_id, item_name, description, price, is_available
- **Admin**: admin_id, username, password, email, is_active

## Business Logic

### Reservation System
- Validates reservation datetime is in the future
- Checks table availability for 2-hour time slots
- Randomly assigns available tables that can accommodate party size
- Prevents double bookings
- Supports up to 12 guests per reservation

### Table Management
- 30 tables total (as per requirements)
- Capacity distribution: 2-person (10), 4-person (12), 6-person (6), 8-person (2)
- Active/inactive status management

### Menu System
- Organized by categories with display ordering
- Item availability management
- Search functionality across names and descriptions

## Frontend Integration

This API is designed to work with a React frontend. Key integration points:

1. **CORS**: Configured for localhost:3000 (React dev server)
2. **JSON APIs**: All endpoints return JSON responses
3. **Error Handling**: Consistent error response format
4. **Validation**: Input validation with descriptive error messages

## Development Notes

- Default admin credentials: username `admin`, password `admin123`
- All passwords should be hashed in production
- Email validation is enforced for newsletter subscriptions
- The API includes comprehensive error handling and logging
- Database migrations can be managed with Flask-Migrate

## Requirements Compliance

This backend fulfills all functional requirements from the SRS:

- ✅ FR-6 to FR-9: Complete reservation system
- ✅ FR-15 to FR-16: Newsletter subscription with validation
- ✅ FR-17 to FR-18: PostgreSQL database with required tables and logic
- ✅ Menu data serving (FR-5 categories and items)
- ✅ Table availability checking and random assignment

## Testing

To test the API endpoints, you can use the provided curl examples or tools like Postman. The `/health` endpoint is useful for verifying the API is running correctly. 