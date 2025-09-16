// API Configuration
export const API_BASE_URL = "http://localhost:8000/api/v1/users";

// Gender Options
export const GENDER_OPTIONS = [
    { value: '', label: 'Select gender' },
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
    { value: 'other', label: 'Other' },
    { value: 'prefer_not_to_say', label: 'Prefer not to say' }
];

// Timezone Options
export const TIMEZONE_OPTIONS = [
    { value: '', label: 'Select timezone' },
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'Eastern Time' },
    { value: 'America/Chicago', label: 'Central Time' },
    { value: 'America/Denver', label: 'Mountain Time' },
    { value: 'America/Los_Angeles', label: 'Pacific Time' },
    { value: 'Europe/London', label: 'London' },
    { value: 'Europe/Paris', label: 'Paris' },
    { value: 'Asia/Tokyo', label: 'Tokyo' },
    { value: 'Asia/Kolkata', label: 'India' }
];

// Form Validation
export const PASSWORD_MIN_LENGTH = 8;

// Error Messages
export const ERROR_MESSAGES = {
    PASSWORDS_NO_MATCH: 'Passwords do not match',
    PASSWORD_TOO_SHORT: `Password must be at least ${PASSWORD_MIN_LENGTH} characters long`,
    REQUEST_FAILED: 'Request failed'
};

// Success Messages
export const SUCCESS_MESSAGES = {
    PROFILE_UPDATED: 'Profile updated successfully!',
    PRIVACY_UPDATED: 'Privacy settings updated successfully!'
};

// Storage Keys (for localStorage)
export const STORAGE_KEYS = {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token'
};