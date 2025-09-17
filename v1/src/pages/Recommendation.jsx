import React from "react";
import ThoughtSection from "../components/recommendations/thought";
import JournalingPrompts from "../components/home/cards";
import RecommendationSection from "../components/recommendations/recommendation";
import ProfileSlider from "../components/recommendations/profile";

const Recommendation = () => {
  return (
    <div className="bg-slate-100 min-h-screen">

      {/* Background Image */}
      <div className="absolute top-0 left-0 w-full h-full -z-10">
        <img
          className="w-full object-cover bg-green-50 opacity-50"
          src="/assets/Topographic bg.png"
          alt="background"
        />
        <img
          className="md:hidden object-cover bg-green-50 opacity-50"
          src="/assets/Topographic bg.png"
          alt="background"
        />
      </div>

      {/* Journaling Section */}
      <div className="m-4">
        <ThoughtSection />
      </div>

      {/* Journaling Prompts */}
      <div className="m-4">
        <JournalingPrompts />
      </div>

      {/* Recommendation Section */}
      <div className="m-4">
        <RecommendationSection />
      </div>

    </div >
  );
};

export default Recommendation;
