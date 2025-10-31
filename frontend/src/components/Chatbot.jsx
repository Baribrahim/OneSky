import React, { useState, useRef, useEffect } from "react";
import { api, toResult } from "../lib/apiClient";
import "../styles/chatbot.css";
import logo from "../assets/OneSky-logo.png";

/**
 * Chatbot Component
 * Floating chat interface with toggle button in bottom-right corner
 * Uses apiClient for consistent API calls across the project
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

    // Call chatbot API using apiClient
    try {
      const { data, error } = await toResult(
        api.post('/api/chatbot/chat', { message: userMessage })
      );

      if (error) {
        console.error('Chatbot error:', error);
        const errorMessage = {
          role: "bot",
          content: error.message || "Sorry, I'm having trouble connecting right now. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      // Check if response has an error field
      if (data?.error) {
        const errorMessage = {
          role: "bot",
          content: data.error + (data.details ? `: ${data.details}` : ''),
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      const botMessage = {
        role: "bot",
        content: data?.response || "Sorry, I couldn't process that request.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        role: "bot",
        content: "Sorry, I'm having trouble connecting right now. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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
