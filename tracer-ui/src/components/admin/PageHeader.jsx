export default function PageHeader({ title, description, action }) {
  return (
    <div className="bg-card border-b border-border px-6 py-4 flex items-center justify-between shrink-0">
      <div>
        <h1 className="text-sm font-semibold text-foreground">{title}</h1>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      {action}
    </div>
  )
}
