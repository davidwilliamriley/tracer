import { Tag } from 'primereact/tag'
import { cn } from '@/lib/utils'

const VARIANT_CLASSNAMES = {
  default: '',
  secondary: 'p-tag-secondary',
  destructive: 'p-tag-danger',
  outline: 'bg-transparent border border-border text-foreground',
  ghost: 'bg-transparent border border-transparent text-foreground',
  link: 'bg-transparent p-0 text-primary underline',
}

function badgeVariants({ variant = 'default', className } = {}) {
  return cn('text-xs', VARIANT_CLASSNAMES[variant], className)
}

function Badge({
  className,
  variant = 'default',
  asChild: _asChild,
  children,
  ...props
}) {
  return (
    <Tag
      data-slot="badge"
      value={children}
      data-variant={variant}
      className={cn(badgeVariants({ variant, className }))}
      {...props} />
  );
}

export { Badge, badgeVariants }
