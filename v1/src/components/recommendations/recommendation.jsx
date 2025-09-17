import { useState } from "react";
import { Star, Bookmark, Film, BookOpen, Smile, PlayCircle } from "lucide-react";
import { motion } from "framer-motion";

const recommendations = [
    {
        title: "Gratitude Journal",
        description: "Daily prompts to practice gratitude and self-reflection.",
        images: ["./assets/Recommendation/r2.avif", "./assets/Recommendation/r1.avif"],
        tags: ["Mindfulness", "Self-Reflection", "Well-being"],
        icon: <Smile className="text-yellow-500" size={24} />,
        rating: 4.8
    },
    {
        title: "Self-Letter Writing",
        description: "Write letters to your future self for motivation and reflection.",
        images: ["./assets/Recommendation/r3.avif"],
        tags: ["Personal Growth", "Journaling"],
        icon: <BookOpen className="text-green-500" size={24} />,
        rating: 4.6
    },
    {
        title: "Mood-Based Movies",
        description: "Movie recommendations based on your current emotions.",
        images: ["./assets/Recommendation/r5.avif", "./assets/Recommendation/r6.avif"],
        tags: ["Movies", "Emotions", "Entertainment"],
        icon: <Film className="text-blue-500" size={24} />,
        rating: 4.7
    },
    {
        title: "Curated Playlists",
        description: "Music playlists tailored to your mood and energy levels.",
        images: ["./assets/Recommendation/r7.avif"],
        tags: ["Music", "Mood", "Relaxation"],
        icon: <PlayCircle className="text-purple-500" size={24} />,
        rating: 4.9
    },
    {
        title: "Understanding CBT Techniques",
        description: "Educational articles explaining Cognitive Behavioral Therapy.",
        images: ["./assets/Recommendation/r4.avif"],
        tags: ["Psychology", "CBT", "Mental Health"],
        icon: <BookOpen className="text-green-500" size={24} />,
        rating: 4.5
    },
    {
        title: "Mindfulness Practices",
        description: "Learn how mindfulness can improve mental well-being.",
        images: ["./assets/Recommendation/r8.avif"],
        tags: ["Mindfulness", "Meditation", "Well-being"],
        icon: <BookOpen className="text-green-500" size={24} />,
        rating: 4.8
    }
];

const RecommendationCard = ({ rec }) => {
    const [saved, setSaved] = useState(false);
    const [currentImage, setCurrentImage] = useState(0);
    return (
        <motion.div 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-white shadow-xl rounded-lg overflow-hidden transition-all duration-300"
        >
            <div className="relative">
                <div className='flex items-center justify-center mt-4 rounded-md overflow-hidden'>
                    <img className="h-40 w-full object-cover mx-2 rounded-lg" src={rec.images[currentImage]} alt={rec.title} />
                </div>
                <button 
                    className={`absolute top-3 right-3 p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition ${saved ? "text-yellow-500" : "text-gray-700"}`}
                    onClick={() => setSaved(!saved)}
                >
                    <Bookmark />
                </button>
                {rec.images.length > 1 && (
                    <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 flex gap-2">
                        {rec.images.map((_, index) => (
                            <button key={index} 
                                className={`w-3 h-3 px-3 rounded-full ${index === currentImage ? 'bg-gray-800' : 'bg-gray-400'}`}
                                onClick={() => setCurrentImage(index)}
                            />
                        ))}
                    </div>
                )}
            </div>
            <div className="p-5">
                <div className="flex items-center gap-2">
                    {rec.icon}
                    <h3 className="text-xl font-bold text-gray-900">{rec.title}</h3>
                </div>
                <p className="mt-2 text-gray-600">{rec.description}</p>
                <div className="flex flex-wrap gap-2 mt-3">
                    {rec.tags.map((tag, index) => (
                        <span key={index} className="bg-gray-200 text-gray-800 text-sm px-3 py-1 rounded-full">{tag}</span>
                    ))}
                </div>
                <div className="flex items-center gap-1 mt-4">
                    {[1, 2, 3, 4, 5].map((num) => (
                        <Star 
                            key={num} 
                            size={20} 
                            className={`cursor-pointer ${num <= rec.rating ? "text-yellow-500" : "text-gray-400"}`} 
                        />
                    ))}
                </div>
            </div>
        </motion.div>
    );
};

const RecommendationSection = () => {
    return (
        <section className="py-10 bg-gray-100 m-4 rounded-xl pb-14">
            <div className="container mx-auto px-4">
                <h2 className="text-3xl font-bold text-center text-gray-800">Recommendations</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-10">
                    {recommendations.map((rec, index) => (
                        <RecommendationCard key={index} rec={rec} />
                    ))}
                </div>
            </div>
        </section>
    );
};

export default RecommendationSection;
