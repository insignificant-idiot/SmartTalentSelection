export default function Card({ children, className = "" }) {
  return (
    <div
      className={`bg-gray-800 rounded-lg border border-gray-700 p-5 shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}
