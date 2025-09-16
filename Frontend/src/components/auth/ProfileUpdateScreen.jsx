import React, { useState } from 'react';
import { User, Camera } from 'lucide-react';
import { GENDER_OPTIONS, TIMEZONE_OPTIONS } from '../../utils/constants';

/**
 * Profile update screen component for completing user profile after registration
 */
const ProfileUpdateScreen = ({ onProfileUpdate, onSkip }) => {
    const [formData, setFormData] = useState({
        full_name: '',
        bio: '',
        date_of_birth: '',
        gender: '',
        location: '',
        timezone: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    /**
     * Handle form submission
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Filter out empty values to avoid sending unnecessary data
            const profileData = Object.entries(formData).reduce((acc, [key, value]) => {
                if (value.trim() !== '') {
                    acc[key] = value.trim();
                }
                return acc;
            }, {});

            await onProfileUpdate(profileData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Handle input field changes
     */
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));

        // Clear error when user starts typing
        if (error) {
            setError('');
        }
    };

    /**
     * Handle skip button click
     */
    const handleSkip = () => {
        onSkip();
    };

    /**
     * Get today's date in YYYY-MM-DD format for date input max value
     */
    const getTodayDate = () => {
        return new Date().toISOString().split('T')[0];
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full mx-auto mb-4 flex items-center justify-center relative">
                        <User className="w-12 h-12 text-white" />
                        <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg cursor-pointer hover:shadow-xl transition-shadow">
                            <Camera className="w-4 h-4 text-gray-600" />
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Complete Your Profile</h1>
                    <p className="text-gray-600">Tell us a bit about yourself (optional)</p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                {/* Profile Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Full Name and Date of Birth Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                                Full Name
                            </label>
                            <input
                                id="full_name"
                                type="text"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleInputChange}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                                placeholder="Enter your full name"
                                autoComplete="name"
                            />
                        </div>

                        <div>
                            <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 mb-2">
                                Date of Birth
                            </label>
                            <input
                                id="date_of_birth"
                                type="date"
                                name="date_of_birth"
                                value={formData.date_of_birth}
                                onChange={handleInputChange}
                                max={getTodayDate()}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                                autoComplete="bday"
                            />
                        </div>
                    </div>

                    {/* Bio Field */}
                    <div>
                        <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
                            Bio
                        </label>
                        <textarea
                            id="bio"
                            name="bio"
                            value={formData.bio}
                            onChange={handleInputChange}
                            rows={4}
                            maxLength={500}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition-all duration-200"
                            placeholder="Tell us about yourself..."
                        />
                        <div className="mt-1 text-right">
                            <span className="text-sm text-gray-500">
                                {formData.bio.length}/500
                            </span>
                        </div>
                    </div>

                    {/* Gender and Location Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-2">
                                Gender
                            </label>
                            <select
                                id="gender"
                                name="gender"
                                value={formData.gender}
                                onChange={handleInputChange}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                            >
                                {GENDER_OPTIONS.map((option) => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                                Location
                            </label>
                            <input
                                id="location"
                                type="text"
                                name="location"
                                value={formData.location}
                                onChange={handleInputChange}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                                placeholder="City, Country"
                                autoComplete="address-level2"
                            />
                        </div>
                    </div>

                    {/* Timezone Field */}
                    <div>
                        <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-2">
                            Timezone
                        </label>
                        <select
                            id="timezone"
                            name="timezone"
                            value={formData.timezone}
                            onChange={handleInputChange}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                        >
                            {TIMEZONE_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-4 pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 bg-gradient-to-r from-purple-500 to-pink-600 text-white py-3 px-4 rounded-lg hover:from-purple-600 hover:to-pink-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                            {loading ? (
                                <div className="flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                    Saving...
                                </div>
                            ) : (
                                'Complete Profile'
                            )}
                        </button>

                        <button
                            type="button"
                            onClick={handleSkip}
                            disabled={loading}
                            className="px-6 py-3 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Skip for now
                        </button>
                    </div>
                </form>

                {/* Help Text */}
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-500">
                        You can always update this information later in your profile settings
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ProfileUpdateScreen;