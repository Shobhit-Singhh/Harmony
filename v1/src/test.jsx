import React, { useState } from "react";

const ChatbotMessage = ({ text }) => {
  return (
    <div className="chatbot-message flex items-start space-x-3">
      <img
        src="https://via.placeholder.com/30"
        alt="chatbot-avatar"
        className="rounded-full"
      />
      <p className="bg-gray-300 p-2 rounded-lg">{text}</p>
    </div>
  );
};

const UserMessage = ({ text }) => {
  return (
    <div className="user-message flex items-start space-x-3 flex-row-reverse">
      <img
        src="https://via.placeholder.com/30"
        alt="user-avatar"
        className="rounded-full"
      />
      <p className="bg-blue-300 p-2 rounded-lg">{text}</p>
    </div>
  );
};

const App = () => {
  const [message, setMessage] = useState("");

  return (
    <div className="container mx-auto p-4">
      <div className="chatbot-popup bg-gray-100 rounded-lg shadow-md">
        <div className="chatbot-popup-container">
          {/* Header */}
          <div className="chatbot-popup-header flex items-center justify-between bg-blue-500 text-white px-4 py-2 rounded-t-lg">
            <div className="flex items-center">
              <img
                src="https://via.placeholder.com/30"
                alt="chatbot-avatar"
                className="rounded-full mr-2"
              />
              <h4 className="text-lg font-bold">Chatbot</h4>
            </div>
            <button className="text-sm bg-red-500 px-2 py-1 rounded-lg">Close</button>
          </div>

          {/* Body */}
          <div className="chatbot-popup-body p-4 h-80 overflow-y-scroll">
            <div className="chatbot-popup-message space-y-4">
              <ChatbotMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Quos, adipisci." />
              <UserMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Reprehenderit, porro?" />
              <ChatbotMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Quos, adipisci." />
              <UserMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Reprehenderit, porro?" />
              <ChatbotMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Quos, adipisci." />
              <UserMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Reprehenderit, porro?" />
              <ChatbotMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Quos, adipisci." />
              <UserMessage text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Reprehenderit, porro?" />
            </div>
          </div>

          {/* Footer */}
          <div className="chatbot-popup-footer flex items-center bg-gray-200 px-4 py-2 rounded-b-lg">
            <input
              type="text"
              placeholder="Type a message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1 border border-gray-300 rounded-lg p-2 mr-2"
            />
            {message.trim() ? (
              <button className="bg-blue-500 text-white px-4 py-2 rounded-lg">Send</button>
            ) : (
              <button className="bg-gray-500 text-white px-4 py-2 rounded-lg">Skip</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
