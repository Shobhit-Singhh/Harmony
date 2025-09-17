import React from "react";

const professionals = [
    { id: 1, name: "Dr. John Doe", specialty: "Cardiologist", location: "New York, NY", image: "./assets/profile/Profile1.avif" },
    { id: 2, name: "Dr. Jane Smith", specialty: "Dermatologist", location: "Los Angeles, CA", image: "./assets/profile/Profile2.avif" },
    { id: 3, name: "Dr. Emily Johnson", specialty: "Neurologist", location: "Chicago, IL", image: "./assets/profile/Profile3.avif" },
    { id: 4, name: "Dr. Sarah Williams", specialty: "Pediatrician", location: "Phoenix, AZ", image: "./assets/profile/Profile4.avif" },
    { id: 5, name: "Dr. Daniel Martinez", specialty: "Psychiatrist", location: "Philadelphia, PA", image: "./assets/profile/Profile5.avif" },
];

const HealthcareProfessionals = () => {
    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-6">Healthcare Professionals</h2>
            <div className="overflow-x-auto">
                <div className="grid grid-flow-col auto-cols-[minmax(350px,_1fr)] grid-rows-2 sm:grid-rows-2 md:grid-rows-3 lg:grid-rows-1 gap-4">
                    {professionals.map((profile) => (
                        <div key={profile.id} className="p-4 border rounded-lg shadow-lg flex flex-col items-center">
                            <img className="w-20 h-20 rounded-full mb-4 object-cover" src={profile.image} alt={`Profile picture of ${profile.name}`} />
                            <h3 className="text-lg font-semibold">{profile.name}</h3>
                            <p className="text-gray-500">{profile.specialty}</p>
                            <p className="text-gray-400 text-sm">{profile.location}</p>
                            <button className="mt-4 w-full py-2 px-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors">
                                Connect
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default HealthcareProfessionals;

