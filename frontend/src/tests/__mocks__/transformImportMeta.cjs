const { transformSync } = require('@swc/core');

module.exports = {
  process(src, filename) {
    // Don’t touch node_modules
    if (filename.includes('node_modules')) return src;

    // Replace all occurrences of import.meta.env
    const replaced = src.replace(/\bimport\.meta\.env\b/g, 'process.env');

    const { code } = transformSync(replaced, {
      filename,
      sourceMaps: 'inline',
      jsc: {
        target: 'es2022',
        parser: { syntax: 'ecmascript', jsx: /\.jsx?$/.test(filename) },
        transform: { react: { runtime: 'automatic' } }
      },
      module: { type: 'commonjs' }
    });

    return { code };
  },
};