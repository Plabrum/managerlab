import { render } from '@react-email/components';
import * as fs from 'fs';
import * as path from 'path';
import * as ts from 'typescript';

const TEMPLATES_DIR = path.join(__dirname, '../templates');
const OUTPUT_DIR = path.join(__dirname, '../../templates/emails-react');

/**
 * Extract prop names from a TypeScript interface in a .tsx file
 */
function extractPropsFromTemplate(templatePath: string): string[] {
  const sourceCode = fs.readFileSync(templatePath, 'utf-8');
  const sourceFile = ts.createSourceFile(
    templatePath,
    sourceCode,
    ts.ScriptTarget.Latest,
    true
  );

  const propNames: string[] = [];

  function visit(node: ts.Node) {
    // Look for interface declarations ending with "Props"
    if (ts.isInterfaceDeclaration(node) && node.name.text.endsWith('Props')) {
      // Extract property names from the interface
      node.members.forEach((member) => {
        if (ts.isPropertySignature(member) && ts.isIdentifier(member.name)) {
          propNames.push(member.name.text);
        }
      });
    }
    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  return propNames;
}

/**
 * Generate Jinja2 variables for all props in a template
 */
function generateJinjaProps(templatePath: string): Record<string, string> {
  const propNames = extractPropsFromTemplate(templatePath);
  const jinjaProps: Record<string, string> = {};

  for (const propName of propNames) {
    // Convert prop name to Jinja2 variable: prop_name -> {{ prop_name }}
    jinjaProps[propName] = `{{ ${propName} }}`;
  }

  return jinjaProps;
}

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

    // Auto-generate Jinja2 variables from the template's props interface
    const props = generateJinjaProps(templatePath);
    console.log(`  Props: ${Object.keys(props).join(', ') || '(none)'}`);


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
      (file) => file.endsWith('.tsx') && !file.startsWith('_') && file !== 'components.tsx'
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
