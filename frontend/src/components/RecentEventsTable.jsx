export default function RecentEventsTable({ items = [] }) {
  return (
    <div
      style={{
        marginBottom: "24px",
        background: "#fff",
        padding: "20px",
        borderRadius: "18px",
        border: "1px solid #e5e7eb",
        boxShadow: "0 8px 24px rgba(0,0,0,0.05)",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: "16px" }}>Recent Events</h2>

      <div style={{ overflowX: "auto" }}>
        <table width="100%">
          <thead>
            <tr>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Session</th>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Event Type</th>
              <th style={thStyle}>Category</th>
              <th style={thStyle}>Price</th>
              <th style={thStyle}>Profile</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td style={tdStyle}>{item.id}</td>
                <td style={tdStyle}>{item.session_id}</td>
                <td style={tdStyle}>{item.user_id}</td>
                <td style={tdStyle}>{item.event_type}</td>
                <td style={tdStyle}>{item.category}</td>
                <td style={tdStyle}>{item.price}</td>
                <td style={tdStyle}>{item.profile}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle = {
  textAlign: "left",
  padding: "12px",
  borderBottom: "1px solid #e5e7eb",
  fontSize: "14px",
};

const tdStyle = {
  padding: "12px",
  borderBottom: "1px solid #f1f5f9",
  fontSize: "14px",
};