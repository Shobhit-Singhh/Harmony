import Personal from "../components/community/personal";
import ProfessionalSlider from "../components/community/professional";

const Community = () => {
    return (
        <div className="py-4 min-h-screen bg-gradient-to-b from-neutral-50 to-accent-blue-light">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                {/* Personal Connections Section */}
                <div className="mb-16">
                    <Personal />
                </div>

                {/* Professional Connections Section */}
                <div>
                    <ProfessionalSlider />
                </div>
            </div>
        </div>
    );
};

export default Community;