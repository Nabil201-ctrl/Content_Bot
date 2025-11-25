import React, { useState } from 'react';

export default function MessageInput({ onSend, disabled = false }) {
  const [text, setText] = useState('');

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <form onSubmit={submit} className="mt-4 flex gap-2 items-center">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Write about your day... (or ask for post ideas)"
        className="flex-1 border rounded px-3 py-2"
        disabled={disabled}
      />
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        disabled={disabled || !text.trim()}
      >
        Send
      </button>
    </form>
  );
}
