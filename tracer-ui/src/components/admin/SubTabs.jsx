import { Button } from '@/components/ui/button'

export default function SubTabs({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 px-6 py-2 border-b border-border bg-card shrink-0">
      {tabs.map(({ key, label }) => (
        <Button
          key={key}
          size="xs"
          variant={active === key ? 'default' : 'outline'}
          onClick={() => onChange(key)}
        >
          {label}
        </Button>
      ))}
    </div>
  )
}
