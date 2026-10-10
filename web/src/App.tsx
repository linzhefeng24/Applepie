import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowRight, ArrowUpRight, BookOpen, ChevronDown, Download, Feather, LockKeyhole, Moon, Search, X } from 'lucide-react'
import { today, useNotebook } from './notebook'
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
        <span className="header-note"><span className="status-dot" />落笔之前，先读规则。</span>
      </header>
      <main id="main-content" tabIndex={-1} ref={mainRef}>
        {page === 'cover' && <Cover key="cover" navigate={navigate} savedPages={notebook.notes.filter(n => n.title.trim() || n.content.trim()).length} />}
        {page === 'rules' && <Rules key="rules" navigate={navigate} />}
        {page === 'notebook' && <Notebook key="notebook" notebook={notebook} />}
      </main>
      <footer className="footer">
        <span><span className="footer-index">{page === 'cover' ? '01' : page === 'rules' ? '02' : '03'}</span><span className="footer-line" />{page === 'cover' ? 'THE COVER' : page === 'rules' ? 'THE RULES' : 'YOUR WORDS'}</span>
        <span className="footer-whisper">名字、规则，以及选择的代价。</span>
        <span className="footer-local"><LockKeyhole size={11} />笔记仅保存在当前浏览器</span>
      </footer>
    </div>
  )
}

function Cover({ navigate, savedPages }: { navigate: (page: Page) => void; savedPages: number }) {
  return (
    <section className="cover-page page-enter">
      <div className="cover-copy">
        <div className="eyebrow"><span />THE PRICE OF A NAME</div>
        <h1>一个名字，<br /><span className="italic-title">改写命运。</span></h1>
        <p className="cover-description">当一本笔记拥有改写命运的力量，<br />谁有资格决定正义？</p>
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
            <span className="book-edition">THE HUMAN WHOSE NAME IS WRITTEN</span>
            <span className="book-name">DEATH<br />NOTE</span>
            <span className="book-divider" />
            <span className="book-chinese">死 亡 笔 记</span>
            <span className="book-seal"><Feather size={28} strokeWidth={1} /><span>DN</span></span>
            <span className="book-bottom">EVERY CHOICE HAS A PRICE</span>
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
  const { notes, activeNote, activeId, setActiveId, saveState, error, updateNote, exportNote, saveNow } = notebook
  const contentRef = useRef<HTMLTextAreaElement>(null)
  const pageIndex = notes.findIndex(note => note.id === activeId)

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

  return (
    <section className="name-page page-enter" aria-label="死亡笔记书页">
      {error && <div className="storage-error" role="alert">{error}<button onClick={exportNote}>导出内容<Download size={14} /></button></div>}
      <div className="name-paper">
        <p className="name-rule" aria-hidden="true">The human whose name is written in this note shall die.</p>
        <textarea ref={contentRef} className="names-input" aria-label="写下名字" value={activeNote.content} onChange={event => updateNote({ content: event.target.value })} spellCheck={false} />
      </div>
      <div className="name-page-foot">
        {notes.length > 1 && <nav aria-label="已有书页"><button disabled={pageIndex <= 0} onClick={() => setActiveId(notes[pageIndex - 1].id)}>上一页</button><button disabled={pageIndex >= notes.length - 1} onClick={() => setActiveId(notes[pageIndex + 1].id)}>下一页</button></nav>}
        <span role="status">{saveState === 'saved' ? '已保存' : saveState === 'error' ? '暂未保存' : '保存中…'}</span>
      </div>
    </section>
  )
}

export default App
