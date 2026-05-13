export default function IntentModelCards({ metrics }) {
  const cards = [
    { title: "Dataset Rows", value: metrics?.rows ?? 0 },
    { title: "Accuracy", value: metrics?.accuracy ? Number(metrics.accuracy).toFixed(4) : "0.0000" },
    { title: "Precision", value: metrics?.precision ? Number(metrics.precision).toFixed(4) : "0.0000" },
    { title: "Recall", value: metrics?.recall ? Number(metrics.recall).toFixed(4) : "0.0000" },
    { title: "F1 Score", value: metrics?.f1_score ? Number(metrics.f1_score).toFixed(4) : "0.0000" },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(5, 1fr)",
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
            padding: "20px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
            border: "1px solid #e5e7eb",
          }}
        >
          <div style={{ fontSize: "15px", fontWeight: 600, color: "#374151", marginBottom: "10px" }}>
            {card.title}
          </div>
          <div style={{ fontSize: "28px", fontWeight: 700, color: "#111827" }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}