import { RiErrorWarningLine, RiCheckboxCircleLine, RiInformationLine } from 'react-icons/ri'

const icons = { error: RiErrorWarningLine, success: RiCheckboxCircleLine, info: RiInformationLine, warn: RiErrorWarningLine }

export default function Alert({ type = 'error', message, onClose }) {
  if (!message) return null
  const Icon = icons[type] || RiErrorWarningLine
  return (
    <div className={`alert alert-${type}`}>
      <Icon style={{ fontSize: 16, flexShrink: 0, marginTop: 1 }} />
      <span style={{ flex: 1 }}>{typeof message === 'object' ? JSON.stringify(message) : message}</span>
      {onClose && <button onClick={onClose} style={{ opacity: .6, fontSize: 16, lineHeight: 1 }}>✕</button>}
    </div>
  )
}
