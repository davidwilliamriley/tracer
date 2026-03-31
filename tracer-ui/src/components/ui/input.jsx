import { cn } from "@/lib/utils"
import { InputText } from 'primereact/inputtext'

function Input({
  className,
  type = 'text',
  ...props
}) {
  return (
    <InputText
      type={type}
      data-slot="input"
      className={cn(
        'w-full h-9 text-sm',
        className
      )}
      {...props} />
  );
}

export { Input }
