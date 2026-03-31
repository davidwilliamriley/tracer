import * as React from 'react'
import { Dropdown } from 'primereact/dropdown'

import { cn } from "@/lib/utils"

function toText(node) {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(toText).join('')
  if (React.isValidElement(node)) return toText(node.props?.children)
  return ''
}

function collectItems(children, acc = []) {
  React.Children.forEach(children, (child) => {
    if (!React.isValidElement(child)) return
    if (child.type === SelectItem) {
      acc.push({
        value: child.props.value,
        label: toText(child.props.children),
        disabled: child.props.disabled,
      })
      return
    }
    if (child.props?.children) collectItems(child.props.children, acc)
  })
  return acc
}

function findPlaceholder(children) {
  let value = ''
  React.Children.forEach(children, (child) => {
    if (!React.isValidElement(child) || value) return
    if (child.type === SelectValue && child.props?.placeholder) {
      value = child.props.placeholder
      return
    }
    if (child.props?.children) {
      const nested = findPlaceholder(child.props.children)
      if (nested) value = nested
    }
  })
  return value
}

function findTriggerClassName(children) {
  let className = ''
  React.Children.forEach(children, (child) => {
    if (!React.isValidElement(child) || className) return
    if (child.type === SelectTrigger && child.props?.className) {
      className = child.props.className
      return
    }
    if (child.props?.children) {
      const nested = findTriggerClassName(child.props.children)
      if (nested) className = nested
    }
  })
  return className
}

function Select({
  value,
  onValueChange,
  disabled,
  required,
  children,
  className,
}) {
  const options = React.useMemo(() => collectItems(children), [children])
  const placeholder = findPlaceholder(children) || 'Select...'
  const triggerClassName = findTriggerClassName(children)

  return (
    <Dropdown
      data-slot="select"
      value={value ?? null}
      options={options}
      optionLabel="label"
      optionValue="value"
      onChange={(e) => onValueChange?.(e.value)}
      placeholder={placeholder}
      disabled={disabled}
      required={required}
      className={cn('w-full h-9 text-sm', triggerClassName, className)}
      pt={{
        itemLabel: { className: 'text-sm' },
      }}
    />
  )
}

function SelectGroup({ children }) {
  return <>{children}</>
}

function SelectItem({
  children,
  ...props
}) {
  return <span data-slot="select-item" {...props}>{children}</span>
}

function SelectLabel({ children }) {
  return <span data-slot="select-label">{children}</span>
}

function SelectTrigger({ children }) {
  return <>{children}</>
}

function SelectValue() {
  return null
}

function SelectContent({ children }) {
  return <>{children}</>
}

function SelectSeparator() {
  return null
}

function SelectScrollUpButton() {
  return null
}

function SelectScrollDownButton() {
  return null
}

export {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
}
