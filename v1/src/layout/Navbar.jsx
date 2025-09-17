import React from "react";
import { useNavigate } from "react-router-dom";
import { Home, Lightbulb, Image, Users, User } from "lucide-react";
import Chatbot from "../components/Chatbot";

const NavigationItem = ({ icon: Icon, label, path }) => {
    const navigate = useNavigate();

    return (
        <button
            onClick={() => navigate(path)}
            className="flex flex-col items-center p-3 rounded-lg hover:bg-primary-light/20 transition-all"
            aria-label={label}
        >
            <Icon className="-m-1 w-8 h-8 text-primary p-[2px]" />
        </button>
    );
};

const FooterLinkSection = ({ title, links }) => (
    <div>
        <h4 className="font-display text-lg mb-4">{title}</h4>
        <ul className="space-y-3">
            {links.map((link) => (
                <li key={link.text}>
                    <a
                        href={link.href}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        {link.text}
                    </a>
                </li>
            ))}
        </ul>
    </div>
);

const Footer = () => {
    const mobileNavItems = [
        { icon: Home, label: "Home", path: "/" },
        { icon: Lightbulb, label: "Recommendation", path: "/recommendation" },
        { icon: Image, label: "Media", path: "/memory" },
        { icon: Users, label: "Community", path: "/community" },
        { icon: User, label: "Profile", path: "/profile" }
    ];

    const footerSections = {
        company: {
            title: "Company",
            links: [
                { text: "About Us", href: "#" },
                { text: "Contact Us", href: "#" },
                { text: "Partners", href: "#" }
            ]
        },
        resources: {
            title: "Resources",
            links: [
                { text: "Resources", href: "#" },
                { text: "FAQs", href: "#" },
                { text: "Support", href: "#" }
            ]
        },
        account: {
            title: "Account",
            links: [
                { text: "Log in", href: "#" },
                { text: "Register", href: "#" },
                { text: "Dashboard", href: "#" }
            ]
        }
    };

    return (
        <>
            {/* Mobile Bottom Navigation */}
            <nav className="sm:hidden fixed bottom-0 left-0 w-full bg-white shadow-lg py-2 z-50 border-t border-neutral-200">
                <div className="flex justify-around items-center">
                    {mobileNavItems.map((item) => (
                        <NavigationItem
                            key={item.label}
                            icon={item.icon}
                            path={item.path}
                        />
                    ))}
                </div>
            </nav>

            {/* Desktop Footer */}
            <footer className="hidden sm:block bg-primary-dark text-white py-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-4 gap-8">
                        {/* Logo and tagline */}
                        <div className="col-span-1">
                            <div className="flex items-center space-x-2 mb-4">
                                <img src="/assets/logo_light.png" alt="Neoptio logo" className="w-8 h-8" />
                                <span className="font-display text-xl">Neoptio</span>
                            </div>
                            <p className="text-sm text-gray-400">
                                Explore the future of mental healthcare
                            </p>
                        </div>

                        {/* Navigation Links */}
                        <div className="col-span-3 grid grid-cols-3 gap-8">
                            {Object.values(footerSections).map((section) => (
                                <FooterLinkSection
                                    key={section.title}
                                    title={section.title}
                                    links={section.links}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </footer>

            <Chatbot />
        </>
    );
};

export default Footer;