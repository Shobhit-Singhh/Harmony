import React, { useState } from "react";
import { Star, X, Smile } from "lucide-react";

const promptCards = [
    {
        title: "Frustration Burns Within",
        description: "I was irritated all day because _ _ _",
        points: "+1 pts",
        icon: "./assets/Mood/Mood=Angry.png",
        background: "bg-red-50",
        borderColor: "border-red-200",
        prompts: "13 AI Suggested Prompts",
    },
    {
        title: "Happiness Shines Bright",
        description: "I'm grateful for _ _ _",
        points: "+1 pts",
        icon: "./assets/Mood/Mood=Happy.png",
        background: "bg-yellow-50",
        borderColor: "border-yellow-200",
        prompts: "10 AI Suggested Prompts",
    },
    {
        title: "Lost in a Whirl of Thoughts",
        description: "I was lost in thought _ _ _",
        points: "+1 pts",
        icon: "./assets/Mood/Mood=Thinking.png",
        background: "bg-green-50",
        borderColor: "border-green-200",
        prompts: "15 AI Suggested Prompts",
    },
    {
        title: "Sadness Looms Over",
        description: "I was low all day because _ _ _",
        points: "+1 pts",
        icon: "./assets/Mood/Mood=Sad.png",
        background: "bg-blue-50",
        borderColor: "border-blue-200",
        prompts: "12 AI Suggested Prompts",
    },
    {
        title: "Anxiety Creeps In",
        description: "I couldn't shake the thought _ _ _",
        points: "+1 pts",
        icon: "./assets/Mood/Mood=Worry.png",
        background: "bg-purple-50",
        borderColor: "border-purple-200",
        prompts: "8 AI Suggested Prompts",
    },
    {
        title: "Crying Out Loud",
        description: "No one knows but I'm _ _ _",
        points: "+1 pts",
        icon: "./assets/Mood/Mood=Cry.png",
        background: "bg-pink-50",
        borderColor: "border-pink-200",
        prompts: "5 AI Suggested Prompts",
    },
];

const JournalingPrompts = () => {
    const [selectedCard, setSelectedCard] = useState(null);
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        images: [],
        tags: "",
        rating: 0,
        mood: ""
    });

    const handleCardClick = (card) => {
        setSelectedCard(card);
        setFormData({ ...formData, title: card.title, description: card.description });
    };

    const handleClose = () => {
        setSelectedCard(null);
    };

    return (
        <div className="p-4 bg-white rounded-xl shadow-md">
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-medium text-gray-800">Daily Reflections</h2>
                <span className="text-gray-400">→</span>
            </div>

            <div className="overflow-x-auto scrollbar-hide">
                <div className="grid grid-flow-col auto-cols-[minmax(280px,_1fr)] gap-4">
                    {promptCards.map((card, index) => (
                        <div
                            key={index}
                            onClick={() => handleCardClick(card)}
                            className={`min-w-[280px] p-4 rounded-xl cursor-pointer ${card.background} ${card.borderColor}`}
                        >
                            <h3 className="text-base font-medium mb-2">{card.title}</h3>
                            <p className="text-sm text-gray-600">{card.description}</p>
                            <span className="text-xs font-medium mt-2 inline-block bg-white px-2 py-1 rounded-full">
                                {card.points}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {selectedCard && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg w-96 relative z-50">
                        <button onClick={handleClose} className="absolute top-3 right-3">
                            <X size={20} />
                        </button>
                        <h2 className="text-lg font-bold mb-2">{selectedCard.title}</h2>
                        <select
                            className="w-full p-2 border rounded mb-2"
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        >
                            <option value="">Choose a prompt...</option>
                            {["I couldn't shake the thought", "Today felt like a dream", "A moment I’ll never forget", "If only I could rewind time", "This day taught me..."].map((prompt, index) => (
                                <option key={index} value={prompt}>{prompt}</option>
                            ))}
                        </select>
                        <textarea
                            className="w-full p-2 border rounded"
                            placeholder="Add description..."
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        />
                        <input
                            className="w-full p-2 border rounded mt-2"
                            placeholder="Add tags (comma-separated)..."
                            value={formData.tags}
                            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                        />
                        <input
                            type="file"
                            accept="image/*"
                            className="w-full p-2 border rounded mt-2"
                            onChange={(e) => setFormData({ ...formData, images: [...formData.images, e.target.files[0]] })}
                        />
                        <div className="flex items-center gap-1 mt-3">
                            {[1, 2, 3, 4, 5].map((num) => (
                                <Star
                                    key={num}
                                    size={20}
                                    className={`cursor-pointer ${num <= formData.rating ? "text-yellow-500" : "text-gray-400"}`}
                                    onClick={() => setFormData({ ...formData, rating: num })}
                                />
                            ))}
                        </div>
                        <div className="mt-4">
                            <label className="text-sm font-medium">Mood Emoji:</label>
                            <div className="flex gap-2 mt-2">
                                {["😀", "😢", "😡", "😨", "😌"].map((emoji, index) => (
                                    <button
                                        key={index}
                                        className="text-xl"
                                        onClick={() => setFormData({ ...formData, mood: emoji })}
                                    >
                                        {emoji}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <button className="mt-4 w-full bg-blue-500 text-white p-2 rounded">Save</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default JournalingPrompts;
