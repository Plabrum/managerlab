import { render } from '@react-email/components';
import * as fs from 'fs';
import * as path from 'path';

const TEMPLATES_DIR = path.join(__dirname, '../templates');
const OUTPUT_DIR = path.join(__dirname, '../../templates/emails-react');

// Mapping of template files to their Jinja2 variable names
const TEMPLATE_VARIABLES: Record<string, Record<string, string>> = {
  'MagicLink': {
    'magic_link_url': '{{ magic_link_url }}',
    'expiration_minutes': '{{ expiration_minutes }}',
  },
  'TeamInvitation': {
    'invitation_url': '{{ invitation_url }}',
    'team_name': '{{ team_name }}',
    'inviter_name': '{{ inviter_name }}',
    'expiration_hours': '{{ expiration_hours }}',
  },
};

async function buildTemplate(templateName: string) {
  try {
    console.log(`Building ${templateName}...`);

    // Import the template
    const templatePath = path.join(TEMPLATES_DIR, `${templateName}.tsx`);
    const template = await import(templatePath);
    const Component = template.default;

    if (!Component) {
      throw new Error(`No default export found in ${templateName}.tsx`);
    }

    // Get Jinja2 variables for this template
    const variables = TEMPLATE_VARIABLES[templateName] || {};

    // Pass Jinja2 template variables directly as props
    // React Email will render them as-is into the HTML
    const props: Record<string, any> = {};
    for (const [key, jinjaVar] of Object.entries(variables)) {
      props[key] = jinjaVar;
    }

    // Render the component to HTML with Jinja2 variables
    const html = await render(Component(props), {
      pretty: true,
    });

    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Write to output file as .html.jinja2
    // Convert PascalCase to snake_case: MagicLink -> magic_link
    const fileName = templateName
      .replace(/([A-Z])/g, '_$1')
      .toLowerCase()
      .replace(/^_/, '');
    const outputPath = path.join(OUTPUT_DIR, `${fileName}.html.jinja2`);
    fs.writeFileSync(outputPath, html, 'utf-8');

    console.log(`✓ Built ${templateName} -> ${outputPath}`);
  } catch (error) {
    console.error(`✗ Error building ${templateName}:`, error);
    throw error;
  }
}

async function buildAll() {
  console.log('Building all email templates...\n');

  try {
    // Find all .tsx files in templates directory
    if (!fs.existsSync(TEMPLATES_DIR)) {
      console.error(`Templates directory not found: ${TEMPLATES_DIR}`);
      process.exit(1);
    }

    const files = fs.readdirSync(TEMPLATES_DIR);
    const templateFiles = files.filter(
      (file) => file.endsWith('.tsx') && !file.startsWith('_')
    );

    if (templateFiles.length === 0) {
      console.log('No template files found.');
      return;
    }

    // Build each template
    for (const file of templateFiles) {
      const templateName = file.replace('.tsx', '');
      await buildTemplate(templateName);
    }

    console.log(`\n✓ Successfully built ${templateFiles.length} template(s)`);
  } catch (error) {
    console.error('\n✗ Build failed:', error);
    process.exit(1);
  }
}

// Run the build
buildAll();
