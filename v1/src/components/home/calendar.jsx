import React from "react";

const CalendarSection = () => {
    return (
        <div className="">
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-medium text-gray-800">Your Schedule</h2>
                <span className="text-gray-400">→</span>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-sm">
                <div className="h-96 bg-gray-50 rounded-lg"></div>
            </div>
        </div>
    );
};

export default CalendarSection;