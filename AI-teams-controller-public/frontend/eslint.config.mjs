import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";

/** @type {import('eslint').Linter.Config[]} */
const eslintConfig = [
  {
    // Apply to all TypeScript and JavaScript files
    files: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    rules: {
      // Block imports from experiments/ folder
      // Components should be migrated to official location, not imported from experiments/
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/experiments/*", "**/experiments/**"],
              message: "Do not import from experiments/. Use as reference only, then rewrite in official location.",
            },
          ],
        },
      ],
    },
  },
  {
    // Ignore node_modules and build directories
    ignores: ["node_modules/**", ".next/**", "out/**"],
  },
];

export default eslintConfig;
