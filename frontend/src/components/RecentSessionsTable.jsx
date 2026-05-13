export default function RecentSessionsTable({ items = [] }) {
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
      <h2 style={{ marginTop: 0, marginBottom: "16px" }}>Recent Sessions</h2>

      <div style={{ overflowX: "auto" }}>
        <table width="100%">
          <thead>
            <tr>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Session</th>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Profile</th>
              <th style={thStyle}>Total Events</th>
              <th style={thStyle}>Clicks</th>
              <th style={thStyle}>Add To Cart</th>
              <th style={thStyle}>Actual Label</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td style={tdStyle}>{item.id}</td>
                <td style={tdStyle}>{item.session_id}</td>
                <td style={tdStyle}>{item.user_id}</td>
                <td style={tdStyle}>{item.profile}</td>
                <td style={tdStyle}>{item.total_event_count}</td>
                <td style={tdStyle}>{item.click_count}</td>
                <td style={tdStyle}>{item.add_to_cart_count}</td>
                <td style={tdStyle}>{item.actual_label}</td>
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