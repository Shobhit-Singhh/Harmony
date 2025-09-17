import Dashboard from "../components/home/dashboard";
import JournalingPrompts from "../components/home/cards";
import GraphCards from "../components/home/graphs";
import ReminderCards from "../components/home/reminder";
import ScoreBoard from "../components/home/scores";
import CalendarSection from "../components/home/calendar";

const Home = () => {
    return (
        <div className="mx-4 bg-gradient-to-b from-blue-50 to-slate-100 min-h-screen py-12">
            <div className="-mx-4 mb-12 text-center">
                <Dashboard />
            </div>

            <div className="mb-12">
                <JournalingPrompts />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                {/* Left Column - Takes 2/3 Width */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-white shadow-lg rounded-xl p-6">
                        <GraphCards />
                    </div>
                </div>

                {/* Right Column - Takes 1/3 Width */}
                <div className="space-y-8">
                    <div className="bg-white shadow-lg rounded-xl p-6">
                        <ScoreBoard />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 mt-10">
                {/* Left Column - Takes 2/3 Width */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-white shadow-lg rounded-xl p-6">
                        < CalendarSection />
                    </div>
                </div>

                {/* Right Column - Takes 1/3 Width */}
                <div className="space-y-8">
                    <div className="bg-white shadow-lg rounded-xl p-6">
                        < ReminderCards />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;