# PDF Conversion Guide for Mermaid Architecture Diagrams

This guide explains how to convert your `architecture.md` file (with Mermaid diagrams) into a shareable PDF.

## 🚀 Quick Start (Windows)

1. **Double-click** `convert_architecture.bat` - it will:
   - Check for Node.js (install if needed)
   - Install mermaid-cli automatically
   - Convert your architecture.md to PDF
   - Open the result

## 🛠️ Manual Methods

### Method 1: Mermaid CLI (Best Quality)
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convert to PDF
mmdc -i diagrams/architecture.md -o diagrams/architecture.pdf -t default

# With dark theme
mmdc -i diagrams/architecture.md -o diagrams/architecture.pdf -t dark
```

### Method 2: Python Script (Multiple Options)
```bash
# Using the provided script
python convert_to_pdf.py --input diagrams/architecture.md --method mermaid-cli

# Try different methods if one fails
python convert_to_pdf.py --input diagrams/architecture.md --method pandoc
python convert_to_pdf.py --input diagrams/architecture.md --method manual
```

### Method 3: VS Code (Manual but Reliable)
1. Install **Markdown Preview Mermaid Support** extension
2. Open `architecture.md`
3. Press `Ctrl+Shift+V` for preview
4. Right-click → Print → Save as PDF

### Method 4: Online Tools
1. Copy your Mermaid code to [Mermaid Live Editor](https://mermaid.live/)
2. Export diagrams as PNG/SVG
3. Combine with text in Word/Google Docs
4. Export as PDF

## 📋 Prerequisites

### For Automated Methods:
- **Node.js** (for mermaid-cli): https://nodejs.org/
- **Python 3.8+** (for the conversion script)

### Optional Tools:
- **Pandoc**: https://pandoc.org/installing.html
- **VS Code** with Mermaid extension

## 🎨 Customization Options

### Mermaid Themes:
- `default` - Standard theme
- `dark` - Dark background
- `forest` - Green theme
- `neutral` - Minimal styling

### Example with Custom Theme:
```bash
mmdc -i diagrams/architecture.md -o diagrams/architecture_dark.pdf -t dark
```

## 🔧 Troubleshooting

### Common Issues:

**"mmdc command not found"**
```bash
npm install -g @mermaid-js/mermaid-cli
```

**"Permission denied" on Windows**
- Run Command Prompt as Administrator
- Or use PowerShell: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Diagrams not rendering**
- Check Mermaid syntax in [Mermaid Live Editor](https://mermaid.live/)
- Try different conversion methods
- Use VS Code preview method as fallback

**Large file size**
- Use `--scale 0.8` flag with mmdc
- Convert to PNG first, then combine in document

## 📤 Sharing Options

Once you have the PDF:

1. **Email attachment** - Direct sharing
2. **Cloud storage** - Google Drive, Dropbox, OneDrive
3. **GitHub releases** - Attach to project releases
4. **Project documentation** - Include in docs folder
5. **Presentation** - Import into PowerPoint/Google Slides

## 🎯 Best Practices

1. **Test locally first** - Use VS Code preview to verify diagrams
2. **Version control** - Keep both .md and .pdf in git
3. **Multiple formats** - Generate both light and dark theme PDFs
4. **Backup method** - Always have VS Code print-to-PDF as fallback
5. **File naming** - Use descriptive names like `architecture_v1.2_dark.pdf`

## 📁 Output Files

After conversion, you'll have:
```
backend/docs/diagrams/
├── architecture.md          # Source markdown
├── architecture.pdf         # Converted PDF
├── architecture_dark.pdf    # Dark theme version (optional)
└── architecture_enhanced.drawio  # DrawIO version
```

## 🆘 Need Help?

If automated methods fail:
1. Run: `python convert_to_pdf.py --method manual`
2. Use VS Code print-to-PDF method
3. Try online Mermaid tools
4. Check the troubleshooting section above