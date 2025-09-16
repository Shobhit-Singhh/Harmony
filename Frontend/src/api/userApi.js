import { API_BASE_URL, STORAGE_KEYS } from '../utils/constants';

// In-memory storage for Claude artifacts (fallback when localStorage isn't available)
let memoryStorage = {};

// Storage wrapper to handle both localStorage and in-memory storage
const storage = {
    getItem: (key) => {
        if (typeof localStorage !== 'undefined') {
            return localStorage.getItem(key);
        }
        return memoryStorage[key] || null;
    },

    setItem: (key, value) => {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem(key, value);
        } else {
            memoryStorage[key] = value;
        }
    },

    removeItem: (key) => {
        if (typeof localStorage !== 'undefined') {
            localStorage.removeItem(key);
        } else {
            delete memoryStorage[key];
        }
    }
};

// API utility class
class UserAPI {
    /**
     * Make an authenticated API request
     */
    async request(endpoint, options = {}) {
        const token = storage.getItem(STORAGE_KEYS.ACCESS_TOKEN);

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { Authorization: `Bearer ${token}` }),
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            // Handle network errors
            if (error instanceof TypeError) {
                throw new Error('Network error. Please check your connection.');
            }
            throw error;
        }
    }

    /**
     * Authenticate user with email and password
     */
    async login(email, password) {
        const response = await this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        // Store tokens
        if (response.access_token) {
            storage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
        }
        if (response.refresh_token) {
            storage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token);
        }

        return response;
    }

    /**
     * Register new user
     */
    async register(userData) {
        const response = await this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });

        return response;
    }

    /**
     * Get current authenticated user
     */
    async getCurrentUser() {
        return this.request('/me');
    }

    /**
     * Update user profile information
     */
    async updateProfile(profileData) {
        return this.request('/me/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });
    }

    /**
     * Update user privacy settings
     */
    async updatePrivacySettings(settings) {
        return this.request('/me/profile/privacy', {
            method: 'PATCH',
            body: JSON.stringify(settings),
        });
    }

    /**
     * Update user password
     */
    async updatePassword(currentPassword, newPassword) {
        return this.request('/me/password', {
            method: 'PATCH',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
            }),
        });
    }

    /**
     * Delete user account
     */
    async deleteAccount(password) {
        return this.request('/me', {
            method: 'DELETE',
            body: JSON.stringify({ password }),
        });
    }

    /**
     * Refresh access token
     */
    async refreshToken() {
        const refreshToken = storage.getItem(STORAGE_KEYS.REFRESH_TOKEN);

        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await this.request('/refresh', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.access_token) {
            storage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
        }

        return response;
    }

    /**
     * Logout user by clearing stored tokens
     */
    logout() {
        storage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        storage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        memoryStorage = {}; // Clear in-memory storage
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!storage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    }

    /**
     * Get stored access token
     */
    getAccessToken() {
        return storage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    }
}

// Export singleton instance
export const api = new UserAPI();

// Export class for testing
export { UserAPI };