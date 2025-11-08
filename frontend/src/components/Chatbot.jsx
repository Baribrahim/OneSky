import React, { useState, useRef, useEffect } from "react";
import { api, toResult } from "../lib/apiClient";
import "../styles/chatbot.css";
import logo from "../assets/OneSky-logo.png";
import EventCard from "./EventCard";
import TeamCard from "./TeamCard";
// Import badge icons
import firstStep from "../assets/badges/firstStep.png";
import eduEnthusiast from "../assets/badges/eduEnthusiast.png";
import volunteerVetran from "../assets/badges/volunteerVetran.png";
import marathonVolunteer from "../assets/badges/marathonVolunteer.png";
import weekendWarrior from "../assets/badges/weekendWarrior.png";
import helpingHand from "../assets/badges/helpingHand.png";
import { io } from "socket.io-client";

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

  // User's joined teams (to determine isMember status)
  const [myTeams, setMyTeams] = useState([]);

  // socket stuff
  const socketRef = useRef(null);
  const [isSocketConnected, setIsSocketConnected] = useState(false);
  // to know which bot message to append streaming chunks to
  const streamingMessageIdRef = useRef(null);

  // Reference to the bottom of the messages area
  const messagesEndRef = useRef(null);

  // Reference to the input text box
  const inputRef = useRef(null);

  // Resize state
  const [windowSize, setWindowSize] = useState({ width: 380, height: 500 });
  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef(null);
  const resizeStartRef = useRef({ x: 0, y: 0, width: 0, height: 0 });

  // Fetch user's teams on mount
  useEffect(() => {
    const fetchMyTeams = async () => {
      try {
        const { data, error } = await toResult(api.get("/api/teams/joined"));
        if (!error && data?.teams) {
          setMyTeams(data.teams);
        }
      } catch (err) {
        console.error("Error fetching user teams:", err);
      }
    };
    fetchMyTeams();
  }, []);

  // init socket
  useEffect(() => {
    // connect to same origin socket.io
    const socket = io("http://localhost:5000", { withCredentials: true });

    socketRef.current = socket;

    socket.on("connect", () => {
      setIsSocketConnected(true);
    });

    socket.on("disconnect", () => {
      setIsSocketConnected(false);
    });

    // main chatbot stream listener
    socket.on("chatbot_response", (payload) => {
      // payload can be:
      // - partial cards: {partial: true, category, events/teams/badges}
      // - stream chunk: {response: "text", stream: true}
      // - done: {done: true, final_text: "..."}
      setMessages((prevMessages) => {
        // we'll construct a new messages array depending on payload
        let newMessages = [...prevMessages];

        // 1) partial result with cards first
        if (payload?.partial) {
          const botMessageId = `bot-${Date.now()}`;
          
          // Check if a message with this ID already exists (shouldn't happen, but safety check)
          const existingIndex = newMessages.findIndex(msg => msg._id === botMessageId);
          if (existingIndex === -1) {
            streamingMessageIdRef.current = botMessageId;

            newMessages.push({
              role: "bot",
              content: "", // text will stream in
              events: payload.events || null,
              teams: payload.teams || null,
              badges: payload.badges || null,
              // team_events currently not rendered separately, but we preserve:
              team_events: payload.team_events || null,
              timestamp: new Date(),
              _id: botMessageId,
            });
          }

          return newMessages;
        }

        // 2) streaming text chunk
        if (payload?.stream && typeof payload.response === "string" && !payload?.done) {
          const currentId = streamingMessageIdRef.current;
          if (!currentId) {
            // no active streaming message, check if last message is a bot message being streamed
            const lastMessage = newMessages[newMessages.length - 1];
            const lastIsStreamingBot = lastMessage && 
              lastMessage.role === "bot" && 
              lastMessage._id &&
              !lastMessage.content; // Empty content means it's waiting for streaming
            
            if (!lastIsStreamingBot) {
              // Create a new message only if the last one isn't already a streaming bot message
              const botMessageId = `bot-${Date.now()}`;
              streamingMessageIdRef.current = botMessageId;
              newMessages.push({
                role: "bot",
                content: payload.response,
                timestamp: new Date(),
                _id: botMessageId,
              });
            } else {
              // Update the existing streaming message
              const lastIndex = newMessages.length - 1;
              newMessages[lastIndex] = {
                ...newMessages[lastIndex],
                content: (newMessages[lastIndex].content || "") + payload.response,
              };
              streamingMessageIdRef.current = lastMessage._id;
            }
            return newMessages;
          }

          // Update existing streaming message
          const messageIndex = newMessages.findIndex(msg => msg._id === currentId);
          if (messageIndex !== -1) {
            newMessages[messageIndex] = {
              ...newMessages[messageIndex],
              content: (newMessages[messageIndex].content || "") + payload.response,
            };
          }
          // If message not found but currentId exists, don't create a new one
          // (wait for the message to be created by partial handler)

          return newMessages;
        }

        // 3) done — stop loader, set final text if provided
        if (payload?.done) {
          setIsLoading(false);
          const currentId = streamingMessageIdRef.current;

          if (currentId) {
            // We have an active streaming message - update it
            const messageIndex = newMessages.findIndex(msg => msg._id === currentId);
            if (messageIndex !== -1) {
              // Update existing streaming message
              const finalText = payload.final_text || newMessages[messageIndex].content || "";
              newMessages[messageIndex] = {
                ...newMessages[messageIndex],
                content: finalText,
              };
              // Remove _id since streaming is done (set to undefined instead of delete for React)
              const updatedMessage = { ...newMessages[messageIndex] };
              delete updatedMessage._id;
              newMessages[messageIndex] = updatedMessage;
            }
            // If message not found but currentId exists, don't create a new one
            // (message might have been removed or there's a state issue)
            streamingMessageIdRef.current = null;
            return newMessages;
          }
          
          // Only create a new message if no currentId and we have content
          if ((payload.final_text || payload.response) && !currentId) {
            // No streaming message exists, create a new one (for general questions only)
            // But first check if the last message is already a bot message with the same content
            const finalText = payload.final_text || payload.response || "";
            const lastMessage = newMessages[newMessages.length - 1];
            const isDuplicate = lastMessage && 
              lastMessage.role === "bot" && 
              lastMessage.content === finalText;
            
            if (!isDuplicate) {
              newMessages.push({
                role: "bot",
                content: finalText,
                events: payload.events || null,
                teams: payload.teams || null,
                badges: payload.badges || null,
                timestamp: new Date(),
              });
            }
          }

          streamingMessageIdRef.current = null;
          return newMessages;
        }

        // 4) non-stream single shot (fallback)
        if (typeof payload?.response === "string" && !payload.stream) {
          newMessages.push({
            role: "bot",
            content: payload.response,
            events: payload.events || null,
            teams: payload.teams || null,
            badges: payload.badges || null,
            timestamp: new Date(),
          });
          setIsLoading(false);
          return newMessages;
        }

        return newMessages;
      });
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  //When chat opens automatically focus the input field
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Resize handlers
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;

      const container = resizeRef.current?.closest('.chatbot-window');
      if (!container) return;

      // Calculate the difference from the start position
      const deltaX = resizeStartRef.current.x - e.clientX;
      const deltaY = resizeStartRef.current.y - e.clientY;

      // Calculate new dimensions (dragging left/up increases size)
      const newWidth = resizeStartRef.current.width + deltaX;
      const newHeight = resizeStartRef.current.height + deltaY;

      // Minimum size constraints
      const minWidth = 300;
      const minHeight = 300;
      const maxWidth = window.innerWidth - 48;
      const maxHeight = window.innerHeight - 100;

      setWindowSize({
        width: Math.max(minWidth, Math.min(maxWidth, newWidth)),
        height: Math.max(minHeight, Math.min(maxHeight, newHeight)),
      });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'nwse-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  // Format message content to preserve paragraphs and line breaks
  const formatMessageContent = (content) => {
    if (!content) return "";

    // Split by double newlines (paragraph breaks)
    const paragraphs = content.split(/\n\n+/).filter((p) => p.trim());

    // If no double newlines, try splitting by single newlines
    if (paragraphs.length === 1 && content.includes("\n")) {
      const lines = content.split("\n").filter((l) => l.trim());
      return lines.map((line, index) => (
        <p key={index} className="chatbot-paragraph">
          {line.trim()}
        </p>
      ));
    }

    return paragraphs.map((paragraph, index) => (
      <p key={index} className="chatbot-paragraph">
        {paragraph.split("\n").map((line, lineIndex, lines) => (
          <React.Fragment key={lineIndex}>
            {line.trim()}
            {lineIndex < lines.length - 1 && <br />}
          </React.Fragment>
        ))}
      </p>
    ));
  };

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

    // Prefer socket if connected
    if (socketRef.current && isSocketConnected) {
      streamingMessageIdRef.current = null;
      socketRef.current.emit("chatbot_message", {
        message: userMessage,
      });
      return;
    }

    // Fallback to HTTP (old behavior)
    try {
      const { data, error } = await toResult(
        api.post("/api/chatbot/chat", { message: userMessage })
      );

      if (error) {
        console.error("Chatbot error:", error);
        const errorMessage = {
          role: "bot",
          content:
            error.message ||
            "Sorry, I'm having trouble connecting right now. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      if (data?.error) {
        const errorMessage = {
          role: "bot",
          content: data.error + (data.details ? `: ${data.details}` : ""),
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      const botMessage = {
        role: "bot",
        content: data?.response || "Sorry, I couldn't process that request.",
        events: data?.events || null, // Include events array if present
        teams: data?.teams || null, // Include teams array if present
        badges: data?.badges || null, // Include badges array if present
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chatbot error:", error);
      const errorMessage = {
        role: "bot",
        content:
          "Sorry, I'm having trouble connecting right now. Please try again.",
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
        <div 
          className="chatbot-window"
          style={{ width: `${windowSize.width}px`, height: `${windowSize.height}px` }}
        >
          {/* Resize Handle */}
          <div
            ref={resizeRef}
            className="chatbot-resize-handle"
            onMouseDown={(e) => {
              e.preventDefault();
              const container = resizeRef.current?.closest('.chatbot-window');
              if (container) {
                const rect = container.getBoundingClientRect();
                resizeStartRef.current = {
                  x: e.clientX,
                  y: e.clientY,
                  width: windowSize.width,
                  height: windowSize.height,
                };
              }
              setIsResizing(true);
            }}
            title="Resize chat window"
          />
          
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-content">
              <div className="chatbot-avatar">
                <img src={logo} alt="OneSky Logo" className="chatbot-logo" />
              </div>
              <div className="chatbot-header-text">
                <h3>OneSky Assistant</h3>
                <p className="chatbot-status">
                  {isSocketConnected ? "Online" : "Connecting..."}
                </p>
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
                {/* Render event cards if events are present */}
                {message.events && message.events.length > 0 && (
                  <div className="chatbot-events-container">
                    {message.events.map((event) => (
                      <div
                        key={event.ID || event.id}
                        className="chatbot-event-card-wrapper"
                      >
                        <EventCard event={event} />
                      </div>
                    ))}
                  </div>
                )}
                {/* Render team cards if teams are present */}
                {message.teams && message.teams.length > 0 && (
                  <div className="chatbot-teams-container">
                    {message.teams.map((team) => {
                      const teamId = team.id || team.ID;
                      const isMember = myTeams.some(
                        (mt) => (mt.id || mt.ID) === teamId
                      );
                      const isOwner = team.is_owner || team.IsOwner || false;
                      return (
                        <div
                          key={teamId}
                          className="chatbot-team-card-wrapper"
                        >
                          <TeamCard
                            team={team}
                            isMember={isMember}
                            isOwner={isOwner}
                            browseEvents={true}
                          />
                        </div>
                      );
                    })}
                  </div>
                )}
                {/* Render badge cards if badges are present */}
                {message.badges && message.badges.length > 0 && (
                  <div className="chatbot-badges-container">
                    {message.badges.map((badge) => {
                      const badgeId = badge.id || badge.ID;
                      const badgeName = badge.Name || badge.name;
                      const badgeDescription =
                        badge.Description || badge.description;

                      // Get badge icon path
                      const getBadgeIconPath = (name) => {
                        const badgeIconMap = {
                          "Event Starter": firstStep,
                          "Event Enthusiast": eduEnthusiast,
                          "First Step": firstStep,
                          "Volunteer Veteran": volunteerVetran,
                          "Marathon Helper": marathonVolunteer,
                          "Weekend Warrior": weekendWarrior,
                          "Marathon Volunteer": marathonVolunteer,
                        };
                        return badgeIconMap[name] || helpingHand;
                      };

                      return (
                        <div
                          key={badgeId}
                          className="chatbot-badge-card-wrapper"
                        >
                          <div className="chatbot-badge-card">
                            <div className="chatbot-badge-icon">
                              <img
                                src={getBadgeIconPath(badgeName)}
                                alt={badgeName}
                                onError={(e) => {
                                  e.target.src = helpingHand;
                                }}
                              />
                            </div>
                            <div className="chatbot-badge-info">
                              <h4 className="chatbot-badge-name">
                                {badgeName}
                              </h4>
                              {badgeDescription && (
                                <p className="chatbot-badge-description">
                                  {badgeDescription}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="chatbot-message-content">
                  {formatMessageContent(message.content)}
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
