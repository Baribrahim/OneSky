import React, { useState, useRef, useEffect } from "react";
import "../styles/chatbot.css";
import logo from "../assets/OneSky-logo.png";

/**
 * Chatbot Component
 * Floating chat interface with toggle button in bottom-right corner
 * Uses placeholder API calls until backend is ready
 */
export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);

  // Stores list of chat messages (bot + user)
  const [messages, setMessages] = useState([
    {
      role: "bot",
      content: "Hi! I'm your OneSky assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ]);

  // Value inside the chat input text box
  const [inputValue, setInputValue] = useState("");

  // Whether the chatbot is currently processing a message
  const [isLoading, setIsLoading] = useState(false);

  // Reference to the bottom of the messages area
  const messagesEndRef = useRef(null);

  // Reference to the input text box
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  //When chat opens automatically focus the input field
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Handles sending a message to the chatbot
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    
    // Add user message
    const newUserMessage = {
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    // TODO: Replace with actual API call when backend is ready
    // const response = await fetch('/api/chatbot/chat', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   credentials: 'include',
    //   body: JSON.stringify({ message: userMessage }),
    // });
    // const data = await response.json();

    // Placeholder: Simulate API delay and response
    setTimeout(() => {
      const placeholderResponse = generatePlaceholderResponse(userMessage);
      const botMessage = {
        role: "bot",
        content: placeholderResponse,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsLoading(false);
    }, 800);
  };

  // Placeholder response generator (remove when backend is connected)
  const generatePlaceholderResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes("event") || lowerMessage.includes("volunteer")) {
      return "I can help you find volunteer events! Once the backend is connected, I'll search our database for events matching your interests.";
    }
    if (lowerMessage.includes("badge") || lowerMessage.includes("achievement")) {
      return "I can show you your earned badges and achievements. This feature will be available once the backend is connected.";
    }
    if (lowerMessage.includes("impact") || lowerMessage.includes("hours") || lowerMessage.includes("stats")) {
      return "I can share your volunteering impact and statistics. This will work once the backend is connected.";
    }
    if (lowerMessage.includes("team")) {
      return "I can help you with team-related questions. This feature will be available once the backend is connected.";
    }
    return "Thanks for your message! The chatbot backend is not yet connected, but you're seeing how the interface will work.";
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="chatbot-container">
      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-content">
              <div className="chatbot-avatar">
                <img src={logo} alt="OneSky Logo" className="chatbot-logo" />
              </div>
              <div className="chatbot-header-text">
                <h3>OneSky Assistant</h3>
                <p className="chatbot-status">Online</p>
              </div>
            </div>
            <button
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Messages Area */}
          <div className="chatbot-messages">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`chatbot-message chatbot-message--${message.role}`}
              >
                <div className="chatbot-message-content">
                  {message.content}
                </div>
                <span className="chatbot-message-time">
                  {formatTime(message.timestamp)}
                </span>
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message chatbot-message--bot">
                <div className="chatbot-message-content">
                  <span className="chatbot-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form className="chatbot-input-area" onSubmit={handleSendMessage}>
            <input
              ref={inputRef}
              type="text"
              className="chatbot-input"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="chatbot-send"
              disabled={!inputValue.trim() || isLoading}
              aria-label="Send message"
            >
              ➤
            </button>
          </form>
        </div>
      )}

      {/* Toggle Button */}
      <button
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Close chat" : "Open chat"}
        aria-expanded={isOpen}
      >
        {isOpen ? "✕" : "💬"}
      </button>
    </div>
  );
}
