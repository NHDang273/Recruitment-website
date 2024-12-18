import React, { useState, useRef, useEffect } from 'react';
import { FaReact, FaTrash, FaArrowLeft, FaArrowRight } from 'react-icons/fa';
import Logo from '@/assets/logo.svg';
import Full_logo from '@/assets/lego_nen.png';

const ChatbotPage: React.FC = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);
  const [history, setHistory] = useState<string[]>([]);
  const [isHistoryVisible, setIsHistoryVisible] = useState(true);
  const [isElementVisible, setIsElementVisible] = useState(true);
  const [ws, setWs] = useState<WebSocket | null>(null); // Quản lý WebSocket
  const [pdfUrl, setPdfUrl] = useState(null); // PDF Blob URL
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, []);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  // Kết nối WebSocket khi component được mount
  useEffect(() => {
    const websocket = new WebSocket("ws://localhost:8000/api/chat/ws");
    setWs(websocket);

    websocket.onopen = () => {
      console.log("WebSocket connection established.");
    };

    websocket.onmessage = (event) => {
      const data = event.data;
      setMessages((prev) => [...prev, `Bot: ${data}`]);
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    websocket.onclose = () => {
      console.log("WebSocket connection closed.");
    };

    return () => {
      websocket.close();
    };
  }, []);

  const handleSendMessage = () => {
    if (message.trim() !== "" && ws && ws.readyState === WebSocket.OPEN) {
      setMessages([...messages, `You: ${message}`]);
      setIsElementVisible(false);
      setHistory([...history, message]);
      ws.send(message); // Gửi tin nhắn qua WebSocket
      setMessage("");
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setHistory([]);
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  const toggleHistoryVisibility = () => {
    setIsHistoryVisible(!isHistoryVisible);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#fff', color: '#fff', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"' }}>
      {/* Thanh lịch sử tìm kiếm bên trái */}
      <div style={{
        width: isHistoryVisible ? '15%' : '2%',
        backgroundColor: '#e3e3e3',
        padding: '10px',
        // borderRadius: '10px',
        // margin: '10px',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        transition: 'width 0.3s',
      }}>
        <button
          onClick={toggleHistoryVisibility}
          style={{
            backgroundColor: '#222831',
            border: 'none',
            borderRadius: '5px',
            color: '#a7a7a7',
            cursor: 'pointer',
            marginBottom: '10px',
            padding: '10px'
          }}
        >
          {isHistoryVisible ? <FaArrowLeft /> : <FaArrowRight />}
        </button>
        {isHistoryVisible && (
          <>
            <h3 style={{ color: '#222831', alignSelf: 'center' }}>Search History</h3>
            {history.map((item, index) => (
              <div key={index} style={{
                backgroundColor: '#e3e3e3',
                color: '#222831',
                margin: '5px 0',
                padding: '5px 10px',
                borderRadius: '10px',
                maxWidth: '100%',
              }}>
                {item}
              </div>
            ))}
            <button
              onClick={handleClearHistory}
              style={{
                width: '15%',
                marginTop: '10px',
                padding: '10px',
                backgroundColor: '#ff4d4d',
                color: '#fff',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                position: 'absolute',
                bottom: 10,
                fontFamily: 'inherit',
                fontWeight: 'bold',
              }}
              
            >
              Clear All History
            </button>
          </>
        )}
      </div>

      {/* Chat content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{
           flex: 1,
           overflowY: 'auto',
           padding: 'clamp(10px, 2%, 40px)',
           margin: 'clamp(10px, 5%, 40px) clamp(10px, 10%, 150px) 60px',
           borderRadius: 'clamp(5px, 1%, 15px)',
           backgroundColor: '#fff',
           display: 'flex',
           flexDirection: 'column',
        }} ref={chatRef}>

          {isElementVisible && (
            <>
              <img
                src={Full_logo}
                alt="logo"
                style={{ 
                  width: '200px', 
                  height: '200px',
                  margin: '150px auto 0',
                }}
              />

              <div style={{
                margin: '40px auto 0',
                padding: '10px 15px',
                color: '#222831',
                textAlign: 'center',
                fontFamily: 'inherit',
                fontSize: '30px',
              }}>
                Hello, how can I help you?
              </div>
            </>
          )}

          {messages.map((msg, index) => (
            <div key={index} style={{
              margin: '10px 0',
              padding: '10px 15px',
              borderRadius: '10px',
              backgroundColor: msg.startsWith("You:") ? '#e3e3e3' : '#fff',
              color: msg.startsWith("You:") ? '#222831' : '#222831',
              maxWidth: '70%',
              alignSelf: msg.startsWith("You:") ? 'flex-end' : 'flex-start',
              textAlign: 'left',
              display: 'inline-block',
              whiteSpace: 'pre-wrap',
            }}>
              {msg.replace("You:", "").replace("Bot:", "")}
            </div>
          ))}
        </div>

        {/* Input bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '10px',
          position: 'sticky',
          bottom: 0,
        }}>
          {/* <FaReact style={{
            fontSize: '30px',
            marginRight: '10px',
            animation: 'spin 5s infinite linear',
          }} /> */}
          <img
            src={Logo}
            alt="logo"
            style={{ 
              width: '20px', 
              height: '20px', 
              marginRight: '20px',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '50%',
              animation: 'spin 5s infinite linear', 
            }}
          />
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            style={{
              flex: 1,
              maxWidth: '50%',
              padding: '10px 15px',
              borderRadius: '10px',
              border: 'none',
              outline: 'none',
              backgroundColor: '#e3e3e3',
              color: '#222831',
              fontSize: '16px',
            }}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <FaTrash
            onClick={handleClearChat}
            style={{
              fontSize: '20px',
              marginLeft: '20px',
              color: '#ff4d4d',
              cursor: 'pointer',
              transition: 'color 0.3s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#ff0000'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#ff4d4d'}
          />
          <button
            onClick={handleSendMessage}
            style={{
              marginLeft: '20px',
              padding: '10px 20px',
              backgroundColor: '#04BFC6',
              color: '#fff',
              border: 'none',
              borderRadius: '10px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '16px',
            }}
          >
            Send
          </button>
        </div>
      </div>

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default ChatbotPage;
