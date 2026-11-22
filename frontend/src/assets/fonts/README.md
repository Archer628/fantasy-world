# 字体文件目录

此目录用于存放自定义字体文件。

## 推荐字体

### 显示字体 (Display Font)
- **Cinzel** - 用于标题，具有古典华丽的风格
- **Noto Serif SC** - 中文衬线字体

### 正文字体 (Body Font)
- **Inter** - 现代无衬线字体
- **Noto Sans SC** - 中文无衬线字体

## 使用方式

将字体文件放入此目录后，在 CSS 中通过 @font-face 引入：

```css
@font-face {
  font-family: 'Cinzel';
  src: url('@/assets/fonts/Cinzel-Regular.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}
```

或通过 CDN 引入（推荐）：
```html
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
```
