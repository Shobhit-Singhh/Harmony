import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';
import LoginScreen from './components/auth/LoginScreen';
import RegistrationScreen from './components/auth/RegistrationScreen';
import ProfileUpdateScreen from './components/auth/ProfileUpdateScreen';
import SettingsScreen from './pages/SettingsScreen';

/**
 * Main application component handling screen navigation and authentication flow
 */
const App = () => {
  const [currentScreen, setCurrentScreen] = useState('login');
  
  const {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
    clearError,
  } = useAuth();

  /**
   * Handle successful login
   */
  const handleLogin = async (email, password) => {
    try {
      await login(email, password);
      setCurrentScreen('settings');
    } catch (error) {
      // Error is handled by the hook and LoginScreen
      throw error;
    }
  };

  /**
   * Handle successful registration
   */
  const handleRegister = async (userData) => {
    try {
      await register(userData);
      setCurrentScreen('profile-update');
    } catch (error) {
      // Error is handled by the hook and RegistrationScreen
      throw error;
    }
  };

  /**
   * Handle profile update completion
   */
  const handleProfileUpdate = async (profileData) => {
    try {
      await updateProfile(profileData);
      setCurrentScreen('settings');
    } catch (error) {
      // Error is handled by the hook and ProfileUpdateScreen
      throw error;
    }
  };

  /**
   * Handle skip profile update
   */
  const handleSkipProfile = () => {
    setCurrentScreen('settings');
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    setCurrentScreen('login');
    clearError();
  };

  /**
   * Navigate to registration from login
   */
  const handleNavigateToRegister = () => {
    clearError();
    setCurrentScreen('register');
  };

  /**
   * Navigate to login from registration
   */
  const handleNavigateToLogin = () => {
    clearError();
    setCurrentScreen('login');
  };

  // Show loading spinner while checking authentication
  if (loading && !user && currentScreen === 'login') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Auto-navigate to settings if user is already authenticated
  if (isAuthenticated && currentScreen === 'login') {
    setCurrentScreen('settings');
  }

  return (
    <div className="app">
      {/* Login Screen */}
      {currentScreen === 'login' && (
        <LoginScreen 
          onLogin={handleLogin}
          onNavigateToRegister={handleNavigateToRegister}
        />
      )}

      {/* Registration Screen */}
      {currentScreen === 'register' && (
        <RegistrationScreen 
          onRegister={handleRegister}
          onNavigateToLogin={handleNavigateToLogin}
        />
      )}

      {/* Profile Update Screen */}
      {currentScreen === 'profile-update' && (
        <ProfileUpdateScreen 
          onProfileUpdate={handleProfileUpdate}
          onSkip={handleSkipProfile}
        />
      )}

      {/* Settings Screen */}
      {currentScreen === 'settings' && isAuthenticated && (
        <SettingsScreen 
          user={user}
          onLogout={handleLogout}
        />
      )}

      {/* Error Boundary Fallback */}
      {error && currentScreen === 'login' && (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-red-600 mb-4">Application Error</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={clearError}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;