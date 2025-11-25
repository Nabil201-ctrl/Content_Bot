import React, { useState, useEffect } from 'react';
import { Send, ArrowLeft, Phone, Video, MoreVertical, Paperclip, Smile, Copy, Image, Clock, TrendingUp, Lightbulb } from 'lucide-react';
import axios from 'axios';

export default function MessagePage() {
  const [messages, setMessages] = useState([
    { id: 'system-1', role: 'assistant', text: 'Hi! Tell me about your day and I\'ll suggest social posts and trends. You can also ask for specific posts like "Give me a LinkedIn post" or "Create an Instagram post".' },
  ]);
  const [loading, setLoading] = useState(false);
  const [inputText, setInputText] = useState("");

  const sendMessage = async () => {
    const text = inputText;
    if (!text || !text.trim()) return;
    
    const userMsg = { 
      id: `u-${Date.now()}`, 
      role: 'user', 
      text,
      timestamp: new Date().toISOString()
    };
    setMessages((m) => [...m, userMsg]);
    setInputText("");
    setLoading(true);

    try {
      const resp = await axios.post('/api/chat', { message: text });
      
      const assistantText = resp?.data?.reply;
      const suggestions = resp?.data?.suggestions || [];
      const trends = resp?.data?.trends || [];
      const shouldSuggest = resp?.data?.should_suggest || false;
      
      const assistantMsg = { 
        id: `a-${Date.now()}`, 
        role: 'assistant', 
        text: assistantText,
        suggestions: suggestions,
        trends: trends,
        shouldSuggest: shouldSuggest,
        timestamp: new Date().toISOString()
      };
      
      setMessages((m) => [...m, assistantMsg]);
      
    } catch (err) {
      console.error('chat error', err);
      const errMsg = { 
        id: `a-err-${Date.now()}`, 
        role: 'assistant', 
        text: 'Error contacting server. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages((m) => [...m, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // You could add a toast notification here
      console.log('Copied to clipboard');
    });
  };

  const renderSuggestions = (suggestions) => {
    return suggestions.map((suggestion, index) => (
      <div key={index} className="mt-4 p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-xl border border-purple-500/20 backdrop-blur-sm">
        {/* Platform Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-semibold rounded-full capitalize">
              {suggestion.platform}
            </span>
            <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-medium rounded">
              {suggestion.type}
            </span>
          </div>
          <button
            onClick={() => copyToClipboard(suggestion.content)}
            className="text-slate-400 hover:text-indigo-400 transition-all duration-200"
            title="Copy post content"
          >
            <Copy size={16} />
          </button>
        </div>
        
        {/* Post Content */}
        <div className="mb-4">
          <h4 className="font-semibold text-slate-200 mb-2 text-sm">Post Content:</h4>
          <p className="text-slate-300 bg-slate-800/50 p-3 rounded-lg border border-slate-700 text-sm leading-relaxed">
            {suggestion.content}
          </p>
        </div>
        
        {/* Hashtags */}
        {suggestion.hashtags && suggestion.hashtags.length > 0 && (
          <div className="mb-3">
            <h5 className="font-medium text-slate-300 mb-2 text-sm">Hashtags:</h5>
            <div className="flex flex-wrap gap-1">
              {suggestion.hashtags.map((tag, tagIndex) => (
                <span key={tagIndex} className="px-2 py-1 bg-slate-700/50 text-slate-300 text-xs rounded-lg border border-slate-600">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Insights Grid */}
        <div className="grid grid-cols-1 gap-3 text-sm">
          {/* Why Effective */}
          <div className="flex items-start gap-2">
            <Lightbulb size={16} className="text-yellow-400 mt-0.5 flex-shrink-0" />
            <div>
              <h5 className="font-medium text-slate-300 mb-1">Why This Works:</h5>
              <p className="text-slate-400 text-xs leading-relaxed">{suggestion.why_effective}</p>
            </div>
          </div>
          
          {/* Visual Recommendation */}
          <div className="flex items-start gap-2">
            <Image size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
            <div>
              <h5 className="font-medium text-slate-300 mb-1">Visual Recommendation:</h5>
              <p className="text-slate-400 text-xs leading-relaxed">{suggestion.visual_recommendation}</p>
            </div>
          </div>
          
          {/* Best Time */}
          <div className="flex items-start gap-2">
            <Clock size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
            <div>
              <h5 className="font-medium text-slate-300 mb-1">Best Time to Post:</h5>
              <p className="text-slate-400 text-xs leading-relaxed">{suggestion.best_time}</p>
            </div>
          </div>
          
          {/* Performance Prediction */}
          <div className="flex items-start gap-2">
            <TrendingUp size={16} className="text-purple-400 mt-0.5 flex-shrink-0" />
            <div>
              <h5 className="font-medium text-slate-300 mb-1">Expected Engagement:</h5>
              <p className="text-slate-400 text-xs leading-relaxed">{suggestion.performance_prediction}</p>
            </div>
          </div>
        </div>
        
        {/* Engagement Tips */}
        {suggestion.engagement_tips && suggestion.engagement_tips.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-700/50">
            <h5 className="font-medium text-slate-300 mb-2 text-sm">Engagement Tips:</h5>
            <ul className="space-y-1">
              {suggestion.engagement_tips.map((tip, tipIndex) => (
                <li key={tipIndex} className="flex items-start gap-2 text-xs text-slate-400">
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full mt-1.5 flex-shrink-0" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    ));
  };

  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    
    return (
      <div
        key={message.id}
        className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-[slideIn_0.4s_ease-out] group`}
      >
        <div
          className={`max-w-[85%] rounded-2xl px-4 py-3 backdrop-blur-sm ${
            isUser
              ? 'bg-gradient-to-br from-indigo-500/90 to-purple-600/90 text-white rounded-br-sm shadow-lg shadow-indigo-500/20'
              : 'bg-slate-800/70 text-slate-100 rounded-bl-sm shadow-lg border border-slate-700/50'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
          
          {/* Render suggestions for assistant messages */}
          {!isUser && message.suggestions && message.suggestions.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/20">
              <div className="mb-2">
                <h4 className="font-semibold text-slate-200 text-sm">🎯 Social Media Suggestions</h4>
              </div>
              {renderSuggestions(message.suggestions)}
            </div>
          )}
          
          {/* Timestamp */}
          <div className={`text-xs mt-2 ${isUser ? 'text-indigo-200' : 'text-slate-400'}`}>
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    );
  };

  // Load previous chat history on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await axios.get('/api/chat/history');
        if (cancelled) return;
        if (resp?.data?.history) {
          const history = Array.isArray(resp.data.history) 
            ? resp.data.history 
            : resp.data.history.messages || [];
          setMessages(history);
        }
      } catch (error) {
        console.log('No previous chat history found');
      }
    })();
    return () => (cancelled = true);
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="w-full max-w-2xl h-[80vh] bg-slate-900/80 backdrop-blur-xl rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-slate-700/50">
        {/* Header */}
        <div className="bg-slate-800/60 backdrop-blur-lg px-6 py-4 flex items-center gap-3 border-b border-slate-700/30">
          <button className="text-slate-400 hover:text-slate-200 transition-all duration-200 hover:scale-105">
            <ArrowLeft size={22} />
          </button>
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 via-purple-400 to-pink-400 flex items-center justify-center text-white font-semibold shadow-lg shadow-purple-500/30">
              CB
            </div>
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-800 shadow-lg"></div>
          </div>
          <div className="flex-1">
            <h3 className="text-slate-100 font-semibold text-sm">Content Bot</h3>
            <p className="text-xs text-emerald-400/80 flex items-center gap-1">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              Active now - Ready to create your posts
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button className="text-slate-400 hover:text-slate-200 transition-all duration-200 hover:scale-110" title="Voice call">
              <Phone size={20} />
            </button>
            <button className="text-slate-400 hover:text-slate-200 transition-all duration-200 hover:scale-110" title="Video call">
              <Video size={20} />
            </button>
            <button className="text-slate-400 hover:text-slate-200 transition-all duration-200 hover:scale-110" title="More options">
              <MoreVertical size={20} />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-900/40">
          {messages.map(renderMessage)}

          {/* Enhanced Typing Indicator */}
          {loading && (
            <div className="flex justify-start animate-[slideIn_0.4s_ease-out]">
              <div className="bg-slate-800/70 backdrop-blur-sm rounded-2xl rounded-bl-sm px-5 py-4 shadow-lg border border-slate-700/50">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-slate-400">Creating your content...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-slate-800/60 backdrop-blur-lg px-6 py-4 flex items-center gap-3 border-t border-slate-700/30">
          <button className="text-slate-400 hover:text-indigo-400 transition-all duration-200 hover:scale-110" title="Attach files">
            <Paperclip size={22} />
          </button>
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Tell me about your day or ask for specific posts (LinkedIn, Instagram, Twitter...)"
              className="w-full bg-slate-700/50 text-slate-100 placeholder-slate-400 rounded-2xl px-5 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:bg-slate-700/70 transition-all duration-200 border border-slate-600/50 focus:border-indigo-500/50"
              disabled={loading}
            />
            <button className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-400 transition-all duration-200 hover:scale-110" title="Emoji">
              <Smile size={20} />
            </button>
          </div>
          <button
            onClick={sendMessage}
            disabled={loading || !inputText.trim()}
            className="bg-gradient-to-br from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-2xl p-3 transition-all duration-200 shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed"
            title="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        /* Custom scrollbar */
        .overflow-y-auto::-webkit-scrollbar {
          width: 6px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-track {
          background: rgba(30, 41, 59, 0.3);
          border-radius: 3px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.4);
          border-radius: 3px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb:hover {
          background: rgba(99, 102, 241, 0.6);
        }
      `}</style>
    </div>
  );
}