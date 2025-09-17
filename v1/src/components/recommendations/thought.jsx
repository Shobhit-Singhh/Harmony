import { Send, Paperclip, Smile } from "lucide-react";

const ThoughtSection = () => {
    return (
        <section className="mt-[70px]">
            <div className="flex items-center justify-center bg-gradient-to-r from-emerald-200 to-green-300 py-6 rounded-lg shadow-lg">
                <div className="flex flex-col items-center justify-center w-full max-w-lg px-6">
                    <a className="text-lg font-medium text-green-900 hover:underline" href="#">
                        Daily Reflection
                    </a>
                    <h2 className="text-2xl font-bold text-center text-green-700 my-4">
                        How do you feel about your current emotions?
                    </h2>
                    
                    {/* Thought Input Area */}
                    <div className="w-full">
                        <textarea
                            className="p-3 w-full rounded-lg border-2 border-green-500 focus:ring-2 focus:ring-green-400 focus:outline-none resize-none bg-white"
                            placeholder="Write your thoughts here..."
                        ></textarea>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-between w-full mt-3">
                        {/* Media Upload Button */}
                        <button className="flex items-center gap-1 text-green-700 hover:text-green-900">
                            <Paperclip className="w-5 h-5" />
                            <span>Add Media</span>
                        </button>

                        {/* Submit Button */}
                        <button className="flex items-center gap-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all">
                            <span>Submit</span>
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ThoughtSection;
