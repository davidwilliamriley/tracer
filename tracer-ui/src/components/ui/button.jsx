import { Button as PrimeButton } from 'primereact/button'
import { cn } from '@/lib/utils'

const VARIANT_CLASSNAMES = {
  default: '',
  destructive: '',
  outline: '',
  secondary: '',
  ghost: 'p-button-text',
  link: 'p-button-link',
}

const SIZE_CLASSNAMES = {
  default: 'h-9 px-4 text-sm',
  xs: 'h-6 px-2 text-xs',
  sm: 'h-8 px-3 text-sm',
  lg: 'h-10 px-6 text-base',
  icon: 'h-9 w-9 p-0',
  'icon-xs': 'h-6 w-6 p-0',
  'icon-sm': 'h-8 w-8 p-0',
  'icon-lg': 'h-10 w-10 p-0',
}

function buttonVariants({ variant = 'default', size = 'default', className } = {}) {
  return cn(
    'inline-flex items-center justify-center gap-2 font-medium',
    VARIANT_CLASSNAMES[variant],
    SIZE_CLASSNAMES[size],
    className
  )
}

function variantProps(variant) {
  if (variant === 'destructive') return { severity: 'danger' }
  if (variant === 'outline') return { outlined: true }
  if (variant === 'secondary') return { severity: 'secondary' }
  if (variant === 'ghost') return { text: true }
  if (variant === 'link') return { link: true }
  return {}
}

function Button({
  className,
  variant = 'default',
  size = 'default',
  asChild: _asChild,
  ...props
}) {
  return (
    <PrimeButton
      data-slot="button"
      data-variant={variant}
      data-size={size}
      {...variantProps(variant)}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props} />
  );
}

export { Button, buttonVariants }
