export default function RecentOlistOrdersTable({ items = [] }) {
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
      <h2 style={{ marginTop: 0, marginBottom: "16px" }}>Recent Olist Orders</h2>

      <div style={{ overflowX: "auto" }}>
        <table width="100%">
          <thead>
            <tr>
              <th style={thStyle}>Order ID</th>
              <th style={thStyle}>Customer ID</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Purchase Time</th>
              <th style={thStyle}>Delivered</th>
              <th style={thStyle}>Estimated Delivery</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.order_id}>
                <td style={tdStyle}>{item.order_id}</td>
                <td style={tdStyle}>{item.customer_id}</td>
                <td style={tdStyle}>{item.order_status}</td>
                <td style={tdStyle}>{item.order_purchase_timestamp}</td>
                <td style={tdStyle}>{item.order_delivered_customer_date}</td>
                <td style={tdStyle}>{item.order_estimated_delivery_date}</td>
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