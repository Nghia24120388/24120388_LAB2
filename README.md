# OpenStreetMap Web Application

A Google Maps-like web application built with FastAPI backend and vanilla JavaScript frontend, using OpenStreetMap APIs and Firebase for authentication and data storage.

## Features

### Core Functionality
- **Interactive Map**: Full-screen map using Leaflet.js and OpenStreetMap tiles
- **Search**: Location search using Nominatim API
- **Routing**: Turn-by-turn directions using OSRM API
- **POI Discovery**: Find nearby points of interest using Overpass API
- **Geolocation**: Get user's current location
- **Reverse Geocoding**: Get address from coordinates

### Authentication & Data
- **Firebase Auth**: Email/password and Google sign-in
- **User Data Storage**: Firebase Realtime Database
- **Saved Places**: CRUD operations for personal locations

### User Interface
- **Google Maps-like Design**: Clean, modern interface
- **Responsive**: Works on desktop and mobile
- **Sidebar**: Organized results and saved places
- **Real-time Updates**: Dynamic map interactions

## Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   └── firebase_config.py  # Firebase configuration and utilities
│   ├── dependencies/
│   │   └── auth.py            # Authentication dependencies
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── map.py             # Map and routing endpoints
│   │   └── poi.py             # POI and saved places endpoints
│   ├── schemas/
│   │   ├── auth.py            # Authentication schemas
│   │   ├── map.py             # Map-related schemas
│   │   └── poi.py             # POI and place schemas
│   └── services/
│       ├── firebase_service.py # Firebase operations
│       ├── nominatim_service.py # Nominatim API integration
│       ├── overpass_service.py # Overpass API integration
│       └── osrm_service.py    # OSRM routing API
└── run.py                     # Development server runner
```

### Frontend (Vanilla JS)
```
frontend/
├── index.html                 # Main HTML file
├── styles.css                 # Complete CSS styling
├── api_client.js              # API communication layer
└── app.js                     # Main application logic
```

## API Endpoints

### Authentication
- `POST /auth/login` - Login with Firebase token
- `GET /auth/me` - Get current user info
- `GET /auth/check` - Check authentication status

### Map Operations
- `GET /map/search` - Search for places
- `POST /map/reverse` - Reverse geocoding
- `POST /map/route` - Get route between points
- `POST /map/nearest` - Find nearest road

### POI Operations
- `GET /poi/nearby` - Get nearby POIs
- `GET /poi/type/{poi_type}` - Get POIs by type
- `POST /poi/places` - Save a place
- `GET /poi/places` - Get user's saved places
- `PUT /poi/places/{id}` - Update a place
- `DELETE /poi/places/{id}` - Delete a place

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js (optional, for development tools)
- Firebase account

### 1. Firebase Setup

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project"
   - Follow the setup wizard

2. **Enable Authentication**
   - In Firebase Console, go to Authentication
   - Enable "Email/Password" sign-in method
   - Enable "Google" sign-in method
   - Add your domain to authorized domains (localhost for development)

3. **Set up Realtime Database**
   - In Firebase Console, go to Realtime Database
   - Click "Create Database"
   - Choose "Start in test mode" (for development)
   - Copy your database URL

4. **Get Service Account Key**
   - Go to Project Settings → Service accounts
   - Click "Generate new private key"
   - Download the JSON file
   - Keep this file secure!

5. **Get Web App Configuration**
   - In Firebase Console, go to Project Settings → General
   - Under "Your apps", click the web app icon
   - Copy the Firebase configuration object

### 2. Backend Setup

1. **Clone and Navigate**
   ```bash
   cd OpenStreetMapAPI/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy the example file
   cp ../.env.example .env
   
   # Edit .env with your Firebase credentials
   # You need to convert your service account JSON to a single line
   # Example: FIREBASE_CONFIG={"type":"service_account",...}
   ```

5. **Update Firebase Configuration in Frontend**
   - Open `frontend/app.js`
   - Replace the `firebaseConfig` object with your actual Firebase config
   - Update `frontend/api_client.js` baseURL if needed for production

### 3. Run the Application

1. **Start Backend Server**
   ```bash
   cd backend
   python run.py
   ```
   
   The API will be available at `http://localhost:8000`

2. **Open Frontend**
   - Open `frontend/index.html` in your browser
   - Or serve it with a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   Then visit `http://localhost:3000`

### 4. Using the Application

1. **Authentication**
   - Sign up with email/password or use Google sign-in
   - Your user data will be stored in Firebase

2. **Map Features**
   - Search for locations using the search bar
   - Click on the map to select locations
   - Use the location button to find your current position
   - Set start/end points and calculate routes

3. **POI Discovery**
   - Click on the map, then use "Find Nearby POI"
   - Filter by POI types (restaurants, hotels, etc.)
   - Results appear in the sidebar

4. **Saved Places**
   - Save any location by clicking "Save Place"
   - View and manage your saved places
   - Add descriptions and categories

## Development

### Running in Development Mode

1. **Backend with Auto-reload**
   ```bash
   cd backend
   python run.py
   # Or with uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend with Live Reload**
   ```bash
   cd frontend
   python -m http.server 3000
   ```

### API Documentation

- Visit `http://localhost:8000/docs` for interactive API documentation
- All endpoints are documented with OpenAPI/Swagger

### Environment Variables

```bash
# Required
FIREBASE_CONFIG=your_firebase_service_account_json_as_string
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/

# Optional
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## Production Deployment

### Backend Deployment

1. **Environment Setup**
   - Set production environment variables
   - Use HTTPS for Firebase Auth callbacks

2. **Server Options**
   - Use Gunicorn with Uvicorn workers:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Docker Deployment**
   - Build with the provided Dockerfile (if created)
   - Expose port 8000

### Frontend Deployment

1. **Static Hosting**
   - Deploy to Netlify, Vercel, or GitHub Pages
   - Update the API base URL in `api_client.js`

2. **CORS Configuration**
   - Update FastAPI CORS settings for your domain

## API Usage Limits

### OpenStreetMap APIs
- **Nominatim**: 1 request/second max
- **Overpass**: Variable, be considerate
- **OSRM**: Public instance has limits

### Recommendations
- Implement caching for frequently requested data
- Add rate limiting for production
- Consider self-hosting OSRM for high usage

## Troubleshooting

### Common Issues

1. **Firebase Authentication Errors**
   - Check your Firebase configuration
   - Ensure authorized domains include your development URL
   - Verify service account permissions

2. **CORS Errors**
   - Check backend CORS configuration
   - Ensure frontend URL is allowed

3. **Map Not Loading**
   - Check Leaflet.js CDN access
   - Verify internet connection for tile loading

4. **API Errors**
   - Check OpenStreetMap API status
   - Verify rate limits aren't exceeded

### Debug Mode

Enable debug logging:
```bash
DEBUG=True python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **Firebase Admin SDK**: Authentication and database
- **HTTPX**: Async HTTP client
- **Pydantic**: Data validation

### Frontend
- **Leaflet.js**: Interactive maps
- **Firebase JS SDK**: Client-side authentication
- **Vanilla JavaScript**: No framework dependencies
- **CSS3**: Modern styling

### External APIs
- **OpenStreetMap**: Map tiles and data
- **Nominatim**: Geocoding and search
- **Overpass**: POI data queries
- **OSRM**: Routing and navigation

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Create an issue on GitHub

---

**Note**: This is a demonstration application. For production use, consider additional security measures, error handling, and performance optimizations.
