import { useState } from "react";

const profiles = [
  { name: "Dr. John Doe", specialization: "Child Psychiatry", experience: "10 years", connected: "2" },
  { name: "Dr. Jane Smith", specialization: "Adult Psychiatry", experience: "8 years", connected: "4" },
  { name: "Dr. Emily Brown", specialization: "Psychotherapy", experience: "5 years", connected: "3" },
  { name: "Dr. Mark Wilson", specialization: "Forensic Psychiatry", experience: "12 years", connected: "1" },
  { name: "Dr. Sarah Lee", specialization: "Geriatric Psychiatry", experience: "7 years", connected: "6" },
];

const ProfileSlider = () => {
  const [visibleButtons, setVisibleButtons] = useState({});

  const toggleButtons = (index) => {
    setVisibleButtons((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  return (
    <div className="slider flex overflow-x-auto space-x-4 p-4">
      {profiles.map((profile, index) => (
        <div key={index} className="bg-white shadow-lg rounded-lg p-4 min-w-[250px]">
          <h3 className="text-lg font-bold">{profile.name}</h3>
          <p className="text-gray-600">{profile.specialization}</p>
          <p className="text-gray-500">Experience: {profile.experience}</p>
          <p className="text-gray-500">Connected with: {profile.connected}</p>
          <button 
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded" 
            onClick={() => toggleButtons(index)}
          >
            Share
          </button>
          {visibleButtons[index] && (
            <div className="custom-buttons mt-2">
              <button className="px-3 py-1 bg-green-500 text-white rounded mr-2">WhatsApp</button>
              <button className="px-3 py-1 bg-gray-700 text-white rounded">Email</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ProfileSlider;
