import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import importPlugin from 'eslint-plugin-import';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'build/**',
      '.next/**',
      'src/openapi/**',
    ],
  },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      'jsx-a11y': jsxA11y,
      import: importPlugin,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      ...jsxA11y.flatConfigs.recommended.rules,
      ...importPlugin.flatConfigs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        {
          allowConstantExport: true,
          allowExportNames: [
            'useAuth',
            'useSidebar',
            'badgeVariants',
            'buttonVariants',
            'toggleVariants',
            'SIDEBAR_COOKIE_NAME',
            'queryClient',
            'RequiredMessage',
            'FieldError',
            'createTypedForm',
          ],
        },
      ],
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-empty-pattern': 'off',
      // Accessibility - adjusted for shadcn/ui and Radix UI
      'jsx-a11y/label-has-associated-control': [
        'warn',
        {
          labelComponents: ['Label'],
          labelAttributes: ['label'],
          controlComponents: ['Input', 'Select', 'Textarea'],
          depth: 3,
        },
      ],
      'jsx-a11y/no-autofocus': 'off', // Allow autoFocus in modals/forms for UX
      // Import plugin settings
      'import/order': [
        'error', // Changed from 'warn' to 'error' for strict enforcement
        {
          groups: [
            'builtin', // Node built-ins (fs, path, etc.)
            'external', // npm packages
            'internal', // Internal aliases (@/)
            ['parent', 'sibling'], // Relative imports
            'index',
            'type', // Type imports
          ],
          pathGroups: [
            {
              pattern: 'react',
              group: 'external',
              position: 'before',
            },
            {
              pattern: '@tanstack/**',
              group: 'external',
              position: 'before',
            },
            {
              pattern: '@/**',
              group: 'internal',
              position: 'before',
            },
          ],
          pathGroupsExcludedImportTypes: ['react', 'type'],
          'newlines-between': 'never',
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
          distinctGroup: false,
        },
      ],
      'import/no-duplicates': 'error', // Prevent duplicate imports
      'import/first': 'error', // All imports must be at top of file
      'import/newline-after-import': 'error', // Blank line after imports
      'import/no-unresolved': 'off', // TypeScript handles this
      'import/named': 'off', // TypeScript handles this
    },
  },
  // Prettier must be last to override formatting rules
  prettier
);
