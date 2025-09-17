import React from "react";
import { ScrollText } from "lucide-react";

const gratitudeData = [
    {
        title: "Grateful for Health and Energy",
        content: "Today, I am grateful for my health and the energy I have to start the day. Every morning is a new opportunity to take care of my body and mind.",
    },
    {
        title: "Grateful for Inner Peace",
        content: "I am grateful for the peace within me. It helps me stay grounded amidst the chaos of daily life.",
    },
    {
        title: "Grateful for My Mindset",
        content: "I am grateful for my mindset and the way I approach life. With a positive outlook, I see challenges as opportunities to grow.",
    },
    {
        title: "Grateful for the Present Moment",
        content: "I am grateful for the present moment. Right now, I have the power to make choices that align with my values.",
    },
    {
        title: "Grateful for Self-Growth",
        content: "Today, I am grateful for the continuous growth I experience. Each day offers a chance to become better than yesterday.",
    },
    {
        title: "Grateful for Opportunities",
        content: "I am grateful for the opportunities I have each day to learn, improve, and contribute.",
    },
];

const Gratitude = () => {
    return (
        <div className="p-4 bg-white rounded-xl shadow-md">
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-medium text-gray-800">Gratitude Journals</h2>
                <span className="text-gray-400">→</span>
            </div>

            {/* Scrollable container */}
            <div className="overflow-x-auto">
                <div className="grid grid-rows-3 md:grid-rows-2 lg:grid-rows-2 grid-flow-col gap-4 pb-2">
                    {gratitudeData.map((item, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-xl shadow-sm p-4 flex flex-col w-72 hover:shadow-md transition-shadow"
                        >
                            <ScrollText className="h-5 w-5 text-gray-400 mb-3" />
                            <h3 className="text-base font-medium mb-2">{item.title}</h3>
                            <p className="text-sm text-gray-600">{item.content}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Gratitude;
