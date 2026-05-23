export default function Spinner({ fullPage = false, small = false }) {
  const cls = small ? 'spinner spinner-sm' : 'spinner'
  if (fullPage)
    return <div className="spinner-wrap" style={{ minHeight: '60vh' }}><div className={cls} /></div>
  return <div className="spinner-wrap"><div className={cls} /></div>
}
