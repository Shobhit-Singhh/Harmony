import { useState, useEffect } from 'react';
import { api } from '../api/userApi';

/**
 * Custom hook for managing authentication state
 */
export const useAuth = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    /**
     * Check authentication status on hook initialization
     */
    useEffect(() => {
        checkAuthStatus();
    }, []);

    /**
     * Verify if user is authenticated and fetch user data
     */
    const checkAuthStatus = async () => {
        setLoading(true);
        setError(null);

        try {
            if (api.isAuthenticated()) {
                const userData = await api.getCurrentUser();
                setUser(userData);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            // Clear invalid tokens
            api.logout();
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Login user with credentials
     */
    const login = async (email, password) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.login(email, password);
            setUser(response.user);
            return response;
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Register new user
     */
    const register = async (userData) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.register(userData);
            setUser(response.user);
            return response;
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Update user profile
     */
    const updateProfile = async (profileData) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.updateProfile(profileData);
            // Update user state with new profile data
            setUser(prevUser => ({
                ...prevUser,
                profile: { ...prevUser?.profile, ...response }
            }));
            return response;
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Update privacy settings
     */
    const updatePrivacySettings = async (settings) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.updatePrivacySettings(settings);
            // Update user state with new privacy settings
            setUser(prevUser => ({
                ...prevUser,
                profile: {
                    ...prevUser?.profile,
                    privacy_settings: { ...prevUser?.profile?.privacy_settings, ...response }
                }
            }));
            return response;
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Update user password
     */
    const updatePassword = async (currentPassword, newPassword) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.updatePassword(currentPassword, newPassword);
            return response;
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Delete user account
     */
    const deleteAccount = async (password) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.deleteAccount(password);
            setUser(null);
            return response;
        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Logout user
     */
    const logout = () => {
        api.logout();
        setUser(null);
        setError(null);
    };

    /**
     * Refresh authentication status
     */
    const refresh = async () => {
        try {
            await api.refreshToken();
            await checkAuthStatus();
        } catch (error) {
            console.error('Token refresh failed:', error);
            logout();
            throw error;
        }
    };

    /**
     * Clear error state
     */
    const clearError = () => {
        setError(null);
    };

    return {
        // State
        user,
        loading,
        error,
        isAuthenticated: !!user,

        // Actions
        login,
        register,
        logout,
        updateProfile,
        updatePrivacySettings,
        updatePassword,
        deleteAccount,
        checkAuthStatus,
        refresh,
        clearError,
    };
};