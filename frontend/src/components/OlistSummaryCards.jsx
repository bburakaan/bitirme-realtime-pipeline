export default function OlistSummaryCards({ summary }) {
  const cards = [
    { title: "Customers", value: summary?.customers_count ?? 0 },
    { title: "Orders", value: summary?.orders_count ?? 0 },
    { title: "Order Items", value: summary?.order_items_count ?? 0 },
    { title: "Payments", value: summary?.payments_count ?? 0 },
    { title: "Products", value: summary?.products_count ?? 0 },
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
          <div
            style={{
              fontSize: "15px",
              fontWeight: 600,
              color: "#374151",
              marginBottom: "10px",
            }}
          >
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