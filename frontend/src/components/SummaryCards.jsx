export default function SummaryCards({ summary }) {
  const cards = [
    { title: "Raw Events", value: summary?.raw_events_count ?? 0 },
    { title: "Session Features", value: summary?.session_features_count ?? 0 },
    { title: "Predictions", value: summary?.predictions_count ?? 0 },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "20px",
        marginBottom: "28px",
      }}
    >
      {cards.map((card) => (
        <div
          key={card.title}
          style={{
            background: "#ffffff",
            borderRadius: "18px",
            padding: "24px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
            border: "1px solid #e5e7eb",
          }}
        >
          <div style={{ fontSize: "16px", fontWeight: 600, color: "#374151", marginBottom: "16px" }}>
            {card.title}
          </div>
          <div style={{ fontSize: "34px", fontWeight: 700, color: "#111827" }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}