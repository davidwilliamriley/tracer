import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'

export default function FormField({ label, required, hint, error, children }) {
  return (
    <div className="mb-4">
      <label className="flex items-center gap-1.5 text-xs font-medium text-foreground mb-1">
        {label}
        {required && <span className="text-destructive text-[10px]">required</span>}
      </label>
      {hint && <p className="text-[11px] text-muted-foreground mb-1">{hint}</p>}
      {children}
      {error && <p className="text-[11px] text-destructive mt-1">{error}</p>}
    </div>
  )
}

export function TextInput({ value, onChange, placeholder, required, disabled }) {
  return (
    <Input
      type="text"
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
      disabled={disabled}
      className="text-sm"
    />
  )
}

export function TextArea({ value, onChange, placeholder, rows = 3 }) {
  return (
    <Textarea
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={rows}
      className="text-sm resize-none"
    />
  )
}

export function SelectInput({ value, onChange, options, required }) {
  return (
    <Select value={value ?? ''} onValueChange={onChange} required={required}>
      <SelectTrigger className="text-sm">
        <SelectValue placeholder="Select…" />
      </SelectTrigger>
      <SelectContent>
        {options.map((opt) => (
          <SelectItem key={opt.value} value={opt.value}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function Toggle({ checked, onChange, label }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <Switch checked={checked} onCheckedChange={onChange} />
      {label && <span className="text-xs text-foreground">{label}</span>}
    </label>
  )
}
