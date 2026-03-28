import { useState, useEffect } from 'react'
import DataTable from '../../components/admin/DataTable'
import Modal from '../../components/admin/Modal'
import ConfirmDialog from '../../components/admin/ConfirmDialog'
import FormField, { TextInput, TextArea } from '../../components/admin/FormField'
import PageHeader from '../../components/admin/PageHeader'
import { Button } from '@/components/ui/button'
import {
  getNodeTypes,
  createNodeType,
  updateNodeType,
  deleteNodeType,
} from '../../api/admin'

const COLUMNS = [
  { key: 'node_type_identifier', label: 'Identifier' },
  { key: 'node_type_name',       label: 'Name' },
  { key: 'node_type_description', label: 'Description',
    render: (row) => row.node_type_description || <span className="text-muted-foreground">—</span> },
  { key: 'created_on', label: 'Created',
    render: (row) => row.created_on?.slice(0, 10) },
]

function NodeTypeForm({ initial, onSubmit, isLoading, error }) {
  const [identifier, setIdentifier] = useState(initial?.node_type_identifier ?? '')
  const [name, setName]             = useState(initial?.node_type_name ?? '')
  const [description, setDescription] = useState(initial?.node_type_description ?? '')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ node_type_identifier: identifier, node_type_name: name, node_type_description: description })
  }

  return (
    <form onSubmit={handleSubmit}>
      <FormField label="Identifier" required hint="Unique code e.g. SAFETY_REQUIREMENT — cannot be changed after creation">
        <TextInput
          value={identifier}
          onChange={setIdentifier}
          placeholder="SAFETY_REQUIREMENT"
          required
          disabled={!!initial}
        />
      </FormField>
      <FormField label="Name" required>
        <TextInput value={name} onChange={setName} placeholder="Safety Requirement" required />
      </FormField>
      <FormField label="Description">
        <TextArea value={description} onChange={setDescription} placeholder="Optional description" />
      </FormField>

      {error && (
        <div className="mb-4 text-xs text-destructive bg-destructive/10 border border-destructive/30 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? 'Saving…' : initial ? 'Save changes' : 'Create node type'}
      </Button>
    </form>
  )
}

export default function NodeTypes() {
  const [rows, setRows]         = useState([])
  const [isLoading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [editTarget, setEditTarget] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [formLoading, setFormLoading] = useState(false)
  const [formError, setFormError] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    setLoadError(null)
    try {
      setRows(await getNodeTypes())
    } catch (e) {
      setLoadError(e.response?.data?.message || 'Failed to load')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (payload) => {
    setFormLoading(true)
    setFormError(null)
    try {
      await createNodeType(payload)
      setCreateOpen(false)
      load()
    } catch (e) {
      setFormError(e.response?.data?.message || 'Create failed')
    } finally {
      setFormLoading(false)
    }
  }

  const handleEdit = async (payload) => {
    setFormLoading(true)
    setFormError(null)
    try {
      await updateNodeType(editTarget.id, {
        node_type_name: payload.node_type_name,
        node_type_description: payload.node_type_description,
      })
      setEditTarget(null)
      load()
    } catch (e) {
      setFormError(e.response?.data?.message || 'Update failed')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    try {
      await deleteNodeType(deleteTarget.id)
      setDeleteTarget(null)
      load()
    } catch (e) {
      alert(e.response?.data?.message || 'Delete failed')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <PageHeader
        title="Node types"
        description="Define the types of nodes that can exist in your graph"
        action={
          <Button size="sm" onClick={() => { setCreateOpen(true); setFormError(null) }}>
            + New node type
          </Button>
        }
      />

      <div className="flex-1 overflow-auto bg-card">
        <DataTable
          columns={COLUMNS}
          rows={rows}
          isLoading={isLoading}
          error={loadError}
          emptyMessage="No node types yet — create your first one"
          actions={(row) => (
            <div className="flex gap-2 justify-end">
              <Button variant="ghost" size="xs" onClick={() => { setEditTarget(row); setFormError(null) }}>
                Edit
              </Button>
              <Button variant="ghost" size="xs" className="text-destructive hover:text-destructive" onClick={() => setDeleteTarget(row)}>
                Delete
              </Button>
            </div>
          )}
        />
      </div>

      {createOpen && (
        <Modal title="New node type" onClose={() => setCreateOpen(false)}>
          <NodeTypeForm onSubmit={handleCreate} isLoading={formLoading} error={formError} />
        </Modal>
      )}

      {editTarget && (
        <Modal title="Edit node type" onClose={() => setEditTarget(null)}>
          <NodeTypeForm initial={editTarget} onSubmit={handleEdit} isLoading={formLoading} error={formError} />
        </Modal>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete node type"
          message={`Delete "${deleteTarget.node_type_name}"? This will fail if any nodes use this type.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={deleteLoading}
        />
      )}
    </div>
  )
}
