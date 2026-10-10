import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowRight, ArrowUpRight, BookOpen, Check, CheckCheck, ChevronDown, ChevronRight, Download, Feather, FileText, LockKeyhole, Moon, Plus, Search, Trash2, X } from 'lucide-react'
import { formatDate, today, useNotebook } from './notebook'
import { ruleFilters, rules } from './rules'

type Page = 'cover' | 'rules' | 'notebook'
type NotebookState = ReturnType<typeof useNotebook>
const background = `${import.meta.env.BASE_URL}assets/ink-raven-modern-city.png`
const homeVideo = (import.meta.env.VITE_HOME_VIDEO_URL as string | undefined) || `${import.meta.env.BASE_URL}assets/cover-background.mp4`

function getPage(): Page {
  const hash = location.hash.replace('#', '')
  return hash === 'rules' || hash === 'notebook' ? hash : 'cover'
}

function App() {
  const [page, setPage] = useState<Page>(getPage)
  const notebook = useNotebook()
  const [videoFailed, setVideoFailed] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const mainRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const onHashChange = () => {
      setPage(getPage())
      window.scrollTo({ top: 0, behavior: 'instant' })
      mainRef.current?.focus({ preventScroll: true })
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  useEffect(() => {
    if (!videoRef.current) return
    if (page === 'cover') void videoRef.current.play().catch(() => setVideoFailed(true))
    else videoRef.current.pause()
  }, [page])

  const navigate = (next: Page) => { location.hash = next }

  const nav = [
    { page: 'cover' as const, label: '封面', icon: Moon },
    { page: 'rules' as const, label: '规则', icon: BookOpen },
    { page: 'notebook' as const, label: '笔记', icon: Feather },
  ]

  return (
    <div className={`app app--${page}`}>
      <button className="skip-link" onClick={() => { mainRef.current?.focus(); mainRef.current?.scrollIntoView() }}>跳到内容</button>
      <div className="scene" aria-hidden="true">
        <img src={background} alt="" />
        {page === 'cover' && !videoFailed && <video ref={videoRef} src={homeVideo} autoPlay muted loop playsInline poster={background} onError={() => setVideoFailed(true)} />}
      </div>
      <div className="grain" aria-hidden="true" />
      <header className="header">
        <button className="brand" onClick={() => navigate('cover')} aria-label="死亡笔记，返回封面">
          <span className="brand-symbol"><Feather size={22} strokeWidth={1.4} /></span>
          <span className="brand-text">死亡笔记<span>DEATH NOTE</span></span>
        </button>
        <nav className="navigation" aria-label="主要导航">
          {nav.map(item => <button key={item.page} aria-current={page === item.page ? 'page' : undefined} onClick={() => navigate(item.page)}><item.icon size={15} strokeWidth={1.5} /><span>{item.label}</span></button>)}
        </nav>
        <span className="header-note"><span className="status-dot" />夜还很长，写下你的故事。</span>
      </header>
      <main id="main-content" tabIndex={-1} ref={mainRef}>
        {page === 'cover' && <Cover key="cover" navigate={navigate} savedPages={notebook.notes.filter(n => n.title.trim() || n.content.trim()).length} />}
        {page === 'rules' && <Rules key="rules" navigate={navigate} />}
        {page === 'notebook' && <Notebook key="notebook" notebook={notebook} />}
      </main>
      <footer className="footer">
        <span><span className="footer-index">{page === 'cover' ? '01' : page === 'rules' ? '02' : '03'}</span><span className="footer-line" />{page === 'cover' ? 'THE COVER' : page === 'rules' ? 'THE RULES' : 'YOUR WORDS'}</span>
        <span className="footer-whisper">日常会消逝，文字会留下。</span>
        <span className="footer-local"><LockKeyhole size={11} />笔记仅保存在当前浏览器</span>
      </footer>
    </div>
  )
}

function Cover({ navigate, savedPages }: { navigate: (page: Page) => void; savedPages: number }) {
  return (
    <section className="cover-page page-enter">
      <div className="cover-copy">
        <div className="eyebrow"><span />A NOTEBOOK AFTER DARK</div>
        <h1>有些话，<br />只适合<span className="italic-title">写下来。</span></h1>
        <p className="cover-description">夜色替你保守秘密。<br />在死亡笔记里，记下每一个普通的今天。</p>
        <button className="primary-button" onClick={() => navigate('notebook')}>翻开笔记<ArrowRight size={17} /></button>
        <button className="text-button" onClick={() => navigate('rules')}>在书写之前，读一读规则<ArrowUpRight size={14} /></button>
        <div className="cover-note"><span className="little-star">✦</span><p>“名字写下去很容易。<br /><span>你真的想好了吗？”</span></p><span className="quote-author">— 墨鸦</span></div>
      </div>
      <div className="book-stage">
        <div className="book-orbit" aria-hidden="true" />
        <button className="death-book" onClick={() => navigate('notebook')} aria-label="打开死亡笔记，开始写字">
          <span className="book-spine" />
          <span className="book-cover">
            <span className="book-corner corner-tl" /><span className="book-corner corner-tr" /><span className="book-corner corner-bl" /><span className="book-corner corner-br" />
            <span className="book-edition">A PRIVATE COLLECTION OF DAYS</span>
            <span className="book-name">DEATH<br />NOTE</span>
            <span className="book-divider" />
            <span className="book-chinese">死 亡 笔 记</span>
            <span className="book-seal"><Feather size={28} strokeWidth={1} /><span>MM</span></span>
            <span className="book-bottom">THIS NOTEBOOK BELONGS TO YOU</span>
          </span>
          <span className="book-pages" />
          <span className="book-ribbon" />
        </button>
        <div className="book-caption"><span>一页，一天，一个你。</span><span>{String(savedPages).padStart(2, '0')} 页已留下</span></div>
      </div>
      <div className="cover-bottom"><span>把喧嚣留在外面。</span><button onClick={() => navigate('notebook')} aria-label="进入笔记页"><ArrowDown size={18} /></button><span>{today().replaceAll('-', '.')} · AFTER MIDNIGHT</span></div>
    </section>
  )
}

function Rules({ navigate }: { navigate: (page: Page) => void }) {
  const [filter, setFilter] = useState<string>('全部')
  const [query, setQuery] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)
  const visible = rules.filter(rule => (filter === '全部' || filter === rule.category) && `${rule.title}${rule.text}${rule.tag}`.toLowerCase().includes(query.trim().toLowerCase()))

  return (
    <section className="rules-page page-enter">
      <div className="section-heading">
        <div><div className="eyebrow"><span />HOW TO USE IT</div><h1>书写之前，<em>先读规则。</em></h1><p>每一本笔记都有它的边界。这里收藏《死亡笔记》的基础设定。</p></div>
        <span className="heading-number">II<span>THE RULES</span></span>
      </div>
      <div className="rules-toolbar">
        <div className="rule-filters" aria-label="规则分类">{ruleFilters.map(item => <button key={item} className={filter === item ? 'active' : ''} aria-pressed={filter === item} onClick={() => setFilter(item)}>{item}</button>)}</div>
        <label className="rule-search"><Search size={15} /><input aria-label="搜索规则" placeholder="寻找一条规则…" value={query} onChange={e => setQuery(e.target.value)} />{query && <button aria-label="清除搜索" onClick={() => setQuery('')}><X size={13} /></button>}</label>
      </div>
      <div className="rule-grid">
        {visible.map(rule => <article className={`rule-card ${expanded === rule.number ? 'expanded' : ''}`} key={rule.number}>
          <span className="rule-number">{rule.number}</span>
          <div className="rule-body"><div className="rule-meta"><span>{rule.category}</span><span>{rule.tag}</span></div><h2>{rule.title}</h2><p>{rule.text}</p>
            <button className="rule-detail-button" onClick={() => setExpanded(expanded === rule.number ? null : rule.number)} aria-expanded={expanded === rule.number} aria-controls={`rule-detail-${rule.number}`}>{expanded === rule.number ? '收起注释' : '阅读注释'}<ChevronDown size={13} /></button>
            {expanded === rule.number && <p id={`rule-detail-${rule.number}`} className="rule-detail">{rule.detail}</p>}
          </div>
        </article>)}
        {!visible.length && <div className="no-results"><Search size={24} /><h2>这一页还没有答案。</h2><p>换一个关键词，或试试其他分类。</p><button className="text-button" onClick={() => { setFilter('全部'); setQuery('') }}>查看全部规则<ArrowRight size={14} /></button></div>}
      </div>
      <div className="rules-bottom"><p><BookOpen size={15} /><span>原作设定的中文概述，非完整规则原文。<a href="https://deathnote.fandom.com/wiki/Rules_of_the_Death_Note" target="_blank" rel="noreferrer">查看规则索引<ArrowUpRight size={12} /></a></span></p><button className="outline-button" onClick={() => navigate('notebook')}>我读完了，开始写<ArrowRight size={15} /></button></div>
    </section>
  )
}

function Notebook({ notebook }: { notebook: NotebookState }) {
  const { notes, activeNote, activeId, setActiveId, saveState, error, updateNote, newNote, deleteNote, exportNote, saveNow } = notebook
  const [deleteOpen, setDeleteOpen] = useState(false)
  const dialogRef = useRef<HTMLDialogElement>(null)
  const contentRef = useRef<HTMLTextAreaElement>(null)
  const count = Array.from(activeNote.content.replace(/\s/g, '')).length
  const writtenPages = notes.filter(n => n.title.trim() || n.content.trim()).length

  useLayoutEffect(() => {
    const resizeEditor = () => {
      const editor = contentRef.current
      if (!editor) return
      editor.style.height = 'auto'
      editor.style.height = `${editor.scrollHeight}px`
    }
    resizeEditor()
    window.addEventListener('resize', resizeEditor)
    return () => window.removeEventListener('resize', resizeEditor)
  }, [activeNote.id, activeNote.content])

  useEffect(() => {
    const shortcut = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') { event.preventDefault(); saveNow() }
    }
    window.addEventListener('keydown', shortcut)
    return () => window.removeEventListener('keydown', shortcut)
  }, [saveNow])

  useEffect(() => {
    if (deleteOpen) dialogRef.current?.showModal()
    else dialogRef.current?.close()
  }, [deleteOpen])

  return (
    <section className="notebook-page page-enter">
      <div className="notebook-heading"><div><div className="eyebrow"><span />YOUR WORDS, YOUR WORLD</div><h1>把今天，<em>留在这一页。</em></h1></div><span className="notebook-today"><Moon size={15} />{formatDate(today())}</span></div>
      {error && <div className="storage-error" role="alert">{error}<button onClick={exportNote}>导出当前页<Download size={14} /></button></div>}
      <div className="notebook-shell">
        <aside className="note-sidebar" aria-label="笔记列表">
          <div className="sidebar-heading"><span>我的书页<small>{notes.length}</small></span><button onClick={newNote} aria-label="新建一页" title="新建一页"><Plus size={18} /></button></div>
          <button className="new-note-button" onClick={newNote}><Plus size={15} />写新的一页</button>
          <div className="note-list">{notes.map(note => <button key={note.id} className={`note-list-item ${note.id === activeId ? 'selected' : ''}`} onClick={() => setActiveId(note.id)} aria-current={note.id === activeId ? 'true' : undefined}>
            <span className="note-date">{note.date.replaceAll('-', '.')}<ChevronRight size={12} /></span><span className="note-title">{note.title.trim() || '无题之页'}</span><span className="note-excerpt">{note.content.trim() || '故事还没开始，书页在等你。'}</span>
          </button>)}</div>
          <div className="sidebar-whisper"><Feather size={22} strokeWidth={1} /><p>不必写得漂亮。<br />写得像你，就好。</p><span>— 墨鸦</span></div>
        </aside>
        <div className="editor-panel">
          <div className="editor-toolbar"><div className={`save-indicator ${saveState}`} role="status">{saveState === 'saved' ? <CheckCheck size={14} /> : saveState === 'error' ? <X size={14} /> : <span className="saving-dot" />}<span>{saveState === 'saved' ? '已保存到此设备' : saveState === 'error' ? '暂未保存' : '正在保存…'}</span></div><div className="editor-actions"><button onClick={exportNote} title="导出文本" aria-label="导出当前笔记"><Download size={16} /><span>导出</span></button><span className="toolbar-separator" /><button onClick={() => setDeleteOpen(true)} title="删除当前页" aria-label="删除当前页"><Trash2 size={15} /></button></div></div>
          <div className="paper">
            <span className="paper-ribbon" aria-hidden="true" />
            <div className="paper-meta"><span>{activeNote.date.replaceAll('-', ' / ')}</span><span>PAGE {String(notes.findIndex(n => n.id === activeNote.id) + 1).padStart(2, '0')}</span></div>
            <input className="note-title-input" aria-label="笔记标题" placeholder="给今天一个名字…" value={activeNote.title} onChange={e => updateNote({ title: e.target.value })} maxLength={120} />
            <span className="paper-title-line" />
            <textarea ref={contentRef} className="note-content-input" aria-label="笔记正文" placeholder={'今天发生了什么？\n\n也许是一场雨，一个梦，或一句没有说出口的话。\n把想说的话，留在这张书页上。'} value={activeNote.content} onChange={e => updateNote({ content: e.target.value })} spellCheck={false} />
            <div className="paper-footer"><span><Feather size={13} />死亡笔记，收藏你的文字。</span><span>{count} 字</span></div>
          </div>
        </div>
      </div>
      <div className="notebook-bottom"><span><LockKeyhole size={12} />自动保存于当前浏览器，清除浏览器数据会删除笔记。重要内容记得导出。</span><span>{writtenPages} 页故事 · {notes.length} 张书页</span></div>
      <dialog ref={dialogRef} className="delete-dialog" onCancel={() => setDeleteOpen(false)} aria-labelledby="delete-title">
        <div className="dialog-icon"><FileText size={24} strokeWidth={1.2} /></div><h2 id="delete-title">要撕下这一页吗？</h2><p>“{activeNote.title.trim() || '无题之页'}”将被删除。<br />如果还想留住它，请先导出。</p><div className="dialog-buttons"><button className="outline-button" onClick={() => setDeleteOpen(false)}>留下这一页</button><button className="delete-confirm" onClick={() => { deleteNote(); setDeleteOpen(false) }}><Check size={15} />确认删除</button></div>
      </dialog>
    </section>
  )
}

export default App
