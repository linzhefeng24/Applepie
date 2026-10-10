import { readFile, writeFile, mkdir, readdir, cp } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = fileURLToPath(new URL('../', import.meta.url))
const dist = path.join(root, 'dist')
const output = path.join(root, 'offline')
await mkdir(output, { recursive: true })
const assets = await readdir(path.join(dist, 'assets'))
const js = await readFile(path.join(dist, 'assets', assets.find(name => /^index-.*\.js$/.test(name))), 'utf8')
let css = await readFile(path.join(dist, 'assets', assets.find(name => /^index-.*\.css$/.test(name))), 'utf8')
for (const name of assets.filter(name => /\.woff2?$/.test(name))) {
  const data = await readFile(path.join(dist, 'assets', name))
  css = css.replaceAll(`./${name}`, `data:font/${name.endsWith('woff2') ? 'woff2' : 'woff'};base64,${data.toString('base64')}`)
}
let html = await readFile(path.join(dist, 'index.html'), 'utf8')
html = html.replace(/<script[^>]*src="[^"]+"[^>]*><\/script>/, () => `<script type="module">${js.replaceAll('</script', '<\\/script')}</script>`)
html = html.replace(/<link[^>]*rel="stylesheet"[^>]*>/, () => `<style>${css}</style>`)
await writeFile(path.join(output, '打开笔记本.html'), html)
await mkdir(path.join(output, 'assets'), { recursive: true })
for (const name of ['cover-background.mp4', 'ink-raven-modern-city.png']) {
  await cp(path.join(dist, 'assets', name), path.join(output, 'assets', name))
}
await cp(path.join(dist, 'favicon.svg'), path.join(output, 'favicon.svg'))
await cp(path.join(dist, 'licenses'), path.join(output, 'licenses'), { recursive: true })
await writeFile(path.join(output, '使用说明.txt'), '先将压缩包全部解压，然后双击“打开笔记本.html”。建议使用 Chrome 或 Edge。无需安装 Node.js，无需输入命令，也无需联网。\r\n请保留 assets 文件夹与 HTML 文件的相对位置。\r\n笔记保存在当前浏览器中，请使用同一个浏览器，并保持文件位置不变；重要内容请导出备份。\r\n')
console.log(`Offline application exported to ${output}`)
