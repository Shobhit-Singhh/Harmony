import React from "react";
import { Outlet } from "react-router-dom";
import Chatbot from "../components/Chatbot";
import BottomNavChat from "../layout/Navbar";
import TopNavbar from "../layout/Header";

const MainLayout = () => {
    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
            <TopNavbar /> 
            <Outlet /> 
            <BottomNavChat />
        </div>
    );
};

export default MainLayout;
