import { useCallback, useEffect, useRef, useState } from 'react'

export interface Note {
  id: string
  title: string
  content: string
  date: string
  updatedAt: string
}

interface StoredNotebook {
  version: 1
  notes: Note[]
  activeId: string
}

// Keep the existing key so renaming the app preserves previously saved notes.
const STORAGE_KEY = 'manman-notebook:v1'

export function today() {
  return new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date())
}

export function makeNote(): Note {
  return {
    id: crypto.randomUUID(), title: '', content: '', date: today(),
    updatedAt: new Date().toISOString(),
  }
}

export function formatDate(date: string) {
  const [year, month, day] = date.split('-')
  return `${year} 年 ${Number(month)} 月 ${Number(day)} 日`
}

function isNote(value: unknown): value is Note {
  if (!value || typeof value !== 'object') return false
  const n = value as Record<string, unknown>
  return typeof n.id === 'string' && typeof n.title === 'string' &&
    typeof n.content === 'string' && typeof n.updatedAt === 'string' &&
    typeof n.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(n.date)
}

function readNotebook(): { data: StoredNotebook; error: string } {
  const note = makeNote()
  const blank: StoredNotebook = { version: 1, notes: [note], activeId: note.id }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { data: blank, error: '' }
    const parsed: unknown = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') throw new Error('Invalid notebook')
    const data = parsed as Partial<StoredNotebook>
    if (data.version !== 1 || !Array.isArray(data.notes) || !data.notes.length ||
      !data.notes.every(isNote) || new Set(data.notes.map(n => n.id)).size !== data.notes.length) {
      throw new Error('Invalid notebook')
    }
    return {
      data: { version: 1, notes: data.notes, activeId: data.notes.some(n => n.id === data.activeId) ? data.activeId! : data.notes[0].id },
      error: '',
    }
  } catch {
    return { data: blank, error: '无法读取已有笔记，已暂停自动保存。你仍可书写并导出文本，原有数据不会被覆盖。' }
  }
}

export function useNotebook() {
  const [initial] = useState(readNotebook)
  const [notes, setNotes] = useState(initial.data.notes)
  const [activeId, setActiveId] = useState(initial.data.activeId)
  const [saveState, setSaveState] = useState<'saved' | 'saving' | 'error'>(initial.error ? 'error' : 'saved')
  const [error, setError] = useState(initial.error)
  const dataRef = useRef({ notes, activeId })
  dataRef.current = { notes, activeId }

  const saveNow = useCallback(() => {
    if (initial.error) return
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, ...dataRef.current }))
      setSaveState('saved')
      setError('')
    } catch {
      setSaveState('error')
      setError('暂时无法保存到浏览器。请先导出文本，避免关闭页面后丢失内容。')
    }
  }, [initial.error])

  useEffect(() => {
    if (initial.error) return
    setSaveState('saving')
    const timer = window.setTimeout(saveNow, 350)
    return () => window.clearTimeout(timer)
  }, [notes, activeId, initial.error, saveNow])

  useEffect(() => {
    const onHide = () => { if (document.visibilityState === 'hidden') saveNow() }
    window.addEventListener('pagehide', saveNow)
    document.addEventListener('visibilitychange', onHide)
    return () => {
      window.removeEventListener('pagehide', saveNow)
      document.removeEventListener('visibilitychange', onHide)
    }
  }, [saveNow])

  const activeNote = notes.find(n => n.id === activeId) ?? notes[0]

  const updateNote = (patch: Partial<Pick<Note, 'title' | 'content'>>) => {
    setNotes(list => list.map(n => n.id === activeNote.id ? { ...n, ...patch, updatedAt: new Date().toISOString() } : n))
  }

  const newNote = () => {
    const note = makeNote()
    setNotes(list => [note, ...list])
    setActiveId(note.id)
  }

  const deleteNote = () => {
    const remaining = notes.filter(n => n.id !== activeNote.id)
    const next = remaining.length ? remaining : [makeNote()]
    setNotes(next)
    setActiveId(next[0].id)
  }

  const exportNote = () => {
    const title = activeNote.title.trim() || '无题之页'
    const blob = new Blob([`${title}\n${formatDate(activeNote.date)}\n\n${activeNote.content}\n`], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${activeNote.date}-${title.replace(/[\\/:*?"<>|\u0000-\u001f]/g, '-').slice(0, 60)}.txt`
    anchor.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  return { notes, activeNote, activeId, setActiveId, saveState, error, updateNote, newNote, deleteNote, exportNote, saveNow }
}
