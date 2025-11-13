import express from 'express';
import cors from 'cors';
import { render } from '@react-email/components';
import * as path from 'path';
import * as fs from 'fs';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Serve the viewer HTML page
app.get('/', (req, res) => {
  const viewerPath = path.join(__dirname, '../viewer/index.html');
  res.sendFile(viewerPath);
});

// API endpoint to render email templates
app.post('/api/render', async (req, res) => {
  try {
    const { template, data } = req.body;

    if (!template) {
      return res.status(400).json({ error: 'Template name is required' });
    }

    // Import the template dynamically
    const templatePath = path.join(__dirname, '../templates', `${template}.tsx`);

    if (!fs.existsSync(templatePath)) {
      return res.status(404).json({ error: `Template '${template}' not found` });
    }

    // Dynamic import doesn't work well with tsx in this context,
    // so we'll read the compiled HTML from the output directory
    // Convert PascalCase to snake_case: MagicLink -> magic_link
    const fileName = template
      .replace(/([A-Z])/g, '_$1')
      .toLowerCase()
      .replace(/^_/, '');
    const compiledPath = path.join(
      __dirname,
      '../../templates/emails-react',
      `${fileName}.html`
    );

    if (!fs.existsSync(compiledPath)) {
      return res.status(404).json({
        error: `Compiled template not found. Run 'npm run build' first.`
      });
    }

    // Read the compiled HTML
    let html = fs.readFileSync(compiledPath, 'utf-8');

    // Replace Jinja2 variables with actual values
    for (const [key, value] of Object.entries(data || {})) {
      const jinjaVar = `{{ ${key} }}`;
      html = html.replace(new RegExp(jinjaVar.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), String(value));
    }

    res.setHeader('Content-Type', 'text/html');
    res.send(html);
  } catch (error: any) {
    console.error('Render error:', error);
    res.status(500).json({
      error: 'Failed to render template',
      message: error.message
    });
  }
});

// List available templates
app.get('/api/templates', (req, res) => {
  const templatesDir = path.join(__dirname, '../templates');
  const files = fs.readdirSync(templatesDir);
  const templates = files
    .filter(file => file.endsWith('.tsx') && !file.startsWith('_'))
    .map(file => file.replace('.tsx', ''));

  res.json({ templates });
});

app.listen(PORT, () => {
  console.log(`📧 Email Template Viewer running at:`);
  console.log(`   http://localhost:${PORT}`);
  console.log(``);
  console.log(`✨ Edit templates in backend/emails/templates/`);
  console.log(`🔄 Changes will auto-compile and reload`);
});
