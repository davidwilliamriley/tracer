/**
 * PropertyDefinitions.jsx — manage node and edge property definitions.
 * Two tabs: one for node properties, one for edge properties.
 */
import { useState, useEffect } from 'react'
import DataTable from '../../components/admin/DataTable'
import Modal from '../../components/admin/Modal'
import ConfirmDialog from '../../components/admin/ConfirmDialog'
import FormField, { TextInput, TextArea, SelectInput } from '../../components/admin/FormField'
import {
  getNodePropertyDefinitions,
  createNodePropertyDefinition,
  updateNodePropertyDefinition,
  deleteNodePropertyDefinition,
  getEdgePropertyDefinitions,
  createEdgePropertyDefinition,
  updateEdgePropertyDefinition,
  deleteEdgePropertyDefinition,
} from '../../api/admin'

const PROPERTY_TYPES = [
  { value: 'string',  label: 'String'  },
  { value: 'integer', label: 'Integer' },
  { value: 'float',   label: 'Float'   },
  { value: 'boolean', label: 'Boolean' },
  { value: 'date',    label: 'Date'    },
]

const COLUMNS = (prefix) => [
  { key: `${prefix}_identifier`, label: 'Identifier' },
  { key: `${prefix}_name`,       label: 'Name' },
  { key: `${prefix}_type`,       label: 'Type',
    render: (row) => (
      <span className="inline-block text-[10px] font-medium px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 border border-gray-200">
        {row[`${prefix}_type`]}
      </span>
    )},
  { key: `${prefix}_default_value`, label: 'Default',
    render: (row) => row[`${prefix}_default_value`] || <span className="text-gray-300">—</span> },
]

function PropDefForm({ prefix, initial, onSubmit, isLoading, error }) {
  const [identifier, setIdentifier] = useState(initial?.[`${prefix}_identifier`] ?? '')
  const [name, setName]             = useState(initial?.[`${prefix}_name`] ?? '')
  const [description, setDescription] = useState(initial?.[`${prefix}_description`] ?? '')
  const [type, setType]             = useState(initial?.[`${prefix}_type`] ?? 'string')
  const [defaultValue, setDefaultValue] = useState(initial?.[`${prefix}_default_value`] ?? '')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      [`${prefix}_identifier`]:    identifier,
      [`${prefix}_name`]:          name,
      [`${prefix}_description`]:   description,
      [`${prefix}_type`]:          type,
      [`${prefix}_default_value`]: defaultValue || null,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <FormField label="Identifier" required hint="Unique code — cannot be changed after creation">
        <TextInput value={identifier} onChange={setIdentifier} placeholder="SEVERITY" required disabled={!!initial} />
      </FormField>
      <FormField label="Name" required>
        <TextInput value={name} onChange={setName} placeholder="Severity" required />
      </FormField>
      <FormField label="Description">
        <TextArea value={description} onChange={setDescription} placeholder="Optional description" />
      </FormField>
      <FormField label="Type" required hint="Values will be validated against this type when saved">
        <SelectInput value={type} onChange={setType} options={PROPERTY_TYPES} required />
      </FormField>
      <FormField label="Default value" hint="Used when no value is provided (optional)">
        <TextInput value={defaultValue} onChange={setDefaultValue} placeholder={type === 'boolean' ? 'true or false' : ''} />
      </FormField>
      {error && (
        <div className="mb-4 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</div>
      )}
      <button type="submit" disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {isLoading ? 'Saving…' : initial ? 'Save changes' : 'Create definition'}
      </button>
    </form>
  )
}

function PropDefTab({ prefix, getFn, createFn, updateFn, deleteFn, label }) {
  const [rows, setRows]           = useState([])
  const [isLoading, setLoading]   = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [editTarget, setEditTarget] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [formLoading, setFormLoading] = useState(false)
  const [formError, setFormError]   = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const load = async () => {
    setLoading(true); setLoadError(null)
    try { setRows(await getFn()) }
    catch (e) { setLoadError(e.response?.data?.message || 'Failed to load') }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (payload) => {
    setFormLoading(true); setFormError(null)
    try { await createFn(payload); setCreateOpen(false); load() }
    catch (e) { setFormError(e.response?.data?.message || 'Create failed') }
    finally { setFormLoading(false) }
  }

  const handleEdit = async (payload) => {
    setFormLoading(true); setFormError(null)
    try { await updateFn(editTarget.id, payload); setEditTarget(null); load() }
    catch (e) { setFormError(e.response?.data?.message || 'Update failed') }
    finally { setFormLoading(false) }
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    try { await deleteFn(deleteTarget.id); setDeleteTarget(null); load() }
    catch (e) { alert(e.response?.data?.message || 'Delete failed') }
    finally { setDeleteLoading(false) }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex justify-end px-6 py-3 border-b border-gray-100 shrink-0">
        <button onClick={() => { setCreateOpen(true); setFormError(null) }}
          className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          + New definition
        </button>
      </div>
      <div className="flex-1 overflow-auto bg-white">
        <DataTable
          columns={COLUMNS(prefix)} rows={rows} isLoading={isLoading} error={loadError}
          emptyMessage={`No ${label} property definitions yet`}
          actions={(row) => (
            <div className="flex gap-2 justify-end">
              <button onClick={() => { setEditTarget(row); setFormError(null) }} className="text-xs text-blue-600 hover:underline">Edit</button>
              <button onClick={() => setDeleteTarget(row)} className="text-xs text-red-500 hover:underline">Delete</button>
            </div>
          )}
        />
      </div>
      {createOpen && <Modal title={`New ${label} property`} onClose={() => setCreateOpen(false)}><PropDefForm prefix={prefix} onSubmit={handleCreate} isLoading={formLoading} error={formError} /></Modal>}
      {editTarget && <Modal title={`Edit ${label} property`} onClose={() => setEditTarget(null)}><PropDefForm prefix={prefix} initial={editTarget} onSubmit={handleEdit} isLoading={formLoading} error={formError} /></Modal>}
      {deleteTarget && <ConfirmDialog title="Delete property definition" message={`Delete "${deleteTarget[`${prefix}_name`]}"? This will fail if it is assigned to any types.`} onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} isLoading={deleteLoading} />}
    </div>
  )
}

export default function PropertyDefinitions() {
  const [tab, setTab] = useState('node')

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="bg-white border-b border-gray-200 px-6 py-4 shrink-0">
        <h1 className="text-base font-semibold text-gray-900">Property definitions</h1>
        <p className="text-xs text-gray-400 mt-0.5">Define reusable property fields that can be assigned to node and edge types</p>
        <div className="flex gap-1 mt-4">
          {[['node', 'Node properties'], ['edge', 'Edge properties']].map(([key, label]) => (
            <button key={key} onClick={() => setTab(key)}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${tab === key ? 'bg-gray-900 text-white border-gray-900' : 'text-gray-600 border-gray-200 hover:border-gray-300'}`}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'node' && (
        <PropDefTab prefix="node_property_definition" label="node"
          getFn={getNodePropertyDefinitions} createFn={createNodePropertyDefinition}
          updateFn={updateNodePropertyDefinition} deleteFn={deleteNodePropertyDefinition} />
      )}
      {tab === 'edge' && (
        <PropDefTab prefix="edge_property_definition" label="edge"
          getFn={getEdgePropertyDefinitions} createFn={createEdgePropertyDefinition}
          updateFn={updateEdgePropertyDefinition} deleteFn={deleteEdgePropertyDefinition} />
      )}
    </div>
  )
}
