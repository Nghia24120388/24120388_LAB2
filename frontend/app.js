// Main Application JavaScript
class MapApp {
  constructor() {
    this.map = null;
    this.currentUser = null;
    this.markers = [];
    this.routeLayer = null;
    this.routeMarkers = []; // Track start/end markers separately
    this.searchResults = [];
    this.savedPlaces = [];
    this.nearbyPOIs = [];
    this.selectedLocation = null;
    this.routeStart = null;
    this.routeEnd = null;
    this.isSigningIn = false;
    this.tokenRefreshInterval = null;

    // Firebase configuration
    this.firebaseConfig = {
      apiKey: "AIzaSyCBadoNmKiZGyjplw88ZI73UcFePgA5gdE",
      authDomain: "accommodation-project-49a8f.firebaseapp.com",
      databaseURL:
        "https://accommodation-project-49a8f-default-rtdb.firebaseio.com",
      projectId: "accommodation-project-49a8f",
      storageBucket: "accommodation-project-49a8f.firebasestorage.app",
      messagingSenderId: "756603304716",
      appId: "1:756603304716:web:d25c3bc028ad7b2a646729",
      measurementId: "G-DBY3NXG3R1",
    };

    this.init();
  }

  async init() {
    try {
      // Initialize Firebase
      this.initFirebase();

      // Check authentication status
      await this.checkAuthStatus();

      // Initialize map if authenticated
      if (this.currentUser) {
        this.initMap();
        this.bindEvents();
        this.loadSavedPlaces();
      } else {
        this.showAuthModal();
      }
    } catch (error) {
      console.error("App initialization failed:", error);
      this.showToast("App initialization failed", "error");
    }
  }

  initFirebase() {
    // Initialize Firebase with your configuration
    // Note: Replace with your actual Firebase config
    firebase.initializeApp(this.firebaseConfig);
    this.auth = firebase.auth();

    // Set up auth state listener
    this.auth.onAuthStateChanged((user) => {
      if (user) {
        // Don't show toast on auth state change - it's handled by login methods
        this.handleSuccessfulAuth(user, false);
      } else {
        this.handleLogout();
      }
    });
  }

  async checkAuthStatus() {
    try {
      const response = await window.APIClient.checkAuth();
      if (response.authenticated && response.user) {
        this.currentUser = response.user;
        window.APIClient.setToken(localStorage.getItem("authToken"));
        return true;
      }
      return false;
    } catch (error) {
      console.log("Not authenticated:", error.message);
      return false;
    }
  }

  showAuthModal() {
    document.getElementById("authModal").style.display = "block";
    // Only bind events once to prevent duplicate listeners
    if (!this.authEventsBound) {
      this.bindAuthEvents();
      this.authEventsBound = true;
    }
  }

  hideAuthModal() {
    document.getElementById("authModal").style.display = "none";
  }

  bindAuthEvents() {
    // Login button
    document.getElementById("loginBtn").addEventListener("click", () => {
      this.handleEmailLogin();
    });

    // Signup button
    document.getElementById("signupBtn").addEventListener("click", () => {
      this.handleEmailSignup();
    });

    // Google sign in
    document.getElementById("googleSignInBtn").addEventListener("click", () => {
      this.handleGoogleSignIn();
    });

    // Debounce rapid clicks to prevent popup conflicts
    this.googleSignInDebounced = this.debounce(() => {
      this.handleGoogleSignIn();
    }, 1000); // 1 second debounce

    // Enter key on password field
    document.getElementById("password").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.handleEmailLogin();
      }
    });
  }

  async handleEmailLogin() {
    // Prevent multiple simultaneous login attempts
    if (this.isSigningIn) {
      console.log("Sign in already in progress");
      return;
    }

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const errorDiv = document.getElementById("authError");

    if (!email || !password) {
      this.showAuthError("Please enter email and password");
      return;
    }

    this.isSigningIn = true;
    this.showLoading(true);
    errorDiv.style.display = "none";

    try {
      // Sign in with Firebase
      const userCredential = await this.auth.signInWithEmailAndPassword(
        email,
        password,
      );
      const token = await userCredential.user.getIdToken();

      // Send token to backend
      const response = await window.APIClient.login(token);

      this.handleSuccessfulAuth(response.user);
      window.APIClient.setToken(token);
    } catch (error) {
      console.error("Login failed:", error);
      this.showAuthError(error.message);
    } finally {
      this.showLoading(false);
      this.isSigningIn = false;
    }
  }

  async handleEmailSignup() {
    // Prevent multiple simultaneous signup attempts
    if (this.isSigningIn) {
      console.log("Sign in already in progress");
      return;
    }

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const errorDiv = document.getElementById("authError");

    if (!email || !password) {
      this.showAuthError("Please enter email and password");
      return;
    }

    if (password.length < 6) {
      this.showAuthError("Password must be at least 6 characters");
      return;
    }

    this.isSigningIn = true;
    this.showLoading(true);
    errorDiv.style.display = "none";

    try {
      // Create user with Firebase
      const userCredential = await this.auth.createUserWithEmailAndPassword(
        email,
        password,
      );
      const token = await userCredential.user.getIdToken();

      // Send token to backend
      const response = await window.APIClient.login(token);

      this.handleSuccessfulAuth(response.user);
      window.APIClient.setToken(token);
    } catch (error) {
      console.error("Signup failed:", error);
      this.showAuthError(error.message);
    } finally {
      this.showLoading(false);
      this.isSigningIn = false;
    }
  }

  async handleGoogleSignIn() {
    const errorDiv = document.getElementById("authError");
    this.showLoading(true);
    errorDiv.style.display = "none";

    // Prevent multiple simultaneous popup attempts
    if (this.isSigningIn) {
      console.log("Sign in already in progress");
      return;
    }

    this.isSigningIn = true;

    try {
      const provider = new firebase.auth.GoogleAuthProvider();
      const result = await this.auth.signInWithPopup(provider);
      const token = await result.user.getIdToken();

      // Send token to backend
      const response = await window.APIClient.login(token);

      this.handleSuccessfulAuth(response.user);
      window.APIClient.setToken(token);
    } catch (error) {
      console.error("Google sign in failed:", error);
      this.showAuthError(error.message);
    } finally {
      this.showLoading(false);
      this.isSigningIn = false;
    }
  }

  handleSuccessfulAuth(user, showToast = true) {
    this.currentUser = user;
    this.hideAuthModal();
    document.getElementById("app").style.display = "flex";
    document.getElementById("userEmail").textContent = user.email;

    if (!this.map) {
      this.initMap();
      this.bindEvents();
      this.loadSavedPlaces();
    }

    // Start periodic token refresh (every 30 minutes to prevent expiration)
    this.startTokenRefresh();

    // Only show toast if explicitly requested (prevents duplicates from auth state listener)
    if (showToast) {
      this.showToast("Successfully signed in!", "success");
    }
  }

  startTokenRefresh() {
    // Clear any existing interval first
    if (this.tokenRefreshInterval) {
      clearInterval(this.tokenRefreshInterval);
    }

    // Refresh token every 30 minutes (Firebase tokens expire after 1 hour)
    this.tokenRefreshInterval = setInterval(
      async () => {
        if (this.currentUser && firebase.auth().currentUser) {
          try {
            const newToken = await firebase.auth().currentUser.getIdToken(true);
            window.APIClient.setToken(newToken);
            console.log("Token refreshed proactively");
          } catch (error) {
            console.error("Failed to refresh token:", error);
          }
        }
      },
      30 * 60 * 1000,
    ); // 30 minutes
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        timeout = null;
        func(...args);
      };

      if (!timeout) {
        timeout = setTimeout(later, wait);
      } else {
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      }
    };
  }

  handleLogout() {
    this.currentUser = null;
    window.APIClient.clearToken();

    // Clear token refresh interval
    if (this.tokenRefreshInterval) {
      clearInterval(this.tokenRefreshInterval);
      this.tokenRefreshInterval = null;
    }

    document.getElementById("app").style.display = "none";
    this.showAuthModal();

    if (this.auth) {
      this.auth.signOut();
    }
  }

  showAuthError(message) {
    const errorDiv = document.getElementById("authError");
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
  }

  initMap() {
    // Initialize Leaflet map
    this.map = L.map("map").setView([40.7128, -74.006], 13); // Default to NYC

    // Add OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
      maxZoom: 19,
    }).addTo(this.map);

    // Add click event to map
    this.map.on("click", (e) => {
      this.handleMapClick(e.latlng);
    });

    // Try to get user's current location
    this.getCurrentLocation();
  }

  bindEvents() {
    // Search
    document.getElementById("searchBtn").addEventListener("click", () => {
      this.handleSearch();
    });

    document.getElementById("searchInput").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.handleSearch();
      }
    });

    // Current location
    document
      .getElementById("currentLocationBtn")
      .addEventListener("click", () => {
        this.getCurrentLocation();
      });

    // Logout
    document.getElementById("logoutBtn").addEventListener("click", () => {
      this.handleLogout();
    });

    // Sidebar toggle
    document.getElementById("toggleSidebar").addEventListener("click", () => {
      this.toggleSidebar();
    });

    // Tabs
    document.getElementById("searchTab").addEventListener("click", () => {
      this.switchTab("search");
    });

    document.getElementById("savedTab").addEventListener("click", () => {
      this.switchTab("saved");
    });

    document.getElementById("poiTab").addEventListener("click", () => {
      this.switchTab("poi");
    });

    // Add place button
    document.getElementById("addPlaceBtn").addEventListener("click", () => {
      this.showPlaceModal();
    });

    // POI search
    document.getElementById("searchPOI").addEventListener("click", () => {
      this.searchNearbyPOIs();
    });

    // Route buttons
    document.getElementById("routeBtn").addEventListener("click", () => {
      this.calculateRoute();
    });

    document.getElementById("clearRouteBtn").addEventListener("click", () => {
      this.clearRoute();
    });

    // Place modal
    document.getElementById("placeForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.savePlace();
    });

    document.querySelector(".cancel-btn").addEventListener("click", () => {
      this.hidePlaceModal();
    });

    document.querySelector(".close-btn").addEventListener("click", () => {
      this.hidePlaceModal();
    });
  }

  async handleSearch() {
    const query = document.getElementById("searchInput").value.trim();

    if (!query) {
      this.showToast("Please enter a search query", "warning");
      return;
    }

    this.showLoading(true);

    try {
      const results = await window.APIClient.searchPlaces(query);
      this.searchResults = results;
      this.displaySearchResults(results);

      // Fit map to show all results
      if (results.length > 0) {
        this.showSearchResultsOnMap(results);
      }
    } catch (error) {
      console.error("Search failed:", error);
      this.showToast("Search failed: " + error.message, "error");
    } finally {
      this.showLoading(false);
    }
  }

  displaySearchResults(results) {
    const container = document.getElementById("searchResultsList");

    if (results.length === 0) {
      container.innerHTML = '<p class="empty-state">No results found</p>';
      return;
    }

    container.innerHTML = results
      .map(
        (result, index) => `
            <div class="result-item" data-index="${index}">
                <h4>${result.display_name}</h4>
                <p>${this.formatAddress(result.address)}</p>
                <div class="meta">
                    <span>Type: ${result.type || "Unknown"}</span>
                    <span>Lat: ${result.lat.toFixed(4)}, Lng: ${result.lon.toFixed(4)}</span>
                </div>
                <div class="actions">
                    <button class="btn btn-small btn-primary" onclick="mapApp.goToLocation(${result.lat}, ${result.lon})">Go to</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.setRouteStart(${result.lat}, ${result.lon})">Set as Start</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.setRouteEnd(${result.lat}, ${result.lon})">Set as End</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.savePlaceFromSearch(${result.lat}, ${result.lon}, '${result.display_name.replace(/'/g, "\\'")}')">Save</button>
                </div>
            </div>
        `,
      )
      .join("");
  }

  showSearchResultsOnMap(results) {
    this.clearMarkers();

    const bounds = L.latLngBounds();

    results.forEach((result) => {
      const marker = L.marker([result.lat, result.lon])
        .addTo(this.map)
        .bindPopup(result.display_name);

      this.markers.push(marker);
      bounds.extend([result.lat, result.lon]);
    });

    this.map.fitBounds(bounds, { padding: [50, 50] });
  }

  async getCurrentLocation() {
    if (!navigator.geolocation) {
      this.showToast("Geolocation is not supported by your browser", "error");
      return;
    }

    this.showLoading(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        // Center map on user location
        this.map.setView([latitude, longitude], 15);

        // Add marker for user location
        L.marker([latitude, longitude])
          .addTo(this.map)
          .bindPopup("Your Location")
          .openPopup();

        // Get address for current location
        try {
          const address = await window.APIClient.reverseGeocode(
            latitude,
            longitude,
          );
          this.selectedLocation = {
            lat: latitude,
            lon: longitude,
            address: address.display_name,
          };
        } catch (error) {
          console.error("Failed to get address:", error);
        }

        this.showLoading(false);
        this.showToast("Location found!", "success");
      },
      (error) => {
        console.error("Geolocation error:", error);
        this.showToast("Failed to get your location", "error");
        this.showLoading(false);
      },
    );
  }

  handleMapClick(latlng) {
    this.selectedLocation = {
      lat: latlng.lat,
      lon: latlng.lng,
    };

    // Clear existing route if changing start point
    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
      this.routeLayer = null;
    }
    this.clearRouteMarkers();
    this.hideRouteDistance();

    // Automatically set as start point for routing
    this.routeStart = { lat: latlng.lat, lon: latlng.lng };
    this.showToast("Start point set", "info");
    this.updateRouteButtons();

    // Add start point marker
    this.clearMarkers();
    const startMarker = L.marker([latlng.lat, latlng.lng], {
      icon: L.divIcon({
        className: "start-marker",
        html: '<div style="background: #10b981; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: bold;">S</div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      }),
    })
      .addTo(this.map)
      .bindPopup("Start Point")
      .openPopup();

    this.markers.push(startMarker);

    // Get address for clicked location
    this.reverseGeocodeAndShow(latlng.lat, latlng.lng);
  }

  async reverseGeocodeAndShow(lat, lon) {
    try {
      const address = await window.APIClient.reverseGeocode(lat, lon);
      this.selectedLocation.address = address.display_name;

      // Show in sidebar
      const container = document.getElementById("searchResultsList");
      container.innerHTML = `
                <div class="result-item active">
                    <h4>${address.display_name}</h4>
                    <p>Lat: ${lat.toFixed(4)}, Lng: ${lon.toFixed(4)}</p>
                    <div class="actions">
                        <button class="btn btn-small btn-primary" onclick="mapApp.savePlaceFromSearch(${lat}, ${lon}, '${address.display_name.replace(/'/g, "\\'")}')">Save Place</button>
                        <button class="btn btn-small btn-secondary" onclick="mapApp.searchNearbyPOIsAt(${lat}, ${lon})">Find Nearby POI</button>
                    </div>
                </div>
            `;

      this.switchTab("search");
    } catch (error) {
      console.error("Failed to get address:", error);
    }
  }

  async searchNearbyPOIs() {
    if (!this.selectedLocation) {
      this.showToast("Please select a location on the map first", "warning");
      return;
    }

    this.searchNearbyPOIsAt(
      this.selectedLocation.lat,
      this.selectedLocation.lon,
    );
  }

  async searchNearbyPOIsAt(lat, lon) {
    this.showLoading(true);

    try {
      const poiType = document.getElementById("poiTypeSelect").value;
      console.log(
        `Searching POIs with type: "${poiType}" at lat:${lat}, lon:${lon}`,
      );

      const pois = await window.APIClient.getNearbyPOIs(
        lat,
        lon,
        1000,
        poiType ? [poiType] : null,
      );

      console.log(`Received ${pois.length} POIs from API`);
      this.nearbyPOIs = pois;
      this.displayPOIResults(pois);
      this.showPOIsOnMap(pois);

      this.switchTab("poi");
    } catch (error) {
      console.error("POI search failed:", error);
      this.showToast("POI search failed: " + error.message, "error");
    } finally {
      this.showLoading(false);
    }
  }

  displayPOIResults(pois) {
    const container = document.getElementById("poiResultsList");

    if (pois.length === 0) {
      container.innerHTML = '<p class="empty-state">No POI found nearby</p>';
      return;
    }

    container.innerHTML = pois
      .slice(0, 50)
      .map(
        (poi, index) => `
            <div class="result-item" data-poi-index="${index}">
                <h4>${poi.name}</h4>
                <p><strong>Category:</strong> ${poi.category}</p>
                ${poi.address ? `<p>${poi.address}</p>` : ""}
                ${poi.phone ? `<p>📞 ${poi.phone}</p>` : ""}
                ${poi.opening_hours ? `<p>🕒 ${poi.opening_hours}</p>` : ""}
                <div class="meta">
                    <span>Type: ${poi.type}</span>
                </div>
                <div class="actions">
                    <button class="btn btn-small btn-primary" onclick="mapApp.goToLocation(${poi.lat}, ${poi.lon})">Go to</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.setRouteStart(${poi.lat}, ${poi.lon})">Set as Start</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.setRouteEnd(${poi.lat}, ${poi.lon})">Set as End</button>
                    <button class="btn btn-small btn-success" onclick="mapApp.savePOIAsPlace(${poi.lat}, ${poi.lon}, '${poi.name.replace(/'/g, "\\'")}', '${poi.category.replace(/'/g, "\\'")}')">Save Place</button>
                </div>
            </div>
        `,
      )
      .join("");
  }

  showPOIsOnMap(pois) {
    this.clearMarkers();

    pois.forEach((poi, index) => {
      const popupContent = `
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0; color: #333;">${poi.name}</h4>
          <p style="margin: 4px 0; color: #666;">${poi.category}</p>
          ${poi.address ? `<p style="margin: 4px 0; font-size: 12px; color: #888;">${poi.address}</p>` : ""}
          <div style="margin-top: 8px; display: flex; gap: 4px; flex-wrap: wrap;">
            <button class="btn btn-small btn-primary" onclick="mapApp.setRouteEnd(${poi.lat}, ${poi.lon})">Set as End</button>
            <button class="btn btn-small btn-success" onclick="mapApp.savePOIAsPlace(${poi.lat}, ${poi.lon}, '${poi.name.replace(/'/g, "\\'")}', '${poi.category.replace(/'/g, "\\'")}')">Save</button>
          </div>
        </div>
      `;

      const marker = L.marker([poi.lat, poi.lon])
        .addTo(this.map)
        .bindPopup(popupContent, {
          maxWidth: 300,
          className: "poi-popup",
        });

      // Add click handler to marker
      marker.on("click", () => {
        marker.openPopup();
      });

      this.markers.push(marker);
    });
  }

  async loadSavedPlaces() {
    if (!this.currentUser) return;

    try {
      const places = await window.APIClient.getPlaces();
      this.savedPlaces = places;
      this.displaySavedPlaces();
      this.showSavedPlacesOnMap();
    } catch (error) {
      console.error("Failed to load saved places:", error);
    }
  }

  displaySavedPlaces() {
    const container = document.getElementById("savedPlacesList");

    console.log("Saved places data:", this.savedPlaces);
    console.log("Saved places type:", Array.isArray(this.savedPlaces));

    if (!this.savedPlaces || this.savedPlaces.length === 0) {
      container.innerHTML = '<p class="empty-state">No saved places yet</p>';
      return;
    }

    container.innerHTML = this.savedPlaces
      .map((place) => {
        console.log(`Place ID: ${place.id}, Place data:`, place);
        return `
            <div class="result-item" data-place-id="${place.id}">
                <h4>${place.name}</h4>
                ${place.description ? `<p>${place.description}</p>` : ""}
                ${place.address ? `<p>${place.address}</p>` : ""}
                ${place.category ? `<p><strong>Category:</strong> ${place.category}</p>` : ""}
                <div class="meta">
                    <span>Lat: ${place.lat.toFixed(4)}, Lng: ${place.lon.toFixed(4)}</span>
                </div>
                <div class="actions">
                    <button class="btn btn-small btn-primary" onclick="mapApp.goToLocation(${place.lat}, ${place.lon})">Go to</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.setRouteStart(${place.lat}, ${place.lon})">Set as Start</button>
                    <button class="btn btn-small btn-secondary" onclick="mapApp.setRouteEnd(${place.lat}, ${place.lon})">Set as End</button>
                    <button class="btn btn-small btn-danger" onclick="mapApp.deletePlace('${place.id}')">Delete</button>
                </div>
            </div>
        `;
      })
      .join("");
  }

  showSavedPlacesOnMap() {
    if (!this.savedPlaces || !Array.isArray(this.savedPlaces)) return;

    this.savedPlaces.forEach((place) => {
      const marker = L.marker([place.lat, place.lon])
        .addTo(this.map)
        .bindPopup(
          `<strong>${place.name}</strong><br>${place.description || ""}`,
        );

      this.markers.push(marker);
    });
  }

  showPlaceModal() {
    if (!this.selectedLocation) {
      this.showToast("Please select a location on the map first", "warning");
      return;
    }

    document.getElementById("placeModal").style.display = "block";

    // Pre-fill with selected location data if available
    if (this.selectedLocation.address) {
      document.getElementById("placeName").value =
        this.selectedLocation.address.split(",")[0];
      document.getElementById("placeAddress").value =
        this.selectedLocation.address;
    }
  }

  hidePlaceModal() {
    document.getElementById("placeModal").style.display = "none";
    document.getElementById("placeForm").reset();
  }

  async savePlace() {
    const name = document.getElementById("placeName").value;
    const category = document.getElementById("placeCategory").value;
    const description = document.getElementById("placeDescription").value;
    const address = document.getElementById("placeAddress").value;

    if (!name) {
      this.showToast("Please enter a place name", "warning");
      return;
    }

    if (!this.selectedLocation) {
      this.showToast("Please select a location on the map", "warning");
      return;
    }

    const placeData = {
      name,
      lat: this.selectedLocation.lat,
      lon: this.selectedLocation.lon,
      description,
      category,
      address,
      tags: {},
    };

    this.showLoading(true);

    try {
      await window.APIClient.createPlace(placeData);
      this.hidePlaceModal();
      this.loadSavedPlaces();
      this.showToast("Place saved successfully!", "success");
    } catch (error) {
      console.error("Failed to save place:", error);
      this.showToast("Failed to save place: " + error.message, "error");
    } finally {
      this.showLoading(false);
    }
  }

  async savePlaceFromSearch(lat, lon, displayName) {
    this.selectedLocation = { lat, lon, address: displayName };
    this.showPlaceModal();
  }

  async savePOIAsPlace(lat, lon, name, category) {
    const placeData = {
      name: name,
      lat: lat,
      lon: lon,
      description: `Saved from POI search - ${category}`,
      category: category || "poi",
      address: "",
      tags: { source: "poi_search" },
    };

    this.showLoading(true);

    try {
      await window.APIClient.createPlace(placeData);
      this.loadSavedPlaces();
      this.showToast("POI saved successfully!", "success");
    } catch (error) {
      console.error("Failed to save POI:", error);
      this.showToast("Failed to save POI: " + error.message, "error");
    } finally {
      this.showLoading(false);
    }
  }

  async deletePlace(placeId) {
    console.log("Attempting to delete place with ID:", placeId);
    console.log("Type of placeId:", typeof placeId);

    if (!confirm("Are you sure you want to delete this place?")) {
      return;
    }

    this.showLoading(true);

    try {
      console.log("Calling API to delete place:", placeId);
      await window.APIClient.deletePlace(placeId);
      this.loadSavedPlaces();
      this.showToast("Place deleted successfully!", "success");
    } catch (error) {
      console.error("Failed to delete place:", error);
      this.showToast("Failed to delete place: " + error.message, "error");
    } finally {
      this.showLoading(false);
    }
  }

  setRouteStart(lat, lon) {
    // Clear existing route if setting new start point
    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
      this.routeLayer = null;
    }
    this.clearRouteMarkers();
    this.hideRouteDistance();

    this.routeStart = { lat, lon };
    this.showToast("Start point set", "info");
    this.updateRouteButtons();
  }

  setRouteEnd(lat, lon) {
    // Clear existing route if setting new end point
    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
      this.routeLayer = null;
    }
    this.clearRouteMarkers();
    this.hideRouteDistance();

    this.routeEnd = { lat, lon };
    this.showToast("End point set", "info");
    this.updateRouteButtons();

    // Automatically calculate route if both points are set
    if (this.routeStart && this.routeEnd) {
      this.calculateRoute();
    }
  }

  updateRouteButtons() {
    const routeBtn = document.getElementById("routeBtn");
    const clearBtn = document.getElementById("clearRouteBtn");

    if (this.routeStart && this.routeEnd) {
      routeBtn.style.display = "inline-flex";
      clearBtn.style.display = "inline-flex";
    } else {
      routeBtn.style.display = "none";
      clearBtn.style.display = "none";
    }
  }

  async calculateRoute() {
    if (!this.routeStart || !this.routeEnd) {
      this.showToast("Please set both start and end points", "warning");
      return;
    }

    this.showLoading(true);

    try {
      const route = await window.APIClient.getRoute(
        this.routeStart.lat,
        this.routeStart.lon,
        this.routeEnd.lat,
        this.routeEnd.lon,
      );

      this.displayRoute(route);
      this.showToast("Route calculated successfully!", "success");
    } catch (error) {
      console.error("Failed to calculate route:", error);
      this.showToast("Failed to calculate route: " + error.message, "error");
    } finally {
      this.showLoading(false);
    }
  }

  displayRoute(route) {
    // Clear previous route layer and markers (but preserve route points)
    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
      this.routeLayer = null;
    }
    this.clearRouteMarkers();

    // Add route to map
    if (route.geometry && route.geometry.coordinates) {
      const latlngs = route.geometry.coordinates.map((coord) => [
        coord[1],
        coord[0],
      ]);
      this.routeLayer = L.polyline(latlngs, {
        color: "#667eea",
        weight: 5,
        opacity: 0.7,
      }).addTo(this.map);

      // Fit map to show route
      this.map.fitBounds(this.routeLayer.getBounds(), { padding: [50, 50] });
    }

    // Display route distance
    if (route.distance !== undefined) {
      console.log("Route calculated, distance:", route.distance, "meters");
      this.displayRouteDistance(route.distance);
    } else {
      console.warn("Route response missing distance field");
    }

    // Add markers for start and end with custom icons
    const startIcon = L.divIcon({
      className: "start-marker",
      html: '<div style="background: #10b981; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">S</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    const endIcon = L.divIcon({
      className: "end-marker",
      html: '<div style="background: #ef4444; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">E</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    const startMarker = L.marker([this.routeStart.lat, this.routeStart.lon], {
      icon: startIcon,
    })
      .addTo(this.map)
      .bindPopup("Start Point")
      .openPopup();
    this.routeMarkers.push(startMarker);

    const endMarker = L.marker([this.routeEnd.lat, this.routeEnd.lon], {
      icon: endIcon,
    })
      .addTo(this.map)
      .bindPopup("End Point")
      .openPopup();
    this.routeMarkers.push(endMarker);
  }

  clearRouteMarkers() {
    this.routeMarkers.forEach((marker) => {
      this.map.removeLayer(marker);
    });
    this.routeMarkers = [];
  }

  clearRoute() {
    if (this.routeLayer) {
      this.map.removeLayer(this.routeLayer);
      this.routeLayer = null;
    }
    this.clearRouteMarkers();

    this.routeStart = null;
    this.routeEnd = null;
    this.hideRouteDistance();
    this.updateRouteButtons();
  }

  displayRouteDistance(distanceMeters) {
    const routeInfo = document.getElementById("routeInfo");
    const distanceEl = document.getElementById("routeDistance");

    // Guard against missing elements
    if (!routeInfo || !distanceEl) {
      console.warn("Route distance elements not found in DOM");
      return;
    }

    // Format distance: show km if >= 1000m, otherwise show meters
    let formattedDistance;
    if (distanceMeters >= 1000) {
      formattedDistance = (distanceMeters / 1000).toFixed(2) + " km";
    } else {
      formattedDistance = Math.round(distanceMeters) + " m";
    }

    distanceEl.textContent = formattedDistance;
    routeInfo.style.display = "flex";
  }

  hideRouteDistance() {
    const routeInfo = document.getElementById("routeInfo");
    const distanceEl = document.getElementById("routeDistance");

    // Guard against missing elements
    if (!routeInfo || !distanceEl) {
      return;
    }

    distanceEl.textContent = "--";
    routeInfo.style.display = "none";
  }

  goToLocation(lat, lon) {
    this.map.setView([lat, lon], 16);

    // Add marker if not exists
    L.marker([lat, lon]).addTo(this.map).bindPopup("Location").openPopup();
  }

  clearMarkers() {
    this.markers.forEach((marker) => {
      this.map.removeLayer(marker);
    });
    this.markers = [];
  }

  toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("collapsed");
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    document.getElementById(`${tabName}Tab`).classList.add("active");

    // Update tab content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    document
      .getElementById(
        `${tabName === "search" ? "searchResults" : tabName === "saved" ? "savedPlaces" : "nearbyPOI"}`,
      )
      .classList.add("active");
  }

  formatAddress(address) {
    if (!address) return "";

    const parts = [
      address.house_number,
      address.road,
      address.suburb,
      address.city,
      address.state,
      address.postcode,
      address.country,
    ].filter((part) => part);

    return parts.join(", ");
  }

  showLoading(show) {
    const overlay = document.getElementById("loadingOverlay");
    overlay.style.display = show ? "flex" : "none";
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
            <span>${message}</span>
        `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.mapApp = new MapApp();
});
