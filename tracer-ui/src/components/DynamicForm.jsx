/**
 * DynamicForm.jsx — renders a form from the API's form schema.
 *
 * React concept — controlled inputs:
 *   Each input's value is controlled by React state (formValues).
 *   When the user types, onChange updates the state, which re-renders
 *   the input with the new value. This is the standard React pattern
 *   for forms — React owns the state, the DOM reflects it.
 *
 * This component receives the form schema from GET /node-types/{id}/form-schema
 * and renders the appropriate input for each field type. On submit it
 * calls POST /nodes/{id}/properties with all values at once.
 */
import { useState, useEffect } from 'react'
import { updateNodeProperties } from '../api/graph'
import { Button } from '@/components/ui/button'

// Map property definition types to appropriate HTML input types
const INPUT_TYPE_MAP = {
  string: 'text',
  integer: 'number',
  float: 'number',
  boolean: 'checkbox',
  date: 'date',
}

function FieldInput({ field, value, onChange }) {
  const inputType = INPUT_TYPE_MAP[field.type] || 'text'

  if (field.type === 'boolean') {
    return (
      <input
        type="checkbox"
        checked={value === 'true' || value === '1'}
        onChange={(e) => onChange(e.target.checked ? 'true' : 'false')}
        className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
      />
    )
  }

  return (
    <input
      type={inputType}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={field.default_value ?? ''}
      step={field.type === 'float' ? 'any' : undefined}
      className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 disabled:bg-gray-50 disabled:text-gray-500"
    />
  )
}

export default function DynamicForm({ schema, existingProperties, nodeId, onSaved }) {
  // Build initial form values from existing property values
  const buildInitialValues = () => {
    const values = {}
    if (schema?.fields) {
      schema.fields.forEach((field) => {
        const existing = existingProperties?.find(
          (p) => p.definition_id === field.definition_id
        )
        values[field.definition_id] = existing?.value ?? field.default_value ?? ''
      })
    }
    return values
  }

  const [formValues, setFormValues] = useState(buildInitialValues)
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState(null)
  const [saveSuccess, setShowSuccess] = useState(false)

  // Re-initialise when the schema or existing properties change
  useEffect(() => {
    setFormValues(buildInitialValues())
    setSaveError(null)
  }, [schema, existingProperties])

  const handleFieldChange = (definitionId, value) => {
    setFormValues((prev) => ({ ...prev, [definitionId]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSaving(true)
    setSaveError(null)
    setShowSuccess(false)

    try {
      const properties = Object.entries(formValues).map(([definition_id, value]) => ({
        definition_id,
        value: value === '' ? null : value,
      }))

      const updated = await updateNodeProperties(nodeId, properties, 'user')
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 2000)
      onSaved?.(updated)
    } catch (err) {
      setSaveError(err.response?.data?.message || 'Save failed')
    } finally {
      setIsSaving(false)
    }
  }

  if (!schema) return null

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {schema.fields.map((field) => (
        <div key={field.definition_id}>
          <label className="flex items-center gap-1.5 text-xs font-medium text-gray-700 mb-1">
            {field.name}
            {field.is_required && (
              <span className="text-red-500 text-[10px]">required</span>
            )}
          </label>

          {field.description && (
            <p className="text-[11px] text-gray-400 mb-1">{field.description}</p>
          )}

          <FieldInput
            field={field}
            value={formValues[field.definition_id]}
            onChange={(val) => handleFieldChange(field.definition_id, val)}
          />
        </div>
      ))}

      {saveError && (
        <div className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {saveError}
        </div>
      )}

      <Button
        type="submit"
        disabled={isSaving}
        loading={isSaving}
        className="w-full"
      >
        {saveSuccess ? 'Saved!' : 'Save changes'}
      </Button>
    </form>
  )
}
