import React, { useRef, useEffect } from 'react';

export default function ChatWindow({ messages = [], loading = false }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="bg-white rounded shadow p-4 h-[60vh] overflow-auto">
      <ul className="space-y-4">
        {messages.map((m) => (
          <li key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] px-4 py-2 rounded-lg ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
              <div className="whitespace-pre-wrap">{m.text}</div>
              <div className="text-xs text-gray-400 mt-1">{m.role}</div>
            </div>
          </li>
        ))}
        {loading && (
          <li className="flex justify-start">
            <div className="max-w-[80%] px-4 py-2 rounded-lg bg-gray-100 text-gray-900">Thinking...</div>
          </li>
        )}
      </ul>
      <div ref={endRef} />
    </div>
  );
}
