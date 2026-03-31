import { Dialog } from 'primereact/dialog'

export default function Modal({ title, onClose, children }) {
  return (
    <Dialog
      visible
      modal
      header={title}
      onHide={onClose}
      style={{ width: '36rem', maxWidth: '95vw' }}
      contentClassName="max-h-[90vh] overflow-y-auto"
    >
      {children}
    </Dialog>
  )
}
