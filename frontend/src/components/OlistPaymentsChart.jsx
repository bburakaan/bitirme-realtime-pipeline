import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];

export default function OlistPaymentsChart({ items = [] }) {
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
      <h2 style={{ marginTop: 0, marginBottom: "16px" }}>Olist Payment Types</h2>

      <div style={{ width: "100%", height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={items}
              dataKey="count"
              nameKey="payment_type"
              cx="50%"
              cy="50%"
              outerRadius={110}
              label
            >
              {items.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}