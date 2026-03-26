import React, { useState, useEffect } from 'react';

export default function EmailManager() {
  const [emails, setEmails] = useState([]);
  const [drafting, setDrafting] = useState(false);
  const [formData, setFormData] = useState({
    to: '',
    subject: '',
    body: ''
  });
  const [selectedDraft, setSelectedDraft] = useState(null);

  const password = 'mission2024';

  // Load pending emails
  const loadEmails = async () => {
    try {
      const response = await fetch('/api/email/pending', {
        headers: { 'X-Password': password }
      });
      const data = await response.json();
      setEmails(data.pending || []);
    } catch (error) {
      console.error('Error loading emails:', error);
    }
  };

  useEffect(() => {
    loadEmails();
    const interval = setInterval(loadEmails, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Draft email
  const handleDraft = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/email/draft', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Password': password
        },
        body: JSON.stringify(formData)
      });
      
      const result = await response.json();
      
      if (result.status === 'drafted') {
        setSelectedDraft(result);
        setFormData({ to: '', subject: '', body: '' });
        loadEmails();
      }
    } catch (error) {
      console.error('Error drafting email:', error);
    }
  };

  // Send email
  const handleSend = async (draftId) => {
    try {
      const response = await fetch('/api/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Password': password
        },
        body: JSON.stringify({ draft_id: draftId })
      });
      
      const result = await response.json();
      
      if (result.status === 'sent') {
        setSelectedDraft(null);
        loadEmails();
      }
    } catch (error) {
      console.error('Error sending email:', error);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Email Manager</h2>

      {/* Draft Form */}
      <form onSubmit={handleDraft} className="mb-6 p-4 bg-gray-50 rounded">
        <h3 className="text-lg font-semibold mb-3">Draft Email</h3>
        
        <input
          type="email"
          placeholder="To"
          value={formData.to}
          onChange={(e) => setFormData({...formData, to: e.target.value})}
          className="w-full p-2 border rounded mb-2"
          required
        />
        
        <input
          type="text"
          placeholder="Subject"
          value={formData.subject}
          onChange={(e) => setFormData({...formData, subject: e.target.value})}
          className="w-full p-2 border rounded mb-2"
          required
        />
        
        <textarea
          placeholder="Body"
          value={formData.body}
          onChange={(e) => setFormData({...formData, body: e.target.value})}
          className="w-full p-2 border rounded mb-2 h-24"
          required
        />
        
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Draft Email
        </button>
      </form>

      {/* Draft Preview */}
      {selectedDraft && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h3 className="text-lg font-semibold mb-2">Review Draft</h3>
          <pre className="whitespace-pre-wrap text-sm mb-3">{selectedDraft.preview}</pre>
          
          <div className="flex gap-2">
            <button
              onClick={() => handleSend(selectedDraft.draft_id)}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Send
            </button>
            <button
              onClick={() => setSelectedDraft(null)}
              className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Pending Emails */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Pending Emails</h3>
        {emails.length === 0 ? (
          <p className="text-gray-500">No pending emails</p>
        ) : (
          <div className="space-y-2">
            {emails.map((email) => (
              <div key={email.id} className="p-3 bg-gray-100 rounded">
                <p><strong>To:</strong> {email.to}</p>
                <p><strong>Subject:</strong> {email.subject}</p>
                <p className="text-sm text-gray-600">Created: {new Date(email.created_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
