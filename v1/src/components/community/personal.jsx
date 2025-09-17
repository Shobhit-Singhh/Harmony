import { useState } from "react";
import Avatar from "react-avatar";
import { FaComment, FaImage, FaPersonWalking, FaUserGroup, FaHeartPulse } from "react-icons/fa6";

const profiles = [
    { id: 1, name: "Mom", color: "#FF6B6B" },
    { id: 2, name: "Dad", color: "#4E89AE" },
    { id: 3, name: "GrandMa", color: "#8E44AD" },
    { id: 4, name: "Sophia", color: "#E67E22", highlight: true },
    { id: 5, name: "John", color: "#2ECC71" },
    { id: 6, name: "Emma", color: "#3498DB" },
    { id: 7, name: "Liam", color: "#FF4757" },
    { id: 8, name: "Olivia", color: "#1E90FF" },
    { id: 9, name: "Noah", color: "#27AE60" },
    { id: 10, name: "Ava", color: "#D35400" },
];

const Personal = () => {
    const [openMenus, setOpenMenus] = useState({});

    const toggleMenu = (id) => {
        setOpenMenus((prev) => ({ ...prev, [id]: !prev[id] }));
    };

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-6">Personal Connections</h2>
            <div className="overflow-x-auto">
                <div className="
                    grid grid-flow-row auto-rows-[minmax(180px,_1fr)] gap-4 
                    sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
                >
                    {profiles.map((profile) => (
                        <div
                            key={profile.id}
                            className={`p-4 border rounded-lg shadow-lg flex flex-col items-center transition-all
                                ${profile.highlight ? "ring-2 ring-primary" : ""} 
                                ${openMenus[profile.id] ? "p-6" : ""}`}
                        >
                            <Avatar name={profile.name} size="60" round={true} color={profile.color} />
                            <h3 className="text-lg font-semibold mt-2">{profile.name}</h3>

                            {openMenus[profile.id] && (
                                <div className="flex gap-2 mt-2">
                                    {[FaComment, FaImage, FaPersonWalking, FaUserGroup, FaHeartPulse].map(
                                        (Icon, index) => (
                                            <button
                                                key={index}
                                                className="p-2 bg-accent-blue-light text-primary rounded-lg hover:bg-accent-blue-light/80 transition-colors"
                                            >
                                                <Icon className="w-4 h-4" />
                                            </button>
                                        )
                                    )}
                                </div>
                            )}

                            <button
                                onClick={() => toggleMenu(profile.id)}
                                className="mt-3 w-full py-2 px-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
                            >
                                {openMenus[profile.id] ? "Close" : "Share"}
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Personal;
