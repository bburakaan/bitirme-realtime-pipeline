export default function RecentPredictionsTable({ items = [] }) {
  return (
    <div style={{ marginBottom: "24px", background: "#fff", padding: "16px", borderRadius: "12px", border: "1px solid #ddd" }}>
      <h2>Recent Predictions</h2>
      <table border="1" cellPadding="8" cellSpacing="0" width="100%">
        <thead>
          <tr>
            <th>ID</th>
            <th>Session</th>
            <th>User</th>
            <th>Actual</th>
            <th>Predicted</th>
            <th>Probability</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.session_id}</td>
              <td>{item.user_id}</td>
              <td>{item.actual_label}</td>
              <td>{item.predicted_label}</td>
              <td>{item.probability}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}