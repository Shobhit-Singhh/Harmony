import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, Lock, Settings, LogOut, Bell, Shield, Globe, Heart, Calendar, MapPin, Languages, Users, Smartphone } from 'lucide-react';

const TIMEZONE_OPTIONS = [
    { value: '', label: 'Select timezone' },
    { value: 'UTC', label: '(UTC) Coordinated Universal Time' },
    { value: 'America/New_York', label: '(EST) Eastern Time' },
    { value: 'America/Chicago', label: '(CST) Central Time' },
    { value: 'America/Denver', label: '(MST) Mountain Time' },
    { value: 'America/Los_Angeles', label: '(PST) Pacific Time' },
    { value: 'Europe/London', label: '(GMT) Greenwich Mean Time' },
    { value: 'Europe/Paris', label: '(CET) Central European Time' },
    { value: 'Asia/Tokyo', label: '(JST) Japan Standard Time' },
    { value: 'Asia/Shanghai', label: '(CST) China Standard Time' },
    { value: 'Australia/Sydney', label: '(AEST) Australian Eastern Time' },
    { value: 'Asia/Kolkata', label: '(IST) India Standard Time' },
];

const SUCCESS_MESSAGES = {
    PROFILE_UPDATED: 'Profile updated successfully!',
    PRIVACY_UPDATED: 'Privacy settings updated successfully!',
};

const SettingsScreen = ({ user, onLogout }) => {
    const [activeTab, setActiveTab] = useState('profile');
    const [profileData, setProfileData] = useState({
        full_name: '',
        date_of_birth: '',
        gender: '',
        location: '',
        timezone: '',
        crisis_contact: '',
        preferred_language: 'en',
    });
    const [healthData, setHealthData] = useState({
        primary_pillar_weights: {
            health: 0.25,
            work: 0.25,
            growth: 0.25,
            relationships: 0.25
        },
        medications: [],
        conditions: []
    });
    const [privacySettings, setPrivacySettings] = useState({
        show_profile: true,
        show_email: false,
        show_phone: false,
        show_location: true,
        show_birthday: false,
    });
    const [notificationSettings, setNotificationSettings] = useState({
        email_notifications: true,
        push_notifications: true,
        security_alerts: true,
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('success');
    const [newMedication, setNewMedication] = useState({ name: '', dosage: '', frequency: '' });
    const [newCondition, setNewCondition] = useState('');

    // Mock functions - replace with actual API calls
    const updateProfile = async (data) => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('Profile updated:', data);
    };

    const updatePrivacySettings = async (data) => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('Privacy settings updated:', data);
    };

    // Initialize form data when user prop changes
    useEffect(() => {
        if (user?.profile) {
            setProfileData({
                full_name: user.profile.full_name || '',
                date_of_birth: user.profile.date_of_birth || '',
                gender: user.profile.gender || '',
                location: user.profile.location || '',
                timezone: user.profile.timezone || '',
                crisis_contact: user.profile.crisis_contact || '',
                preferred_language: user.profile.preferred_language || 'en',
            });

            setHealthData({
                primary_pillar_weights: user.profile.primary_pillar_weights || {
                    health: 0.25,
                    work: 0.25,
                    growth: 0.25,
                    relationships: 0.25
                },
                medications: user.profile.medications || [],
                conditions: user.profile.conditions || []
            });

            setPrivacySettings({
                show_profile: user.profile.privacy_settings?.show_profile ?? true,
                show_email: user.profile.privacy_settings?.show_email ?? false,
                show_phone: user.profile.privacy_settings?.show_phone ?? false,
                show_location: user.profile.privacy_settings?.show_location ?? true,
                show_birthday: user.profile.privacy_settings?.show_birthday ?? false,
            });
        }
    }, [user]);

    const showMessage = (text, type = 'success') => {
        setMessage(text);
        setMessageType(type);
        setTimeout(() => setMessage(''), 5000);
    };

    const handleProfileUpdate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await updateProfile(profileData);
            showMessage(SUCCESS_MESSAGES.PROFILE_UPDATED, 'success');
        } catch (err) {
            showMessage('Failed to update profile: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleHealthUpdate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await updateProfile(healthData);
            showMessage('Health information updated successfully!', 'success');
        } catch (err) {
            showMessage('Failed to update health information: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handlePrivacyUpdate = async () => {
        setLoading(true);
        try {
            await updatePrivacySettings({ privacy_settings: privacySettings });
            showMessage(SUCCESS_MESSAGES.PRIVACY_UPDATED, 'success');
        } catch (err) {
            showMessage('Failed to update privacy settings: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleProfileChange = (e) => {
        const { name, value } = e.target;
        setProfileData(prev => ({ ...prev, [name]: value }));
    };

    const handlePillarWeightChange = (pillar, value) => {
        const newWeight = parseFloat(value) / 100;
        const otherPillars = Object.keys(healthData.primary_pillar_weights).filter(p => p !== pillar);
        const remainingWeight = (1 - newWeight) / otherPillars.length;
        
        const newWeights = { ...healthData.primary_pillar_weights };
        newWeights[pillar] = newWeight;
        otherPillars.forEach(p => {
            newWeights[p] = remainingWeight;
        });

        setHealthData(prev => ({
            ...prev,
            primary_pillar_weights: newWeights
        }));
    };

    const addMedication = () => {
        if (newMedication.name && newMedication.dosage) {
            setHealthData(prev => ({
                ...prev,
                medications: [...prev.medications, { ...newMedication }]
            }));
            setNewMedication({ name: '', dosage: '', frequency: '' });
        }
    };

    const removeMedication = (index) => {
        setHealthData(prev => ({
            ...prev,
            medications: prev.medications.filter((_, i) => i !== index)
        }));
    };

    const addCondition = () => {
        if (newCondition.trim()) {
            setHealthData(prev => ({
                ...prev,
                conditions: [...prev.conditions, newCondition.trim()]
            }));
            setNewCondition('');
        }
    };

    const removeCondition = (index) => {
        setHealthData(prev => ({
            ...prev,
            conditions: prev.conditions.filter((_, i) => i !== index)
        }));
    };

    const handlePrivacyToggle = (setting) => {
        setPrivacySettings(prev => ({ ...prev, [setting]: !prev[setting] }));
    };

    const handleNotificationToggle = (setting) => {
        setNotificationSettings(prev => ({ ...prev, [setting]: !prev[setting] }));
    };

    const tabs = [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'health', label: 'Health & Wellness', icon: Heart },
        { id: 'privacy', label: 'Privacy', icon: Shield },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'account', label: 'Account', icon: Settings },
    ];

    const ToggleSwitch = ({ checked, onChange, disabled = false }) => (
        <label className={`relative inline-flex items-center ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}>
            <input
                type="checkbox"
                checked={checked}
                onChange={onChange}
                disabled={disabled}
                className="sr-only peer"
            />
            <div className={`w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 ${disabled ? 'opacity-60 peer-checked:bg-gray-400' : ''}`}></div>
        </label>
    );

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-4xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                                <User className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                                <p className="text-gray-600">Manage your account preferences</p>
                            </div>
                        </div>
                        <button
                            onClick={onLogout}
                            className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                            <LogOut className="w-4 h-4" />
                            Logout
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="grid grid-cols-12 gap-8">
                    <div className="col-span-12 md:col-span-3">
                        <nav className="space-y-2">
                            {tabs.map((tab) => {
                                const Icon = tab.icon;
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${activeTab === tab.id
                                                ? 'bg-blue-50 text-blue-600 border border-blue-200'
                                                : 'text-gray-700 hover:bg-gray-100'
                                            }`}
                                    >
                                        <Icon className="w-5 h-5" />
                                        {tab.label}
                                    </button>
                                );
                            })}
                        </nav>
                    </div>

                    <div className="col-span-12 md:col-span-9">
                        <div className="bg-white rounded-xl shadow-sm border p-6">
                            {message && (
                                <div className={`mb-6 px-4 py-3 rounded-lg ${messageType === 'success'
                                        ? 'bg-green-50 border border-green-200 text-green-700'
                                        : 'bg-red-50 border border-red-200 text-red-700'
                                    }`}>
                                    {message}
                                </div>
                            )}

                            {activeTab === 'profile' && (
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Information</h2>
                                    <form onSubmit={handleProfileUpdate} className="space-y-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                                                    Full Name
                                                </label>
                                                <input
                                                    id="full_name"
                                                    type="text"
                                                    name="full_name"
                                                    value={profileData.full_name}
                                                    onChange={handleProfileChange}
                                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="Enter your full name"
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
                                                    value={profileData.date_of_birth}
                                                    onChange={handleProfileChange}
                                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                />
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-2">
                                                    Gender
                                                </label>
                                                <select
                                                    id="gender"
                                                    name="gender"
                                                    value={profileData.gender}
                                                    onChange={handleProfileChange}
                                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                >
                                                    <option value="">Select gender</option>
                                                    <option value="male">Male</option>
                                                    <option value="female">Female</option>
                                                    <option value="non-binary">Non-binary</option>
                                                    <option value="prefer-not-to-say">Prefer not to say</option>
                                                    <option value="other">Other</option>
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
                                                    value={profileData.location}
                                                    onChange={handleProfileChange}
                                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="City, Country"
                                                />
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-2">
                                                    Timezone
                                                </label>
                                                <select
                                                    id="timezone"
                                                    name="timezone"
                                                    value={profileData.timezone}
                                                    onChange={handleProfileChange}
                                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                >
                                                    {TIMEZONE_OPTIONS.map((option) => (
                                                        <option key={option.value} value={option.value}>
                                                            {option.label}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>

                                            <div>
                                                <label htmlFor="preferred_language" className="block text-sm font-medium text-gray-700 mb-2">
                                                    Preferred Language
                                                </label>
                                                <select
                                                    id="preferred_language"
                                                    name="preferred_language"
                                                    value={profileData.preferred_language}
                                                    onChange={handleProfileChange}
                                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                >
                                                    <option value="en">English</option>
                                                    <option value="es">Spanish</option>
                                                    <option value="fr">French</option>
                                                    <option value="de">German</option>
                                                    <option value="it">Italian</option>
                                                    <option value="pt">Portuguese</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div>
                                            <label htmlFor="crisis_contact" className="block text-sm font-medium text-gray-700 mb-2">
                                                Crisis Contact
                                            </label>
                                            <input
                                                id="crisis_contact"
                                                type="text"
                                                name="crisis_contact"
                                                value={profileData.crisis_contact}
                                                onChange={handleProfileChange}
                                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="Emergency contact information"
                                            />
                                        </div>

                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 font-medium"
                                        >
                                            {loading ? 'Saving...' : 'Save Changes'}
                                        </button>
                                    </form>
                                </div>
                            )}

                            {activeTab === 'health' && (
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900 mb-6">Health & Wellness</h2>
                                    <form onSubmit={handleHealthUpdate} className="space-y-8">
                                        <div>
                                            <h3 className="text-lg font-medium text-gray-900 mb-4">Life Pillar Priorities</h3>
                                            <div className="space-y-4">
                                                {Object.entries(healthData.primary_pillar_weights).map(([pillar, weight]) => (
                                                    <div key={pillar} className="flex items-center justify-between">
                                                        <label className="text-sm font-medium text-gray-700 capitalize">
                                                            {pillar}
                                                        </label>
                                                        <div className="flex items-center gap-4 w-64">
                                                            <input
                                                                type="range"
                                                                min="0"
                                                                max="100"
                                                                value={weight * 100}
                                                                onChange={(e) => handlePillarWeightChange(pillar, e.target.value)}
                                                                className="flex-1"
                                                            />
                                                            <span className="text-sm text-gray-600 w-12 text-right">
                                                                {Math.round(weight * 100)}%
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div>
                                            <h3 className="text-lg font-medium text-gray-900 mb-4">Medications</h3>
                                            <div className="space-y-4">
                                                {healthData.medications.map((med, index) => (
                                                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                                        <div>
                                                            <span className="font-medium text-gray-900">{med.name}</span>
                                                            <span className="text-gray-600 ml-2">{med.dosage}</span>
                                                            {med.frequency && <span className="text-gray-600 ml-2">({med.frequency})</span>}
                                                        </div>
                                                        <button
                                                            type="button"
                                                            onClick={() => removeMedication(index)}
                                                            className="text-red-600 hover:text-red-800"
                                                        >
                                                            Remove
                                                        </button>
                                                    </div>
                                                ))}
                                                
                                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border border-gray-200 rounded-lg">
                                                    <input
                                                        type="text"
                                                        placeholder="Medication name"
                                                        value={newMedication.name}
                                                        onChange={(e) => setNewMedication({...newMedication, name: e.target.value})}
                                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    />
                                                    <input
                                                        type="text"
                                                        placeholder="Dosage"
                                                        value={newMedication.dosage}
                                                        onChange={(e) => setNewMedication({...newMedication, dosage: e.target.value})}
                                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    />
                                                    <input
                                                        type="text"
                                                        placeholder="Frequency"
                                                        value={newMedication.frequency}
                                                        onChange={(e) => setNewMedication({...newMedication, frequency: e.target.value})}
                                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    />
                                                    <button
                                                        type="button"
                                                        onClick={addMedication}
                                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                                    >
                                                        Add
                                                    </button>
                                                </div>
                                            </div>
                                        </div>

                                        <div>
                                            <h3 className="text-lg font-medium text-gray-900 mb-4">Health Conditions</h3>
                                            <div className="space-y-4">
                                                <div className="flex flex-wrap gap-2">
                                                    {healthData.conditions.map((condition, index) => (
                                                        <div key={index} className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                                                            <span>{condition}</span>
                                                            <button
                                                                type="button"
                                                                onClick={() => removeCondition(index)}
                                                                className="text-blue-600 hover:text-blue-800"
                                                            >
                                                                ×
                                                            </button>
                                                        </div>
                                                    ))}
                                                </div>
                                                
                                                <div className="flex gap-2">
                                                    <input
                                                        type="text"
                                                        placeholder="Add health condition"
                                                        value={newCondition}
                                                        onChange={(e) => setNewCondition(e.target.value)}
                                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCondition())}
                                                    />
                                                    <button
                                                        type="button"
                                                        onClick={addCondition}
                                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                                    >
                                                        Add
                                                    </button>
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 font-medium"
                                        >
                                            {loading ? 'Saving...' : 'Save Health Information'}
                                        </button>
                                    </form>
                                </div>
                            )}

                            {activeTab === 'privacy' && (
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900 mb-6">Privacy Settings</h2>
                                    <div className="space-y-6">
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between py-3">
                                                <div>
                                                    <h3 className="font-medium text-gray-900">Show Profile</h3>
                                                    <p className="text-sm text-gray-600">Make your profile visible to others</p>
                                                </div>
                                                <ToggleSwitch
                                                    checked={privacySettings.show_profile}
                                                    onChange={() => handlePrivacyToggle('show_profile')}
                                                />
                                            </div>

                                            <div className="flex items-center justify-between py-3 border-t">
                                                <div>
                                                    <h3 className="font-medium text-gray-900">Show Email</h3>
                                                    <p className="text-sm text-gray-600">Display your email address on profile</p>
                                                </div>
                                                <ToggleSwitch
                                                    checked={privacySettings.show_email}
                                                    onChange={() => handlePrivacyToggle('show_email')}
                                                />
                                            </div>

                                            <div className="flex items-center justify-between py-3 border-t">
                                                <div>
                                                    <h3 className="font-medium text-gray-900">Show Phone</h3>
                                                    <p className="text-sm text-gray-600">Display your phone number on profile</p>
                                                </div>
                                                <ToggleSwitch
                                                    checked={privacySettings.show_phone}
                                                    onChange={() => handlePrivacyToggle('show_phone')}
                                                />
                                            </div>

                                            <div className="flex items-center justify-between py-3 border-t">
                                                <div>
                                                    <h3 className="font-medium text-gray-900">Show Location</h3>
                                                    <p className="text-sm text-gray-600">Display your location on profile</p>
                                                </div>
                                                <ToggleSwitch
                                                    checked={privacySettings.show_location}
                                                    onChange={() => handlePrivacyToggle('show_location')}
                                                />
                                            </div>

                                            <div className="flex items-center justify-between py-3 border-t">
                                                <div>
                                                    <h3 className="font-medium text-gray-900">Show Birthday</h3>
                                                    <p className="text-sm text-gray-600">Display your birth date on profile</p>
                                                </div>
                                                <ToggleSwitch
                                                    checked={privacySettings.show_birthday}
                                                    onChange={() => handlePrivacyToggle('show_birthday')}
                                                />
                                            </div>
                                        </div>

                                        <button
                                            onClick={handlePrivacyUpdate}
                                            disabled={loading}
                                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 font-medium"
                                        >
                                            {loading ? 'Saving...' : 'Update Privacy Settings'}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'notifications' && (
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Preferences</h2>
                                    <div className="space-y-6">
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between py-3">
                                                <div className="flex items-center gap-3">
                                                    <Mail className="w-5 h-5 text-gray-400" />
                                                    <div>
                                                        <h3 className="font-medium text-gray-900">Email Notifications</h3>
                                                        <p className="text-sm text-gray-600">Receive notifications via email</p>
                                                    </div>
                                                </div>
                                                <ToggleSwitch
                                                    checked={notificationSettings.email_notifications}
                                                    onChange={() => handleNotificationToggle('email_notifications')}
                                                />
                                            </div>

                                            <div className="flex items-center justify-between py-3 border-t">
                                                <div className="flex items-center gap-3">
                                                    <Smartphone className="w-5 h-5 text-gray-400" />
                                                    <div>
                                                        <h3 className="font-medium text-gray-900">Push Notifications</h3>
                                                        <p className="text-sm text-gray-600">Receive push notifications on your device</p>
                                                    </div>
                                                </div>
                                                <ToggleSwitch
                                                    checked={notificationSettings.push_notifications}
                                                    onChange={() => handleNotificationToggle('push_notifications')}
                                                />
                                            </div>

                                            <div className="flex items-center justify-between py-3 border-t">
                                                <div className="flex items-center gap-3">
                                                    <Bell className="w-5 h-5 text-gray-400" />
                                                    <div>
                                                        <h3 className="font-medium text-gray-900">Security Alerts</h3>
                                                        <p className="text-sm text-gray-600">Important security notifications</p>
                                                    </div>
                                                </div>
                                                <ToggleSwitch
                                                    checked={notificationSettings.security_alerts}
                                                    onChange={() => handleNotificationToggle('security_alerts')}
                                                    disabled={true}
                                                />
                                            </div>
                                        </div>

                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                            <div className="flex items-start gap-3">
                                                <Bell className="w-5 h-5 text-blue-600 mt-0.5" />
                                                <div>
                                                    <h4 className="font-medium text-blue-900">Security notifications are always enabled</h4>
                                                    <p className="text-sm text-blue-700 mt-1">These notifications help protect your account and cannot be disabled.</p>
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => showMessage('Notification preferences saved!', 'success')}
                                            disabled={loading}
                                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 font-medium"
                                        >
                                            Save Notification Settings
                                        </button>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'account' && (
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900 mb-6">Account Settings</h2>
                                    <div className="space-y-6">
                                        <div className="border rounded-lg p-4">
                                            <h3 className="font-medium text-gray-900 mb-3">Account Information</h3>
                                            <div className="space-y-3">
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm text-gray-600">Email</span>
                                                    <span className="text-sm font-medium text-gray-900">{user?.email || 'N/A'}</span>
                                                </div>
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm text-gray-600">Username</span>
                                                    <span className="text-sm font-medium text-gray-900">{user?.username || 'N/A'}</span>
                                                </div>
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm text-gray-600">Member Since</span>
                                                    <span className="text-sm font-medium text-gray-900">
                                                        {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="border rounded-lg p-4">
                                            <h3 className="font-medium text-gray-900 mb-3">Security</h3>
                                            <div className="space-y-3">
                                                <button
                                                    onClick={() => showMessage('Password change feature coming soon!', 'success')}
                                                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                                                >
                                                    <div className="flex items-center justify-between">
                                                        <div>
                                                            <h4 className="font-medium text-gray-900">Change Password</h4>
                                                            <p className="text-sm text-gray-600">Update your account password</p>
                                                        </div>
                                                        <Lock className="w-5 h-5 text-gray-400" />
                                                    </div>
                                                </button>

                                                <button
                                                    onClick={() => showMessage('Two-factor authentication setup coming soon!', 'success')}
                                                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                                                >
                                                    <div className="flex items-center justify-between">
                                                        <div>
                                                            <h4 className="font-medium text-gray-900">Two-Factor Authentication</h4>
                                                            <p className="text-sm text-gray-600">Add an extra layer of security</p>
                                                        </div>
                                                        <Shield className="w-5 h-5 text-gray-400" />
                                                    </div>
                                                </button>
                                            </div>
                                        </div>

                                        <div className="border rounded-lg p-4">
                                            <h3 className="font-medium text-gray-900 mb-3">Data Management</h3>
                                            <div className="space-y-3">
                                                <button
                                                    onClick={() => showMessage('Data export feature coming soon!', 'success')}
                                                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                                                >
                                                    <div className="flex items-center justify-between">
                                                        <div>
                                                            <h4 className="font-medium text-gray-900">Export My Data</h4>
                                                            <p className="text-sm text-gray-600">Download a copy of your account data</p>
                                                        </div>
                                                        <Globe className="w-5 h-5 text-gray-400" />
                                                    </div>
                                                </button>
                                            </div>
                                        </div>

                                        <div className="border border-red-200 rounded-lg p-4">
                                            <h3 className="font-medium text-red-900 mb-3">Danger Zone</h3>
                                            <div className="space-y-3">
                                                <button
                                                    onClick={() => showMessage('Account deletion requires additional verification', 'error')}
                                                    className="w-full text-left px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                                                >
                                                    <div>
                                                        <h4 className="font-medium text-red-900">Delete Account</h4>
                                                        <p className="text-sm text-red-600">Permanently delete your account and all data</p>
                                                    </div>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsScreen;