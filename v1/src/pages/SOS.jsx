import React from "react";

const CalmSupport = () => {
    return (
        <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-accent-blue-light">
            {/* Hero Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="text-center mb-16">
                    <h2 className="text-display-lg font-display text-dark mb-6">
                        24/7 Crisis Support
                    </h2>
                    <p className="text-body-lg text-neutral-600 max-w-3xl mx-auto">
                        Immediate access to professional support and emergency resources when you need them most. You're not alone.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Emergency Support Card */}
                    <div className="bg-white rounded-lg shadow-xl p-8">
                        <div className="flex items-center mb-6">
                            <div className="w-12 h-12 bg-secondary-light/20 rounded-full flex items-center justify-center">
                                <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                </svg>
                            </div>
                            <h3 className="text-h3 font-display text-dark ml-4">Emergency Support</h3>
                        </div>
                        <div className="space-y-4">
                            <button className="w-full py-4 bg-secondary text-white rounded-lg hover:bg-secondary-dark transition-colors flex items-center justify-center space-x-3">
                                <span className="text-body-lg font-medium">Call Emergency Services</span>
                            </button>
                            <button className="w-full py-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors">
                                <span className="text-body-lg font-medium">Contact Crisis Hotline</span>
                            </button>
                        </div>
                    </div>

                    {/* Quick Tools Card */}
                    <div className="bg-white rounded-lg shadow-xl p-8">
                        <div className="flex items-center mb-6">
                            <div className="w-12 h-12 bg-primary-light/20 rounded-full flex items-center justify-center">
                                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <h3 className="text-h3 font-display text-dark ml-4">Quick Support Tools</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            {[
                                "Breathing Exercise",
                                "Grounding Technique",
                                "Guided Meditation",
                                "Calming Sounds"
                            ].map((tool, index) => (
                                <button
                                    key={index}
                                    className="p-4 bg-accent-blue-light rounded-lg hover:bg-accent-blue-light/80 transition-colors group"
                                >
                                    <p className="font-medium text-primary group-hover:text-primary-dark">{tool}</p>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Trusted Contacts Section */}
                <div className="mt-12 bg-white rounded-lg shadow-xl">
                    <div className="p-8">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-h3 font-display text-dark">Trusted Contacts</h3>
                            <button className="px-6 py-2 bg-neutral-100 text-neutral-600 rounded-lg hover:bg-neutral-200 transition-colors">
                                Add Contact
                            </button>
                        </div>
                        <div className="space-y-4">
                            {["Dr. Sarah Johnson", "Emergency Contact: Michael", "Crisis Counselor"].map((contact, index) => (
                                <div key={index} className="flex items-center justify-between p-6 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors">
                                    <div>
                                        <p className="text-body font-medium text-dark">{contact}</p>
                                        <p className="text-small text-neutral-500">Available 24/7</p>
                                    </div>
                                    <div className="flex space-x-3">
                                        <button className="p-3 bg-accent-blue-light text-primary rounded-lg hover:bg-accent-blue-light/80 transition-colors">
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                            </svg>
                                        </button>
                                        <button className="p-3 bg-accent-blue-light text-primary rounded-lg hover:bg-accent-blue-light/80 transition-colors">
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CalmSupport;