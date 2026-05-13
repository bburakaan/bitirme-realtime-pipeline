export default function IntentPredictionCard({ prediction }) {
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
      <h2 style={{ marginTop: 0, marginBottom: "16px" }}>Intent Sample Prediction</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "16px",
        }}
      >
        <div style={boxStyle}>
          <div style={labelStyle}>Predicted Label</div>
          <div style={valueStyle}>{prediction?.predicted_label ?? "-"}</div>
        </div>

        <div style={boxStyle}>
          <div style={labelStyle}>Predicted Revenue</div>
          <div style={valueStyle}>
            {prediction?.predicted_revenue === true
              ? "True"
              : prediction?.predicted_revenue === false
              ? "False"
              : "-"}
          </div>
        </div>

        <div style={boxStyle}>
          <div style={labelStyle}>Probability</div>
          <div style={valueStyle}>
            {prediction?.probability !== undefined && prediction?.probability !== null
              ? Number(prediction.probability).toFixed(4)
              : "-"}
          </div>
        </div>
      </div>
    </div>
  );
}

const boxStyle = {
  background: "#f9fafb",
  border: "1px solid #e5e7eb",
  borderRadius: "14px",
  padding: "18px",
};

const labelStyle = {
  fontSize: "14px",
  color: "#6b7280",
  marginBottom: "8px",
  fontWeight: 600,
};

const valueStyle = {
  fontSize: "28px",
  fontWeight: 700,
  color: "#111827",
};