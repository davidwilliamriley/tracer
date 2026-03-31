import { InputSwitch } from 'primereact/inputswitch'

import { cn } from "@/lib/utils"

function Switch({
  className,
  checked,
  onCheckedChange,
  ...props
}) {
  return (
    <InputSwitch
      checked={Boolean(checked)}
      onChange={(e) => onCheckedChange?.(Boolean(e.value))}
      data-slot="switch"
      className={cn(className)}
      {...props}
    />
  );
}

export { Switch }
