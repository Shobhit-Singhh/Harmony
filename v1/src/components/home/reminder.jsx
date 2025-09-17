import React from "react";
import { Droplets, Timer, Eye, Brain, Wind, Pill } from "lucide-react";

const ReminderCards = () => {
    const reminders = [
        { title: "Stay Hydrated", icon: <Droplets /> },
        { title: "Take a Break", icon: <Timer /> },
        { title: "Eye Exercise", icon: <Eye /> },
        { title: "Mindfulness", icon: <Brain /> },
        { title: "Deep Breathing", icon: <Wind /> },
        { title: "Medication", icon: <Pill/> },
    ];

    return (
        <div className="">
            <div className="flex items-center gap-2 mb-4 ">
                <h2 className="text-lg font-medium text-gray-800">Daily Reminders</h2>
                <span className="text-gray-400">→</span>
            </div>
            <div className="grid grid-flow-col grid-rows-2 lg:grid-rows-3 gap-4 overflow-x-auto pb-4  ">
                {reminders.map((reminder, index) => (
                    <div
                        key={index}
                        className="flex-none w-40 bg-white rounded-xl shadow-sm p-4 flex flex-col items-center gap-3 grid-rows-3"
                    >
                        <div className="p-3 bg-gray-50 rounded-full">
                            {reminder.icon}
                        </div>
                        <span className="text-sm font-medium">{reminder.title}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReminderCards;