import React from "react";

const audioData = [
    { src: "/assets/add.png", label: "Add Photo" },
    { src: "/assets/img.png", label: "Audio 1" },
    { src: "/assets/img.png", label: "Audio 2" },
    { src: "/assets/img.png", label: "Audio 3" },
    { src: "/assets/img.png", label: "Audio 4" },
    { src: "/assets/img.png", label: "Audio 5" },
    { src: "/assets/img.png", label: "Audio 6" },
    { src: "/assets/img.png", label: "Audio 7" },
    { src: "/assets/img.png", label: "Audio 8" },
    { src: "/assets/img.png", label: "Audio 9" },
    { src: "/assets/img.png", label: "Audio 10" },
    { src: "/assets/img.png", label: "Audio 11" },
    { src: "/assets/img.png", label: "Audio 12" },
    { src: "/assets/img.png", label: "Audio 13" },
    { src: "/assets/img.png", label: "Audio 14" },
    { src: "/assets/img.png", label: "Audio 15" },
    { src: "/assets/img.png", label: "Audio 16" },
    { src: "/assets/img.png", label: "Audio 17" },
    { src: "/assets/img.png", label: "Audio 18" },
    { src: "/assets/img.png", label: "Audio 19" },
    { src: "/assets/img.png", label: "Audio 20" },
    { src: "/assets/img.png", label: "Audio 21" },
    { src: "/assets/img.png", label: "Audio 22" },
    { src: "/assets/img.png", label: "Audio 23" },
    { src: "/assets/img.png", label: "Audio 24" },
    { src: "/assets/img.png", label: "Audio 25" },
    { src: "/assets/img.png", label: "Audio 26" },
    { src: "/assets/img.png", label: "Audio 27" },
    { src: "/assets/img.png", label: "Audio 28" },
    { src: "/assets/img.png", label: "Audio 29" },
    { src: "/assets/img.png", label: "Audio 30" },
    { src: "/assets/img.png", label: "Audio 31" },
    { src: "/assets/img.png", label: "Audio 32" },
    { src: "/assets/img.png", label: "Audio 33" },
    { src: "/assets/img.png", label: "Audio 34" },
    { src: "/assets/img.png", label: "Audio 35" },
    { src: "/assets/img.png", label: "Audio 36" },
    { src: "/assets/img.png", label: "Audio 37" },
    { src: "/assets/img.png", label: "Audio 38" },
    { src: "/assets/img.png", label: "Audio 39" },
    { src: "/assets/img.png", label: "Audio 40" },
    { src: "/assets/img.png", label: "Audio 41" },
    { src: "/assets/img.png", label: "Audio 42" },
    { src: "/assets/img.png", label: "Audio 43" },
    { src: "/assets/img.png", label: "Audio 44" },
    { src: "/assets/img.png", label: "Audio 45" },
    { src: "/assets/img.png", label: "Audio 46" },
    { src: "/assets/img.png", label: "Audio 47" },
    { src: "/assets/img.png", label: "Audio 48" },
    { src: "/assets/img.png", label: "Audio 49" },
    { src: "/assets/img.png", label: "Audio 50" },
];

const AudioGallery = () => {
    return (
        <div className="p-4 bg-white rounded-xl shadow-md">
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-medium text-gray-800">Memories</h2>
                <span className="text-gray-400">→</span>
            </div>

            {/* Scrollable container */}
            <div className="overflow-x-auto">
                <div className="grid grid-rows-2 md:grid-rows-2 lg:grid-rows-3 grid-flow-col gap-4 pb-2">
                    {audioData.map((audio, index) => (
                        <div
                            key={index}
                            className="bg-white p-2 rounded-xl shadow-sm flex flex-col items-center text-center hover:shadow-md transition-shadow flex-none w-28"
                        >
                            <div className="w-24 h-24 rounded-lg overflow-hidden">
                                <img
                                    src={audio.src}
                                    alt={audio.label}
                                    className="w-full h-full object-cover"
                                />
                            </div>
                            <span className="text-sm text-gray-700 mt-2">{audio.label}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AudioGallery;
