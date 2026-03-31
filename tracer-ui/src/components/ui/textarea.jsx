import { cn } from "@/lib/utils"
import { InputTextarea } from 'primereact/inputtextarea'

function Textarea({
  className,
  ...props
}) {
  return (
    <InputTextarea
      data-slot="textarea"
      className={cn(
        'w-full text-sm',
        className
      )}
      {...props} />
  );
}

export { Textarea }
