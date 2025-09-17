import React, { useState } from "react";
import { useNavigate } from "react-router-dom";


const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();

    const toggleNav = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    return (
        <>
            {/* Desktop Navigation (Large screens) */}
            <nav className="hidden sm:flex items-center justify-center bg-white shadow-md py-4">
                <div className="max-w-7xl w-full flex justify-between items-center px-4 sm:px-6 lg:px-8">
                    {/* Logo Section */}
                    <div className="flex items-center space-x-2">
                        <img src="/assets/logo_dark.png" alt="logo" className="w-8 h-8" />
                        <h1 className="text-h3 font-display text-primary">Neoptio</h1>
                    </div>

                    {/* Navigation Tabs */}
                    <ul className="flex space-x-6 text-sm font-medium text-gray-700">
                        <li><button onClick={() => navigate("/")} className="hover:text-secondary">Home</button></li>
                        <li><button onClick={() => navigate("/recommendation")} className="hover:text-secondary">Recommendation</button></li>
                        <li><button onClick={() => navigate("/memory")} className="hover:text-secondary">Media</button></li>
                        <li><button onClick={() => navigate("/profile")} className="hover:text-secondary">Profile</button></li>
                        <li><button onClick={() => navigate("/community")} className="hover:text-secondary">Community</button></li>
                    </ul>
                    {/* SOS Button */}
                    <button onClick={() => navigate("/sos")}>
                        <img className="h-10 w-10 object-contain" src="./assets/SOS Icon.png" alt="SOS" />
                    </button>
                </div>
            </nav>

            {/* Mobile Navigation (Small screens) */}
            <nav className="sm:hidden fixed top-0 left-0 w-full h-16 bg-white shadow-md flex items-center px-6 z-50 mb-10">
                <div className="w-full flex justify-between items-center">
                    {/* Logo / Greeting */}
                    <div className="flex items-center space-x-2">
                        <h1 className="text-2xl font-bold font-display text-primary">Hi John 👋</h1>
                    </div>

                    {/* SOS Button & Menu */}
                    <div className="flex items-center space-x-4">
                        {/* SOS Button */}
                        <button onClick={() => navigate("/sos")}>
                            <img className="h-12 w-12 object-contain" src="./assets/SOS Icon.png" alt="SOS" />
                        </button>

                        {/* Hamburger Menu */}
                        <button onClick={toggleNav}>
                            <img className="h-8 w-8 object-contain" src="./assets/hamburger icon.png" alt="menu" />
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile Sidebar Menu */}
            <div className={`sm:hidden fixed top-0 right-0 w-80 h-full bg-white shadow-lg transform ${isMenuOpen ? "translate-x-0" : "translate-x-full"} transition-transform duration-300 ease-in-out z-40`}>
                <div className="p-6 relative">
                    {/* Close Button */}
                    <button onClick={toggleNav} className="sm:hidden text-2xl absolute top-4 right-4">
                        &times;
                    </button>

                    {/* Navigation Links (Styled to match desktop) */}
                    <ul className="space-y-6 text-lg font-medium text-gray-700 pt-20">
                        <li><button onClick={() => navigate("/")} className="hover:text-secondary">Home</button></li>
                        <li><button onClick={() => navigate("/recommendation")} className="hover:text-secondary">Recommendation</button></li>
                        <li><button onClick={() => navigate("/memory")} className="hover:text-secondary">Media</button></li>
                        <li><button onClick={() => navigate("/profile")} className="hover:text-secondary">Profile</button></li>
                        <li><button onClick={() => navigate("/community")} className="hover:text-secondary">Community</button></li>
                    </ul>
                </div>
            </div>
        </>
    );
};

export default Navbar;
