export default function Badge({ type, label }) {
  return <span className={`badge badge-${type}`}>{label}</span>
}
