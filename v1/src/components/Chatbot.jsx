import React, { useState, useEffect } from "react";
import { Loader2, Send, SkipForward, X, User, ChevronDown } from "lucide-react";

const ConfirmationModal = ({ isOpen, onClose, onConfirm }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40">
            <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4 shadow-xl">
                <h3 className="text-xl font-display text-dark mb-4">Skip Question</h3>
                <p className="text-neutral-600 mb-6">Are you sure you want to skip this question?</p>
                <div className="flex justify-end space-x-4">
                    <button onClick={onClose} className="px-4 py-2 text-neutral-600 hover:text-neutral-800 transition-colors">
                        Cancel
                    </button>
                    <button onClick={onConfirm} className="px-4 py-2 bg-secondary text-white rounded-lg hover:bg-secondary-dark transition-colors">
                        Confirm Skip
                    </button>
                </div>
            </div>
        </div>
    );
};

const chatbotIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 1024 1024">
            <path fill="#1754C3" d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z" />
        </svg>
    );
};

const ChatbotMessage = ({ text }) => {
    return (
        <div className="flex items-end space-x-3 mb-4">
            <div className="w-10 h-10 bg-primary-light/20 rounded-full flex items-center justify-center">
                {chatbotIcon()}
            </div>
            <div className="bg-accent-blue-light p-4 rounded-tl-2xl rounded-tr-2xl rounded-br-2xl rounded-bl-md max-w-xs shadow-sm">
                <p className="text-neutral-800 text-sm">{text}</p>
            </div>
        </div>
    );
};

const UserMessage = ({ text }) => {
    return (
        <div className="flex items-end space-x-3 flex-row-reverse mb-4 gap-2">
            <div className="w-10 h-10 bg-secondary-light rounded-full flex items-center justify-center text-white">
                <User className="w-5 h-5" />
            </div>
            <div className="bg-accent-orange/30 p-4 rounded-tl-2xl rounded-tr-2xl rounded-bl-2xl rounded-br-md max-w-xs shadow-sm">
                <p className="text-neutral-800 text-sm">{text}</p>
            </div>
        </div>
    );
};

const LogsList = ({ text }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4 border border-neutral-100">
            <div className="flex justify-between items-center mb-2">
                <h4 className="text-sm font-medium text-neutral-700">Analysis Log</h4>
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="text-neutral-500 hover:text-neutral-700"
                >
                    <ChevronDown className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </button>
            </div>
            {isExpanded && (
                <div className="mt-2">
                    {typeof text === "object" ? (
                        <pre className="text-xs text-neutral-600 overflow-x-auto bg-neutral-50 p-3 rounded">
                            {JSON.stringify(text, null, 2)}
                        </pre>
                    ) : (
                        <p className="text-sm text-neutral-600">{text}</p>
                    )}
                </div>
            )}
        </div>
    );
};

const Chatbot = () => {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]);
    const [log, setlog] = useState([]);
    const [logs, setlogs] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [placeholder, setPlaceholder] = useState("Let's talk about it...");
    const [showSkipConfirmation, setShowSkipConfirmation] = useState(false);
    const [isSkipAllowed, setIsSkipAllowed] = useState(false);
    const [isWaitingForAI, setIsWaitingForAI] = useState(false);

    const handleSkip = () => {
        if (isWaitingForAI) return;
        setShowSkipConfirmation(true);
    };

    const confirmSkip = () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            try {
                setIsWaitingForAI(true);
                socket.send(JSON.stringify({ user_response: "" }));
                setMessages((prevMessages) => [
                    ...prevMessages,
                    { type: "user", text: "Next Question Please" },
                ]);
            } catch (error) {
                console.error("Error sending skip message:", error);
                setIsWaitingForAI(false);
            }
        }
        setShowSkipConfirmation(false);
    };

    useEffect(() => {
        let ws;
        let reconnectTimeout;

        const connectWebSocket = () => {
            // ws = new WebSocket("ws://localhost:8000/ws");
            ws = new WebSocket("wss://harmony-ai-6x1o.onrender.com/ws");

            ws.onopen = () => {
                console.log("Connected to WebSocket");
                setSocket(ws);
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log("Parsed WebSocket data:", data);

                    if (data.AIresponce?.question) {
                        console.log("Question:", data.AIresponce.question);
                        setMessages((prev) => [
                            ...prev,
                            { type: "chatbot", text: data.AIresponce.question },
                        ]);
                    }

                    if (data.AIresponce?.skip_allowed !== undefined) {
                        setIsSkipAllowed(data.AIresponce.skip_allowed);
                        setPlaceholder(
                            data.AIresponce.skip_allowed
                                ? "You can move to the next question"
                                : "Wanna talk about it?"
                        );
                    }

                    if (data.AIresponce?.log) {
                        try {
                            let logData = data.AIresponce.log;

                            // Ensure logData is properly formatted as JSON
                            if (typeof logData === "string") {
                                logData = JSON.parse(logData.trim());
                            }

                            console.log("Parsed Log:", logData);

                            // Store parsed JSON directly instead of converting it to a string
                            setlogs((prevLogs) => [...prevLogs, { type: "log", text: logData }]);
                        } catch (error) {
                            console.error("Error parsing log:", error, "Raw Log Data:", data.AIresponce.log);

                            // Fallback: Store raw log safely if parsing fails
                            setlogs((prevLogs) => [...prevLogs, { type: "log", text: data.AIresponce.log }]);
                        }
                    }

                    setIsWaitingForAI(false);
                } catch (error) {
                    console.error("Error parsing WebSocket message:", error);
                    setIsWaitingForAI(false);
                }
            };

            ws.onclose = () => {
                console.log("WebSocket disconnected, reconnecting in 3 seconds...");
                setIsConnected(false);
                reconnectTimeout = setTimeout(connectWebSocket, 3000);
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                ws.close();
            };
        };

        connectWebSocket();

        return () => {
            if (ws) {
                ws.close();
            }
            clearTimeout(reconnectTimeout);
        };
    }, []);

    const handleSend = () => {
        if (!message.trim() || !socket || socket.readyState !== WebSocket.OPEN || isWaitingForAI)
            return;

        try {
            setIsWaitingForAI(true);
            socket.send(JSON.stringify({ user_response: message }));
            setMessages((prevMessages) => [
                ...prevMessages,
                { type: "user", text: message },
            ]);
            setMessage("");
        } catch (error) {
            console.error("Error sending message:", error);
            setIsWaitingForAI(false);
        }
    };

    return (
        <div className="mb-10 bg-gradient-to-b from-neutral-50 to-accent-blue-light/30 p-4">
            {!isOpen && (
                <button
                    className="fixed bottom-20 sm:bottom-8 right-5 z-40 w-16 h-16 bg-primary rounded-full shadow-xl flex items-center justify-center hover:bg-primary-dark transition-all"
                    onClick={() => setIsOpen(true)}
                >
                    <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center">
                        {chatbotIcon()}
                    </div>
                </button>
            )}

            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 className="text-xl font-display text-dark mb-4 border-b border-neutral-200 pb-3 flex items-center">
                        {chatbotIcon()}
                        <div className="ml-5">Analysis Progress</div>
                    </h2>
                    <div className="space-y-3">
                        {logs.map((msg, index) => (
                            <LogsList key={index} text={msg.text} />
                        ))}
                        {isWaitingForAI && (
                            <div className="flex items-center justify-center p-6">
                                <Loader2 className="animate-spin text-primary" size={32} />
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className={`fixed right-5 bottom-20 sm:bottom-8 z-40 bg-white rounded-lg shadow-xl transition-all duration-300 transform ${isOpen ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'}`}
                style={{
                    width: "350px",
                    maxHeight: "500px",
                }}>
                <div className="flex flex-col h-full border border-neutral-200 rounded-lg">
                    <div className="bg-primary text-white p-3 rounded-t-lg flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                                {chatbotIcon()}
                            </div>
                            <h3 className="text-base font-display">Support Assistant</h3>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                            aria-label="Close"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4" style={{ maxHeight: "350px" }}>
                        {messages.map((msg, index) =>
                            msg.type === "user" ? (
                                <UserMessage key={index} text={msg.text} />
                            ) : (
                                <ChatbotMessage key={index} text={msg.text} />
                            )
                        )}
                        {isWaitingForAI && (
                            <div className="flex items-center justify-center p-4">
                                <Loader2 className="animate-spin text-primary" size={24} />
                            </div>
                        )}
                    </div>

                    <div className="border-t border-neutral-200 p-3">
                        <div className="flex space-x-2">
                            <input
                                type="text"
                                placeholder={isWaitingForAI ? "Please wait..." : placeholder}
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                className="flex-1 px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                                disabled={isWaitingForAI}
                                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                            />
                            {message.trim() ? (
                                <button
                                    onClick={handleSend}
                                    className={`p-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors ${isWaitingForAI ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    disabled={isWaitingForAI}
                                    aria-label="Send message"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            ) : (
                                <button
                                    onClick={handleSkip}
                                    className={`p-2 bg-secondary text-white rounded-lg hover:bg-secondary-dark transition-colors ${isWaitingForAI || !isSkipAllowed ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    disabled={isWaitingForAI || !isSkipAllowed}
                                    aria-label="Skip question"
                                >
                                    <SkipForward className="w-5 h-5" />
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <ConfirmationModal
                isOpen={showSkipConfirmation}
                onClose={() => setShowSkipConfirmation(false)}
                onConfirm={confirmSkip}
            />
        </div>
    );
};

export default Chatbot;