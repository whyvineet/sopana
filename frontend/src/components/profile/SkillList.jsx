export default function SkillList({ items }) {
  if (!items?.length) {
    return <p className="text-sm text-gray-400">Nothing recorded yet.</p>
  }

  return (
    <ul className="divide-y divide-gray-100 rounded-xl border border-gray-100">
      {items.map((item) => (
        <li
          key={item.label}
          className="flex items-center justify-between px-4 py-3 text-sm"
        >
          <span className="text-gray-800">{item.label}</span>
          <span className="text-gray-400">{item.level}</span>
        </li>
      ))}
    </ul>
  )
}
