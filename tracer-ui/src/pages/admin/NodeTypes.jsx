/**
 * NodeTypes.jsx — admin page for managing NodeTypes.
 *
 * Pattern used across all admin list pages:
 *   1. Fetch list on mount with useEffect
 *   2. Local state controls which modal is open (create / edit / delete)
 *   3. After any mutation (create/edit/delete), re-fetch the list
 *   4. Errors from the API are shown inline in the modal or table
 */
import { useState, useEffect } from 'react'
import DataTable from '../../components/admin/DataTable'
import Modal from '../../components/admin/Modal'
import ConfirmDialog from '../../components/admin/ConfirmDialog'
import FormField, { TextInput, TextArea } from '../../components/admin/FormField'
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
    render: (row) => row.node_type_description || <span className="text-gray-300">—</span> },
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
          disabled={!!initial}  // identifier is immutable after creation
        />
      </FormField>
      <FormField label="Name" required>
        <TextInput value={name} onChange={setName} placeholder="Safety Requirement" required />
      </FormField>
      <FormField label="Description">
        <TextArea value={description} onChange={setDescription} placeholder="Optional description" />
      </FormField>

      {error && (
        <div className="mb-4 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium
                   hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {isLoading ? 'Saving…' : initial ? 'Save changes' : 'Create node type'}
      </button>
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
      {/* Page header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-base font-semibold text-gray-900">Node types</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Define the types of nodes that can exist in your graph
          </p>
        </div>
        <button
          onClick={() => { setCreateOpen(true); setFormError(null) }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium
                     hover:bg-blue-700 transition-colors"
        >
          + New node type
        </button>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto bg-white">
        <DataTable
          columns={COLUMNS}
          rows={rows}
          isLoading={isLoading}
          error={loadError}
          emptyMessage="No node types yet — create your first one"
          actions={(row) => (
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => { setEditTarget(row); setFormError(null) }}
                className="text-xs text-blue-600 hover:underline"
              >
                Edit
              </button>
              <button
                onClick={() => setDeleteTarget(row)}
                className="text-xs text-red-500 hover:underline"
              >
                Delete
              </button>
            </div>
          )}
        />
      </div>

      {/* Create modal */}
      {createOpen && (
        <Modal title="New node type" onClose={() => setCreateOpen(false)}>
          <NodeTypeForm onSubmit={handleCreate} isLoading={formLoading} error={formError} />
        </Modal>
      )}

      {/* Edit modal */}
      {editTarget && (
        <Modal title="Edit node type" onClose={() => setEditTarget(null)}>
          <NodeTypeForm initial={editTarget} onSubmit={handleEdit} isLoading={formLoading} error={formError} />
        </Modal>
      )}

      {/* Delete confirmation */}
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
