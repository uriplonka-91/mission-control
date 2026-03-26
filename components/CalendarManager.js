import React, { useState, useEffect } from 'react';

export default function CalendarManager() {
  const [meetings, setMeetings] = useState([]);
  const [formData, setFormData] = useState({
    subject: '',
    attendees: '',
    start_time: '',
    duration_minutes: 30
  });
  const [selectedMeeting, setSelectedMeeting] = useState(null);

  const password = 'mission2024';

  // Load pending meetings
  const loadMeetings = async () => {
    try {
      const response = await fetch('/api/calendar/pending', {
        headers: { 'X-Password': password }
      });
      const data = await response.json();
      setMeetings(data.pending || []);
    } catch (error) {
      console.error('Error loading meetings:', error);
    }
  };

  useEffect(() => {
    loadMeetings();
    const interval = setInterval(loadMeetings, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Propose meeting
  const handlePropose = async (e) => {
    e.preventDefault();
    
    const attendees = formData.attendees
      .split(',')
      .map(email => email.trim())
      .filter(email => email);
    
    try {
      const response = await fetch('/api/calendar/propose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Password': password
        },
        body: JSON.stringify({
          subject: formData.subject,
          attendees: attendees,
          start_time: formData.start_time,
          duration_minutes: parseInt(formData.duration_minutes)
        })
      });
      
      const result = await response.json();
      
      if (result.status === 'proposed') {
        setSelectedMeeting(result);
        setFormData({
          subject: '',
          attendees: '',
          start_time: '',
          duration_minutes: 30
        });
        loadMeetings();
      }
    } catch (error) {
      console.error('Error proposing meeting:', error);
    }
  };

  // Book meeting
  const handleBook = async (proposalId) => {
    try {
      const response = await fetch('/api/calendar/book', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Password': password
        },
        body: JSON.stringify({ proposal_id: proposalId })
      });
      
      const result = await response.json();
      
      if (result.status === 'booked') {
        setSelectedMeeting(null);
        loadMeetings();
      }
    } catch (error) {
      console.error('Error booking meeting:', error);
    }
  };

  // Cancel meeting
  const handleCancel = async (proposalId) => {
    if (confirm('Are you sure you want to cancel this meeting?')) {
      try {
        const response = await fetch('/api/calendar/cancel', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Password': password
          },
          body: JSON.stringify({ proposal_id: proposalId })
        });
        
        const result = await response.json();
        loadMeetings();
      } catch (error) {
        console.error('Error cancelling meeting:', error);
      }
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Calendar Manager</h2>

      {/* Propose Form */}
      <form onSubmit={handlePropose} className="mb-6 p-4 bg-gray-50 rounded">
        <h3 className="text-lg font-semibold mb-3">Propose Meeting</h3>
        
        <input
          type="text"
          placeholder="Subject"
          value={formData.subject}
          onChange={(e) => setFormData({...formData, subject: e.target.value})}
          className="w-full p-2 border rounded mb-2"
          required
        />
        
        <input
          type="text"
          placeholder="Attendees (email1@example.com, email2@example.com)"
          value={formData.attendees}
          onChange={(e) => setFormData({...formData, attendees: e.target.value})}
          className="w-full p-2 border rounded mb-2"
          required
        />
        
        <input
          type="datetime-local"
          value={formData.start_time}
          onChange={(e) => setFormData({...formData, start_time: e.target.value})}
          className="w-full p-2 border rounded mb-2"
          required
        />
        
        <input
          type="number"
          placeholder="Duration (minutes)"
          value={formData.duration_minutes}
          onChange={(e) => setFormData({...formData, duration_minutes: e.target.value})}
          className="w-full p-2 border rounded mb-2"
          min="15"
          step="15"
        />
        
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Propose Meeting
        </button>
      </form>

      {/* Meeting Preview */}
      {selectedMeeting && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h3 className="text-lg font-semibold mb-2">Review Meeting</h3>
          <pre className="whitespace-pre-wrap text-sm mb-3">{selectedMeeting.preview}</pre>
          
          <div className="flex gap-2">
            <button
              onClick={() => handleBook(selectedMeeting.proposal_id)}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Book
            </button>
            <button
              onClick={() => setSelectedMeeting(null)}
              className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Pending Meetings */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Pending Meetings</h3>
        {meetings.length === 0 ? (
          <p className="text-gray-500">No pending meetings</p>
        ) : (
          <div className="space-y-2">
            {meetings.map((meeting) => (
              <div key={meeting.id} className="p-3 bg-gray-100 rounded">
                <p><strong>Subject:</strong> {meeting.subject}</p>
                <p><strong>Attendees:</strong> {meeting.attendees.join(', ')}</p>
                <p><strong>Time:</strong> {new Date(meeting.start_time).toLocaleString()}</p>
                <p className="text-sm text-gray-600">Created: {new Date(meeting.created_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
