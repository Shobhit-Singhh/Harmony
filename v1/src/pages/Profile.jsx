import React, { useState } from "react";
import { User, Brain, Settings, Zap, CreditCard, Trash2, LogIn, ChevronRight, MessageSquare, BarChart3, Clock, Heart, Bot, ThumbsUp, Mail, Shield, Palette, Languages } from "lucide-react";

// Main component
const ProfileDashboard = () => {
    const [activeTab, setActiveTab] = useState("Profile");
    const tabs = ["Profile", "Psyche", "Settings"];

    // Profile menu items - using uniform structure
    const profileItems = [
        { title: 'Personal Information', icon: <User size={18} />, description: 'Update your profile details' },
        { title: 'Location & Timezone', icon: <Zap size={18} />, description: 'Set your location and time preferences' },
        { title: 'Login Credentials', icon: <LogIn size={18} />, description: 'Change your password and email' },
        { title: 'Notification Preferences', icon: <Mail size={18} />, description: 'Manage your notification settings' },
    ];

    // Psyche menu items - matching structure with profile items
    const psycheItems = [
        { title: 'Mental Health Assessment', icon: <Brain size={18} />, description: 'Your psychological evaluations' },
        { title: 'Therapy Sessions', icon: <MessageSquare size={18} />, description: 'Schedule and review sessions' },
        { title: 'Mood Journal', icon: <Heart size={18} />, description: 'Track your emotional patterns' },
        { title: 'Resources', icon: <Zap size={18} />, description: 'Helpful materials and exercises' },
        { title: 'Chat History', icon: <MessageSquare size={18} />, description: 'View your recent conversations' },
        { title: 'Response Preferences', icon: <ThumbsUp size={18} />, description: 'Customize how the chatbot responds to you' },
        { title: 'Knowledge Graph', icon: <BarChart3 size={18} />, description: 'Explore your knowledge graph' },
        { title: 'Interaction Patterns', icon: <BarChart3 size={18} />, description: 'Your conversation style analysis' },
    ];

    // Connected services - different style from menu items
    const connectedServices = [
        { name: "Google Account", status: "Connected", icon: "G" },
        { name: "Health App", status: "Connected", icon: "H" },
        { name: "Calendar", status: "Not Connected", icon: "C" },
        { name: "Chatbot API", status: "Connected", icon: "B" }
    ];

    // Preference items - different style from menu items
    const preferenceItems = [
        { name: "Notification Settings", desc: "Manage how and when you receive alerts", icon: <Mail size={18} /> },
        { name: "Privacy Settings", desc: "Control your data sharing preferences", icon: <Shield size={18} /> },
        { name: "Theme Settings", desc: "Customize the app appearance", icon: <Palette size={18} /> },
        { name: "Language Settings", desc: "Change your preferred language", icon: <Languages size={18} /> }
    ];

    return (
        <DashboardLayout>
            <ProfileCard
                name="John Doe"
                age={25}
                gender="Male"
                email="xyz@gmail.com"
                imgSrc="../../public/assets/profile/dp.avif"
                tabs={tabs}
                activeTab={activeTab}
                onTabChange={setActiveTab}
            />

            {/* Content Based on Active Tab */}
            {activeTab === "Profile" && (
                <>
                    <MenuSection
                        title="Chatbot Interaction Profile"
                        icon={<Bot size={20} />}
                        items={profileItems}
                        description="Your behavioral patterns and preferences when interacting with our AI assistant"
                    />
                    <ConnectedServicesCard
                        services={connectedServices}
                    />
                </>
            )}

            {activeTab === "Psyche" && (
                <>
                    <MenuSection
                        title="Mental Health & Wellness"
                        icon={<Brain size={20} />}
                        items={psycheItems}
                        description="Tools and resources to support your mental wellbeing"
                    />
                    {/* Chat Analytics Dashboard Preview */}
                    <div className="bg-white rounded-lg shadow-xl p-4 md:p-8 mb-6 md:mb-8">
                        <SectionHeader
                            title="Interaction Analytics"
                            icon={<BarChart3 size={20} />}
                            description="Insights based on your chat patterns"
                        />
                        <div className="bg-neutral-50 p-4 rounded-lg">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <AnalyticsCard
                                    title="53"
                                    subtitle="Total Conversations"
                                    icon={<MessageSquare size={20} className="text-primary" />}
                                />
                                <AnalyticsCard
                                    title="23 min"
                                    subtitle="Average Duration"
                                    icon={<Clock size={20} className="text-primary" />}
                                />
                                <AnalyticsCard
                                    title="78%"
                                    subtitle="Positive Sentiment"
                                    icon={<ThumbsUp size={20} className="text-primary" />}
                                />
                            </div>
                        </div>
                    </div>
                </>
            )}

            {activeTab === "Settings" && (
                <>
                    <PreferencesCard items={preferenceItems} />
                    <SubscriptionCard
                        plan="Premium Plan"
                        nextBilling="March 25, 2025"
                        status="Active"
                    />
                    <AccountDeletionCard />
                </>
            )}
        </DashboardLayout>
    );
};

// Analytics Card Component
const AnalyticsCard = ({ title, subtitle, icon }) => (
    <div className="bg-white p-4 rounded-lg shadow flex items-center space-x-4">
        <div className="p-2 bg-primary-light/20 rounded-full">
            {icon}
        </div>
        <div>
            <h4 className="text-xl font-bold text-dark">{title}</h4>
            <p className="text-sm text-neutral-500">{subtitle}</p>
        </div>
    </div>
);

// Layout component
const DashboardLayout = ({ children }) => (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-accent-blue-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
        </div>
    </div>
);

// Profile Card Component
const ProfileCard = ({ name, age, gender, email, imgSrc, tabs, activeTab, onTabChange }) => (
    <div className="bg-white rounded-lg shadow-xl p-4 md:p-8 mb-6 md:mb-8 mt-8">
        <div className="flex flex-col md:flex-row items-center gap-4 md:gap-6 mb-6">
            <div className="w-24 h-24 md:w-32 md:h-40 overflow-hidden rounded-full md:rounded-2xl shadow-md">
                <img src={imgSrc} alt="Profile" className="w-full h-full object-cover" />
            </div>
            <div className="text-center md:text-left">
                <h1 className="text-2xl md:text-3xl font-bold text-primary">{name}</h1>
                <h2 className="text-lg md:text-xl font-semibold text-neutral-600">{gender}, {age}</h2>
                <h3 className="text-sm md:text-md text-neutral-500">Email: {email}</h3>
            </div>
        </div>
        <TabBar tabs={tabs} activeTab={activeTab} onTabChange={onTabChange} />
    </div>
);

// Tab Bar Component
const TabBar = ({ tabs, activeTab, onTabChange }) => (
    <div className="flex justify-between bg-neutral-100 rounded-full p-2 gap-4">
        {tabs.map((tab) => (
            <button
                key={tab}
                className={`flex-1 px-4 py-2 rounded-full transition-colors ${activeTab === tab
                    ? "bg-primary text-white"
                    : "bg-neutral-200 hover:bg-primary hover:text-white"
                    }`}
                onClick={() => onTabChange(tab)}
            >
                {tab}
            </button>
        ))}
    </div>
);

// Section Header Component
const SectionHeader = ({ title, icon, description }) => (
    <div className="mb-4 md:mb-6">
        <div className="flex items-center">
            <div className="w-10 h-10 bg-primary-light/20 rounded-full flex items-center justify-center mr-4">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-dark">{title}</h3>
        </div>
        {description && (
            <p className="text-neutral-500 mt-2 ml-14">{description}</p>
        )}
    </div>
);

// Menu Section Component (for uniform menu sections)
const MenuSection = ({ title, icon, items, description }) => (
    <div className="bg-white rounded-lg shadow-xl p-4 md:p-8 mb-6 md:mb-8">
        <SectionHeader title={title} icon={icon} description={description} />
        <div className="mt-4 space-y-3">
            {items.map((item, index) => (
                <MenuItemCard key={index} item={item} />
            ))}
        </div>
    </div>
);

// Menu Item Card Component (unified style for menu items)
const MenuItemCard = ({ item }) => (
    <div className="bg-neutral-50 rounded-lg p-4 hover:bg-neutral-100 transition-all flex justify-between items-center cursor-pointer">
        <div className="flex items-center">
            <div className="w-8 h-8 bg-primary-light/20 rounded-full flex items-center justify-center mr-3">
                {item.icon}
            </div>
            <div>
                <h4 className="font-medium text-dark">{item.title}</h4>
                <p className="text-sm text-neutral-500">{item.description}</p>
            </div>
        </div>
        <ChevronRight size={18} className="text-neutral-400" />
    </div>
);

// Connected Services Card
const ConnectedServicesCard = ({ services }) => (
    <div className="my-6 md:my-8 bg-white rounded-lg shadow-xl">
        <div className="p-4 md:p-8">
            <div className="flex items-center justify-between mb-4 md:mb-8">
                <SectionHeader title="Connected Services" icon={<LogIn size={20} />} />
                <button className="px-4 py-2 bg-neutral-100 text-neutral-600 rounded-lg hover:bg-primary hover:text-white transition-colors">
                    Add Service
                </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {services.map((service, index) => (
                    <ServiceCard key={index} service={service} />
                ))}
            </div>
        </div>
    </div>
);

// Service Card Component
const ServiceCard = ({ service }) => (
    <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors">
        <div className="flex items-center">
            <div className="w-10 h-10 bg-accent-blue-light rounded-lg flex items-center justify-center mr-4">
                <span className="text-primary font-bold">{service.icon}</span>
            </div>
            <div>
                <p className="text-sm md:text-base font-medium text-dark">{service.name}</p>
                <p className="text-xs md:text-sm text-neutral-500">{service.status}</p>
            </div>
        </div>
        <div>
            <button className="px-3 py-1 md:px-4 md:py-2 bg-accent-blue-light text-primary rounded-lg hover:bg-accent-blue-light/80 transition-colors text-sm">
                {service.status === "Connected" ? "Disconnect" : "Connect"}
            </button>
        </div>
    </div>
);

// Preferences Card
const PreferencesCard = ({ items }) => (
    <div className="bg-white rounded-lg shadow-xl p-4 md:p-8 mb-6 md:mb-8">
        <SectionHeader title="Preferences" icon={<Settings size={20} />} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {items.map((pref, index) => (
                <PreferenceItem key={index} item={pref} />
            ))}
        </div>
    </div>
);

// Preference Item Component
const PreferenceItem = ({ item }) => (
    <div className="p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors cursor-pointer">
        <div className="flex justify-between items-center">
            <div className="flex items-center">
                <div className="w-8 h-8 bg-secondary-light/20 rounded-full flex items-center justify-center mr-3">
                    {item.icon}
                </div>
                <div>
                    <p className="font-medium text-dark">{item.name}</p>
                    <p className="text-sm text-neutral-500">{item.desc}</p>
                </div>
            </div>
            <ChevronRight size={18} className="text-neutral-400" />
        </div>
    </div>
);

// Subscription Card Component
const SubscriptionCard = ({ plan, nextBilling, status }) => (
    <div className="mb-6 md:mb-8 bg-white rounded-lg shadow-xl">
        <div className="p-4 md:p-8">
            <SectionHeader title="Subscription" icon={<CreditCard size={20} />} />
            <div className="bg-secondary-light/10 p-4 md:p-6 rounded-lg border border-secondary-light">
                <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 gap-2">
                    <div>
                        <h4 className="text-lg font-bold text-dark">{plan}</h4>
                        <p className="text-neutral-600">Next billing: {nextBilling}</p>
                    </div>
                    <span className="px-3 py-1 bg-secondary-light text-secondary rounded-full text-sm font-medium w-fit">{status}</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 sm:justify-between">
                    <button className="px-6 py-2 bg-white text-neutral-600 rounded-lg hover:bg-neutral-100 transition-colors">
                        View Details
                    </button>
                    <button className="px-6 py-2 bg-secondary text-white rounded-lg hover:bg-secondary-dark transition-colors">
                        Manage Subscription
                    </button>
                </div>
            </div>
        </div>
    </div>
);

// Account Deletion Card Component
const AccountDeletionCard = () => (
    <div className="bg-white rounded-lg shadow-xl">
        <div className="p-4 md:p-8">
            <SectionHeader title="Account Deletion" icon={<Trash2 size={20} />} />
            <p className="text-neutral-600 mb-4">
                If you wish to delete your account, please note that this action is irreversible.
            </p>
            <button className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">
                Delete Account
            </button>
        </div>
    </div>
);

export default ProfileDashboard;