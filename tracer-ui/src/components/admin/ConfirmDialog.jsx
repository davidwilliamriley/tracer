import { Dialog } from 'primereact/dialog'
import { Button } from 'primereact/button'

export default function ConfirmDialog({ title, message, confirmLabel = 'Delete', onConfirm, onCancel, isLoading }) {
  const footer = (
    <div className="flex items-center justify-end gap-2">
      <Button
        label="Cancel"
        outlined
        onClick={onCancel}
        disabled={isLoading}
      />
      <Button
        label={isLoading ? 'Deleting...' : confirmLabel}
        severity="danger"
        onClick={onConfirm}
        loading={isLoading}
        disabled={isLoading}
      />
    </div>
  )

  return (
    <Dialog
      visible
      modal
      header={title}
      onHide={onCancel}
      closable={!isLoading}
      closeOnEscape={!isLoading}
      style={{ width: '28rem', maxWidth: '92vw' }}
      footer={footer}
    >
      <p className="text-sm text-muted-foreground">{message}</p>
    </Dialog>
  )
}
