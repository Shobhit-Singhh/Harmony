import { useEffect } from "react";
import AudioGallery from "../components/memories/audio";
import ImageGallery from "../components/memories/gallery";
import Letter from "../components/memories/letter";
import Gratitude from "../components/memories/gratitude";

const Memories = () => {
    return (
        <div className="bg-slate-100 min-h-screen py-10 px-6 lg:px-16">
            <h2 className="text-3xl font-bold text-center text-green-800 mb-8">Memories</h2>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Takes 2/3 Width */}
                <div className="lg:col-span-2 space-y-6">
                <div className="">
                        <Letter />
                    </div>
                    <div className="">
                        <Gratitude />
                    </div>
                    
                </div>

                {/* Right Column - Takes 1/3 Width */}
                <div className="space-y-6">
                    <div className="">
                        <ImageGallery />
                    </div>
                    <div className="">
                        <AudioGallery />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Memories;
