// API Client for OpenStreetMap Backend
class APIClient {
  constructor() {
    this.baseURL = this.getBaseURL();
    this.token = localStorage.getItem("authToken");
  }

  getBaseURL() {
    // For development, use localhost:8000
    // In production, this should be your deployed backend URL
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      return "http://localhost:8000";
    }
    return window.location.origin;
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem("authToken", token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem("authToken");
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if token exists
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        // Handle authentication errors - try to refresh token
        if (
          (response.status === 401 || response.status === 403) &&
          data.detail &&
          data.detail.includes("Not authenticated")
        ) {
          console.log("Token expired or invalid, attempting refresh...");

          // Try to refresh token
          const refreshed = await this.refreshToken();

          if (refreshed) {
            // Retry request with new token
            config.headers.Authorization = `Bearer ${this.token}`;
            const retryResponse = await fetch(url, config);
            const retryData = await retryResponse.json();

            if (!retryResponse.ok) {
              throw new Error(
                retryData.detail ||
                  `HTTP error! status: ${retryResponse.status}`,
              );
            }

            return retryData;
          }
        }

        throw new Error(
          data.detail || `HTTP error! status: ${response.status}`,
        );
      }

      return data;
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  async refreshToken() {
    try {
      // Check if Firebase auth is available and user is signed in
      if (firebase.auth().currentUser) {
        const newToken = await firebase.auth().currentUser.getIdToken(true);
        this.setToken(newToken);
        console.log("Token refreshed successfully");
        return true;
      }
      return false;
    } catch (error) {
      console.error("Failed to refresh token:", error);
      return false;
    }
  }

  // Auth endpoints
  async login(token) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  }

  async getCurrentUser() {
    return this.request("/auth/me");
  }

  async checkAuth() {
    return this.request("/auth/check");
  }

  // Map endpoints
  async searchPlaces(query, limit = 10) {
    return this.request(
      `/map/search?query=${encodeURIComponent(query)}&limit=${limit}`,
    );
  }

  async reverseGeocode(lat, lon) {
    return this.request("/map/reverse", {
      method: "POST",
      body: JSON.stringify({ lat, lon }),
    });
  }

  async getRoute(startLat, startLon, endLat, endLon, profile = "driving") {
    return this.request("/map/route", {
      method: "POST",
      body: JSON.stringify({
        start_lat: startLat,
        start_lon: startLon,
        end_lat: endLat,
        end_lon: endLon,
        profile,
      }),
    });
  }

  async getNearestRoad(lat, lon, profile = "driving") {
    return this.request("/map/nearest", {
      method: "POST",
      body: JSON.stringify({ lat, lon, profile }),
    });
  }

  async getAlternativeRoutes(
    startLat,
    startLon,
    endLat,
    endLon,
    profile = "driving",
    alternatives = 3,
  ) {
    return this.request(
      `/map/alternatives?start_lat=${startLat}&start_lon=${startLon}&end_lat=${endLat}&end_lon=${endLon}&profile=${profile}&alternatives=${alternatives}`,
    );
  }

  // POI endpoints
  async getNearbyPOIs(lat, lon, radius = 1000, poiTypes = null) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
      radius: radius.toString(),
    });

    if (poiTypes && poiTypes.length > 0) {
      params.append("poi_types", poiTypes.join(","));
    }

    return this.request(`/poi/nearby?${params.toString()}`);
  }

  async getPOIsByType(poiType, lat, lon, radius = 1000) {
    return this.request(
      `/poi/type/${poiType}?lat=${lat}&lon=${lon}&radius=${radius}`,
    );
  }

  // Saved Places CRUD
  async createPlace(placeData) {
    return this.request("/poi/places", {
      method: "POST",
      body: JSON.stringify(placeData),
    });
  }

  async getPlaces() {
    return this.request("/poi/places");
  }

  async updatePlace(placeId, placeData) {
    return this.request(`/poi/places/${placeId}`, {
      method: "PUT",
      body: JSON.stringify(placeData),
    });
  }

  async deletePlace(placeId) {
    return this.request(`/poi/places/${placeId}`, {
      method: "DELETE",
    });
  }

  // Health check
  async healthCheck() {
    return this.request("/health");
  }
}

// Export as global variable
window.APIClient = new APIClient();
